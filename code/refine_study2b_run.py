#!/usr/bin/env python3
"""Protocol 11 / Study 2b — refinement pass with WITHIN-FAMILY refiners (D42).

Each family's C-T-P answers are refined by that family's OWN cheap-sibling model
(the same model that generated the team answers), keeping the refined pipeline
model-homogeneous — the research question is the TEAM effect, so no external
refiner (Study 2 used deepseek-chat; that design difference is disclosed).
The frozen Protocol 09 sec 4 add-only prompt is reused verbatim; the prompt is
the ONLY controlled variable shared with Study 2.

Refiners (locked, config/model_registry.json, D43):
  gpt    -> gpt-5.6-luna                (OpenAI, temp 1: API-enforced)
  gemini -> gemini-3.1-flash-lite       (OpenAI-compatible, temp 0)
  kimi   -> kimi-k2.6                   (OpenAI-compatible, temp 1: API-enforced)
  claude -> claude-haiku-4-5-20251001   (Anthropic Messages API, temp 0)
  qwen   -> qwen3.7-plus-2026-05-26     (OpenAI-compatible, temp 0)

Scheduling (Protocol 11 sec 8): qwen calls only UTC 14:00-00:00 (off-peak).

Resumable JSONL; emits a judge_v2-compatible store (runIds "R<ctp_runId>").
Outputs: --log (JSONL), --store (judge store JSON)
"""
import concurrent.futures
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import judge_v2 as jv  # noqa: E402  (reuse KEYS/.env resolution + problem bank)

REFINERS = {
    "gpt": {"model": "gpt-5.6-luna", "endpoint": "https://api.openai.com/v1",
            "env_key": "OPENAI_API_KEY", "temperature": 1, "api_format": "openai",
            "omit_temperature": True, "max_tokens_field": "max_completion_tokens",
            "reasoning_effort": "low"},
    "gemini": {"model": "gemini-3.1-flash-lite",
               "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai",
               "env_key": "GEMINI_API_KEY", "temperature": 0, "api_format": "openai"},
    # DEVIATION 2026-08-22 (MANIFEST Entry 52): Moonshot direct account suspended
    # (insufficient balance); Together.ai host of kimi-k2.6 is non-serverless
    # (requires a paid dedicated endpoint), so the kimi W-arm refiner is routed
    # to moonshotai/Kimi-K3 on Together serverless — SAME family (construct for
    # the W arm is family identity), DIFFERENT version than locked kimi-k2.6,
    # and reasoning disabled (reasoning_effort=none, verified serverless) to
    # match the non-reasoning editing behavior of the other cheap refiners.
    # Fully disclosed as a protocol deviation in MANIFEST Entry 52.
    "kimi": {"model": "moonshotai/Kimi-K3", "endpoint": "https://api.together.ai/v1",
             "env_key": "TOGETHER_API_KEY", "temperature": 1, "api_format": "openai",
             "reasoning_effort": "none"},
    "claude": {"model": "claude-haiku-4-5-20251001",
               "endpoint": "https://api.anthropic.com/v1",
               "env_key": "ANTHROPIC_API_KEY", "temperature": 0,
               "api_format": "anthropic"},
    "qwen": {"model": "qwen3.7-plus-2026-05-26",
             "endpoint": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
             "env_key": "ALIBABA_API_KEY", "temperature": 0, "api_format": "openai"},
}
MAX_TOKENS = 8192
WORKERS = 8
PROMPT_TAG = "protocol11-v1"
REFINER_KEYS = {}  # filled in main() via jv.load_key (env or .env)

# Frozen Protocol 09 sec 4 universal add-only prompt — byte-identical, D39 rule.
PROMPT = """You are a senior business editor. Your task is to strengthen an existing answer to a
business problem. You must follow these rules exactly:

1. ADD ONLY. You may add: concrete implementation steps, operational details,
   measurable metrics and KPIs, a risk table with mitigations, sequencing/timeline,
   and role responsibilities.
2. NEVER REMOVE OR WEAKEN: original creative ideas, metaphors, rhetorical questions,
   cultural framing or local adaptations, the author's stance, tone, or voice.
3. Do not change the core recommendations or their reasoning. Do not make the answer
   more generic or more conservative.
4. Keep the same language as the original answer.
5. Output the COMPLETE improved answer only — no preamble, no critique, no summary of
   your changes.

=== BUSINESS PROBLEM ===
{problem_text}

=== ANSWER TO STRENGTHEN ===
{solution_text}"""


def call(family, prompt):
    cfg = REFINERS[family]
    if cfg["api_format"] == "anthropic":
        return _call_anthropic(cfg, prompt)
    payload = {"model": cfg["model"],
               "messages": [{"role": "user", "content": prompt}]}
    payload[cfg.get("max_tokens_field", "max_tokens")] = MAX_TOKENS
    if cfg.get("reasoning_effort"):
        # reasoning models (gpt-5.6) can burn the whole completion budget on
        # internal reasoning and emit empty content (observed 2026-08-22:
        # finish_reason=length, 8192/8192 reasoning_tokens, content="").
        # Refinement is an editing task -> locked reasoning_effort=minimal.
        payload["reasoning_effort"] = cfg["reasoning_effort"]
    # gpt-5.6 family rejects ANY explicit temperature (default 1 only); sending
    # temp=1 itself returns 400, so omit the field entirely there (locked value
    # remains temp=1 by provider default — D27 precedent, logged in refine log).
    if not cfg.get("omit_temperature"):
        payload["temperature"] = cfg["temperature"]
    req = urllib.request.Request(
        cfg["endpoint"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {REFINER_KEYS[cfg['env_key']]}",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-study2b/1.0"})
    for attempt in range(7):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
            # content only — any reasoning/thinking trace (e.g. kimi) is excluded
            return data["choices"][0]["message"]["content"], data.get("usage", {})
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = " | " + e.read().decode()[:200]
            except Exception:
                pass
            if e.code == 429:  # rate limit: honor Retry-After, else long backoff
                if attempt >= 6:
                    raise RuntimeError(f"HTTP 429 after 7 attempts{body}")
                wait = float(e.headers.get("Retry-After") or 0) or (15 * (attempt + 1))
                time.sleep(min(wait, 120))
                continue
            if attempt < 6 and e.code >= 500:
                time.sleep(2 ** attempt * 2)
                continue
            raise RuntimeError(f"HTTP {e.code}{body}")
        except urllib.error.HTTPError:
            raise
        except Exception:
            if attempt < 6:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError("call(): retry loop exhausted without result")


def _call_anthropic(cfg, prompt):
    """Anthropic Messages API (claude family): distinct wire format, D43."""
    payload = {"model": cfg["model"],
               "messages": [{"role": "user", "content": prompt}],
               "temperature": cfg["temperature"], "max_tokens": MAX_TOKENS}
    req = urllib.request.Request(
        cfg["endpoint"].rstrip("/") + "/messages",
        data=json.dumps(payload).encode(),
        headers={"x-api-key": REFINER_KEYS[cfg["env_key"]],
                 "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-study2b/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
            text = "".join(b.get("text", "") for b in data.get("content", [])
                           if b.get("type") == "text")
            return text, data.get("usage", {})
        except Exception:
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=str(ROOT / "runs/refine_b/sample_pilot.json"))
    ap.add_argument("--log", default=str(ROOT / "runs/logs/refine_b_pilot.jsonl"))
    ap.add_argument("--store", default=str(ROOT / "runs/refine_b/refined_store_pilot.json"))
    ap.add_argument("--workers", type=int, default=WORKERS)
    args = ap.parse_args()
    sample = json.load(open(args.sample))
    pairs = sample["pairs"]
    for fam in {p["family"] for p in pairs}:
        assert fam in REFINERS, f"no locked refiner for family {fam}"
        REFINER_KEYS[REFINERS[fam]["env_key"]] = jv.load_key(REFINERS[fam]["env_key"])
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if log_path.exists():
        for line in open(log_path):
            j = json.loads(line)
            if j.get("refined_text"):
                done.add(j["ctp_runId"])

    tasks = [p for p in pairs if p["ctp_runId"] not in done]
    print(f"refine study2b: {len(pairs)} answers; {len(tasks)} pending, {len(done)} done; "
          f"refiners={ {f: REFINERS[f]['model'] for f in sorted(REFINERS)} } "
          f"(within-family, D42)")

    lock = threading.Lock()
    counter = {"n": len(done)}
    sem = threading.Semaphore(args.workers)

    def run_task(pair, out):
        prompt = (PROMPT.replace("{problem_text}", pair["problem_text"])
                  .replace("{solution_text}", pair["ctp_fulltext"]))
        cfg = REFINERS[pair["family"]]
        with sem:
            try:
                text, usage = call(pair["family"], prompt)
                rec = {"ctp_runId": pair["ctp_runId"], "fsn_runId": pair["fsn_runId"],
                       "family": pair["family"], "problemId": pair["problemId"],
                       "refined_text": text if text and text.strip() else None,
                       "orig_len": len(pair["ctp_fulltext"]),
                       "refined_len": len(text) if text else 0,
                       "usage": usage, "refiner_model": cfg["model"],
                       "refiner_temperature": cfg["temperature"],
                       "prompt": PROMPT_TAG,
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            except Exception as e:  # noqa: BLE001
                rec = {"ctp_runId": pair["ctp_runId"], "fsn_runId": pair["fsn_runId"],
                       "family": pair["family"], "problemId": pair["problemId"],
                       "refiner_model": cfg["model"], "error": str(e)[:300],
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            counter["n"] += 1
            ok = rec.get("refined_text") is not None
            print(f"[{counter['n']}/{len(pairs)}] {rec['family']} "
                  f"({cfg['model']}) ctp={rec['ctp_runId']}: "
                  f"{'OK ' + str(rec.get('refined_len')) + ' chars' if ok else rec.get('error')}")

    with open(log_path, "a") as out:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = [pool.submit(run_task, p, out) for p in tasks]
            for f in concurrent.futures.as_completed(futs):
                f.result()

    # --- build judge_v2-compatible store
    refined = {}
    for line in open(log_path):
        j = json.loads(line)
        if j.get("refined_text"):
            refined[j["ctp_runId"]] = j
    store = {"source": "protocol11-study2b-refiner", "prompt": PROMPT_TAG,
             "refiner_models": {f: REFINERS[f]["model"] for f in REFINERS},
             "runs": [{"runId": f"R{j['ctp_runId']}", "problemId": j["problemId"],
                       "status": "completed", "fulltext": j["refined_text"],
                       "family": j["family"], "base_runId": j["ctp_runId"],
                       "refiner_model": j["refiner_model"]}
                      for _, j in sorted(refined.items())]}
    dst = Path(args.store)
    dst.write_text(json.dumps(store, indent=1, ensure_ascii=False) + "\n")
    n_fail = len(pairs) - len(store["runs"])
    print(f"done -> {log_path}; store with {len(store['runs'])} refined answers -> {dst}; "
          f"failures={n_fail} ({n_fail / len(pairs) * 100:.1f}%)")


if __name__ == "__main__":
    main()
