#!/usr/bin/env python3
"""study3_design_run.py — Protocol 13 runner: pipeline design authorship.

Arms (executor is ALWAYS the family's pinned cheap sibling):
  D-SELF  — cheap sibling designs the pipeline for the problem, then executes it
  D-FRONT — the family's frontier designs the pipeline, cheap sibling executes it

Discipline:
- One fresh design per (arm, family, problem, rep) — design variance is data (D30 probe logic).
- Designer tokens are charged to arm cost (logged per call; D30 precedent).
- Designs validated against the schema; ONE repair retry with the validator error;
  second failure -> design FAILED, task excluded and disclosed (Protocol 13 §2).
- Append-only JSONL ledger; resume by key scan (completed + non-empty only);
  429 Retry-After honored; 5xx backoff; credit exhaustion -> family skipped, others
  continue (Protocol 12 §5.4 policy); qwen design/execute calls only inside the
  UTC 14:00-00:00 discount window (D21) unless --ignore-window (logged).
- Output store is judge_v2-compatible (runs/study3/study3_store.json) — the frozen
  judge panel scores designed-pipeline solutions unchanged.

Usage:
  python3 code/study3_design_run.py --dry-run
  python3 code/study3_design_run.py --pilot     # 4 problems (D32 draw) x 1 rep
  python3 code/study3_design_run.py             # full: 19 problems x 3 reps
  python3 code/study3_design_run.py --families kimi,qwen --reps 1
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_key(env_key):
    # Local copy of judge_v2.load_key — avoids importing judge_v2 here, whose
    # module-level KEYS would demand judge keys (DeepSeek) at generation time.
    for name in (env_key, "TOGETHER_AI_API_KEY" if env_key == "TOGETHER_API_KEY" else None):
        if name and os.environ.get(name):
            return os.environ[name]
    for env_file in (ROOT / ".env", ROOT.parent.parent / ".env"):
        if not env_file.exists():
            continue
        for line in env_file.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip() == env_key and v.strip():
                return v.strip().strip('"').strip("'")
    sys.exit(f"{env_key} not set (env or .env)")

LEDGER = ROOT / "runs" / "logs" / "study3_ledger.jsonl"
EXHAUSTION = ROOT / "runs" / "logs" / "study3_credit_exhaustion.jsonl"
STORE = ROOT / "runs" / "study3" / "study3_store.json"
DESIGNS_DIR = ROOT / "runs" / "study3" / "designs"
MAX_TOKENS = 8192
WORKERS = 24  # raised from 8 (2026-08-29, author request): D34 calibrated high
              # concurrency as non-distorting; 429 backoff already handled.
PROMPT_TAG = "protocol13-v1"
# Study-3 pilot draw (D55 amendment, 2026-08-28): deterministic seeded draw —
# random.Random(20260828).sample of the 19 confirmatory problems (numeric-sorted),
# rejection-resampled until 4 distinct domains per domain_map.json. Result:
PILOT_PROBLEMS = ["Business_Problem_6", "Business_Problem_8",
                  "Business_Problem_9", "Business_Problem_12"]

# Provider configs: [cheap sibling] and [frontier]. Conventions from
# refine_study2b_run.py (D27 temperatures: provider-enforced defaults; gpt
# rejects explicit temperature and uses max_completion_tokens + low reasoning).
MODELS = {
    "gpt": {
        "cheap": {"model": "gpt-5.6-luna", "endpoint": "https://api.openai.com/v1",
                  "env_key": "OPENAI_API_KEY", "api_format": "openai",
                  "omit_temperature": True, "max_tokens_field": "max_completion_tokens",
                  "reasoning_effort": "low"},
        "frontier": {"model": "gpt-5.6-sol", "endpoint": "https://api.openai.com/v1",
                     "env_key": "OPENAI_API_KEY", "api_format": "openai",
                     "omit_temperature": True, "max_tokens_field": "max_completion_tokens",
                     "reasoning_effort": "low"},
    },
    "claude": {
        "cheap": {"model": "claude-haiku-4-5-20251001",
                  "endpoint": "https://api.anthropic.com/v1",
                  "env_key": "ANTHROPIC_API_KEY", "api_format": "anthropic"},
        "frontier": {"model": "claude-opus-5",
                     "endpoint": "https://api.anthropic.com/v1",
                     "env_key": "ANTHROPIC_API_KEY", "api_format": "anthropic"},
    },
    "gemini": {
        "cheap": {"model": "gemini-3.1-flash-lite",
                  "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai",
                  "env_key": "GEMINI_API_KEY", "api_format": "openai"},
        "frontier": {"model": "gemini-3.1-pro-preview",
                     "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai",
                     "env_key": "GEMINI_API_KEY", "api_format": "openai"},
    },
    "kimi": {
        "cheap": {"model": "kimi-k2.6", "endpoint": "https://api.moonshot.ai/v1",
                  "env_key": "KIMI_API_KEY", "api_format": "openai"},
        "frontier": {"model": "kimi-k3", "endpoint": "https://api.moonshot.ai/v1",
                     "env_key": "KIMI_API_KEY", "api_format": "openai",
                     "extra": {"reasoning_effort": "low"}},
    },
    "qwen": {
        "cheap": {"model": "qwen3.7-plus-2026-05-26",
                  "endpoint": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                  "env_key": "ALIBABA_API_KEY", "api_format": "openai",
                  "discount_window_utc": (14, 24)},
        "frontier": {"model": "qwen3.7-max-2026-06-08",
                     "endpoint": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                     "env_key": "ALIBABA_API_KEY", "api_format": "openai",
                     "discount_window_utc": (14, 24)},
    },
}

DESIGN_PROMPT = """You are an expert designer of multi-step LLM pipelines for business problem solving.

Design a pipeline to answer the business problem below. The pipeline will be executed
step by step by the SAME language model on every step; each step receives the problem
and all previous step outputs. Intermediate steps may analyze, draft, critique or
refine; the FINAL step must produce the complete answer to the problem.

Rules:
1. Output ONLY a JSON object of the form:
   {{"steps": [{{"name": str, "role": str, "systemPrompt": str}}, ...]}}
2. Use 1 to 4 steps. Each systemPrompt instructs the model what to produce at that step.
3. No commentary outside the JSON. No markdown fences.
4. systemPrompt text must not include the problem itself (it is provided at run time).

=== BUSINESS PROBLEM ===
{problem_text}"""

REPAIR_PROMPT = """Your previous output was not valid. Error: {error}

Output ONLY the corrected JSON object:
{{"steps": [{{"name": str, "role": str, "systemPrompt": str}}, ...]}} — 1 to 4 steps,
no commentary, no markdown fences."""


def validate_design(text):
    """Return (steps, error). steps = list of {name, role, systemPrompt}."""
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.lower().startswith("json"):
            t = t[4:]
    try:
        obj = json.loads(t)
    except Exception as e:
        return None, f"JSON parse error: {e}"
    steps = obj.get("steps") if isinstance(obj, dict) else None
    if not isinstance(steps, list) or not (1 <= len(steps) <= 4):
        return None, "need 1-4 steps"
    for i, s in enumerate(steps):
        if not isinstance(s, dict) or not isinstance(s.get("systemPrompt"), str) \
                or not s["systemPrompt"].strip():
            return None, f"step {i} missing systemPrompt"
        s.setdefault("name", f"Step{i+1}")
        s.setdefault("role", s["name"].lower())
    return steps, None


class CreditExhausted(Exception):
    pass


def looks_like_credit(msg):
    m = msg.lower()
    return any(k in m for k in ("credit", "insufficient", "balance", "402",
                                "exceeded_current_quota", "payment required"))


def call(cfg, messages, keys):
    """One chat completion; returns (content, usage). Raises CreditExhausted."""
    if cfg["api_format"] == "anthropic":
        return _call_anthropic(cfg, messages, keys)
    payload = {"model": cfg["model"], "messages": messages}
    payload[cfg.get("max_tokens_field", "max_tokens")] = MAX_TOKENS
    if cfg.get("reasoning_effort"):
        payload["reasoning_effort"] = cfg["reasoning_effort"]
    if cfg.get("extra"):
        payload.update(cfg["extra"])
    req = urllib.request.Request(
        cfg["endpoint"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {keys[cfg['env_key']]}",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-study3/1.0"})
    for attempt in range(7):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"] or "", data.get("usage", {})
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = " | " + e.read().decode()[:300]
            except Exception:
                pass
            if looks_like_credit(f"HTTP {e.code}{body}"):
                raise CreditExhausted(f"HTTP {e.code}{body}")
            if e.code == 429:
                if attempt >= 6:
                    raise RuntimeError(f"HTTP 429 after 7 attempts{body}")
                wait = float(e.headers.get("Retry-After") or 0) or (15 * (attempt + 1))
                time.sleep(min(wait, 120))
                continue
            if attempt < 6 and e.code >= 500:
                time.sleep(2 ** attempt * 2)
                continue
            raise RuntimeError(f"HTTP {e.code}{body}")
        except CreditExhausted:
            raise
        except Exception:
            if attempt < 6:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError("call(): retry loop exhausted")


def _call_anthropic(cfg, messages, keys):
    # Anthropic rejects system-role entries inside messages; hoist to top-level.
    sys_parts = [m["content"] for m in messages if m["role"] == "system"]
    msgs = [m for m in messages if m["role"] != "system"]
    payload = {"model": cfg["model"], "messages": msgs, "max_tokens": MAX_TOKENS}
    if sys_parts:
        payload["system"] = "\n\n".join(sys_parts)
    req = urllib.request.Request(
        cfg["endpoint"].rstrip("/") + "/messages",
        data=json.dumps(payload).encode(),
        headers={"x-api-key": keys[cfg["env_key"]],
                 "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-study3/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
            text = "".join(b.get("text", "") for b in data.get("content", [])
                           if b.get("type") == "text")
            return text, data.get("usage", {})
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = " | " + e.read().decode()[:300]
            except Exception:
                pass
            if looks_like_credit(f"HTTP {e.code}{body}"):
                raise CreditExhausted(f"HTTP {e.code}{body}")
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise RuntimeError(f"HTTP {e.code}{body}")
        except CreditExhausted:
            raise
        except Exception:
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise


def in_window_utc(start, end):
    h = datetime.now(timezone.utc).hour
    return start <= h < end


def load_ledger():
    done, exhausted = set(), set()
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("status") == "completed" and r.get("final_len", 0) > 0:
                done.add(r["key"])
            if r.get("status") == "credit_exhausted":
                exhausted.add(r["family"])
    return done, exhausted


def append_ledger(rec):
    with LEDGER.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def load_problems():
    """The 19 confirmatory problems = problems present in the frozen main ledger."""
    led = json.loads((ROOT / "runs" / "logs" / "main_run_ledger.json").read_text())
    ids = sorted({r["problemId"] for r in led["results"] if r.get("problemId")})
    bank = {}
    for f in ["business_problems_15.json", "business_problems_domain_15.json"]:
        bank.update(json.loads((ROOT / "data" / "problems" / f).read_text()))
    out = {}
    for pid in ids:
        p = bank[pid]
        out[pid] = f"{p['background_context']}\n\n{p['business_problem']}"  # D32.3 verbatim
    return out


def run_task(task, problems, keys, ignore_window):
    """One (arm, family, problem, rep): design -> validate -> execute. Ledger-append."""
    arm, family, pid, rep = task["arm"], task["family"], task["problem"], task["rep"]
    key = f"{arm}__{family}__{pid}__rep{rep}"
    rec = {"key": key, "arm": arm, "family": family, "problemId": pid, "rep": rep,
           "prompt_tag": PROMPT_TAG,
           "started_at": datetime.now(timezone.utc).isoformat()}
    cfg_d = MODELS[family]["frontier" if arm == "D-FRONT" else "cheap"]
    cfg_x = MODELS[family]["cheap"]
    w = cfg_d.get("discount_window_utc") or cfg_x.get("discount_window_utc")
    if w and not ignore_window and not in_window_utc(*w):
        rec.update(status="deferred_window")
        append_ledger(rec)
        return "deferred"
    ptext = problems[pid]
    try:
        # 1) design (step-level checkpointing: killed chunks resume mid-task)
        ckpt_file = ROOT / "runs" / "study3" / "checkpoints" / f"{key}.json"
        ck = {}
        if ckpt_file.exists():
            try:
                ck = json.loads(ckpt_file.read_text())
            except Exception:
                ck = {}
        print(f"  [{key}] design call...", flush=True)
        if ck.get("steps"):
            raw, du, steps = ck["raw"], {}, ck["steps"]
        else:
            raw, du = call(cfg_d, [{"role": "user",
                                    "content": DESIGN_PROMPT.format(problem_text=ptext)}], keys)
        rec["designer_model"] = cfg_d["model"]
        rec["designer_usage"] = du
        steps, err = validate_design(raw)
        if err:
            raw2, du2 = call(cfg_d, [
                {"role": "user", "content": DESIGN_PROMPT.format(problem_text=ptext)},
                {"role": "assistant", "content": raw},
                {"role": "user", "content": REPAIR_PROMPT.format(error=err)}], keys)
            rec["designer_usage_repair"] = du2
            steps, err2 = validate_design(raw2)
            if err2:
                rec.update(status="design_failed", error=f"{err} / repair: {err2}",
                           finished_at=datetime.now(timezone.utc).isoformat())
                append_ledger(rec)
                return "design_failed"
            raw = raw2
        DESIGNS_DIR.mkdir(parents=True, exist_ok=True)
        (DESIGNS_DIR / f"{key}.designer_raw.txt").write_text(raw)
        rec["n_steps"] = len(steps)
        ckpt_file.parent.mkdir(parents=True, exist_ok=True)

        # 2) execute steps on the cheap sibling (checkpoint after each step)
        prior, step_logs = ck.get("prior", ""), ck.get("step_logs", [])
        ckpt_file.write_text(json.dumps({"raw": raw, "steps": steps,
                                         "prior": prior, "step_logs": step_logs}))
        done_names = {s["name"] for s in step_logs}
        for s in steps:
            if s["name"] in done_names:
                continue
            user = (f"=== BUSINESS PROBLEM ===\n{ptext}\n\n"
                    + (f"=== PREVIOUS STEP OUTPUTS ===\n{prior}\n\n" if prior else "")
                    + "Produce your step's output now.")
            out, u = call(cfg_x, [{"role": "system", "content": s["systemPrompt"]},
                                  {"role": "user", "content": user}], keys)
            print(f"  [{key}] step {s['name']} done ({len(out)} chars)", flush=True)
            step_logs.append({"name": s["name"], "role": s["role"],
                              "system_prompt": s["systemPrompt"],
                              "output_len": len(out), "usage": u})
            prior += f"\n\n--- {s['name']} ---\n{out}"
            ckpt_file.write_text(json.dumps({"raw": raw, "steps": steps,
                                             "prior": prior, "step_logs": step_logs}))
        ckpt_file.unlink(missing_ok=True)
        final = step_logs[-1]["output_len"]
        rec.update(status="completed", executor_model=cfg_x["model"],
                   steps=step_logs, final_len=final,
                   finished_at=datetime.now(timezone.utc).isoformat())
        append_ledger(rec)
        # solution text for the judging store
        sol_file = ROOT / "runs" / "study3" / "solutions" / f"{key}.txt"
        sol_file.parent.mkdir(parents=True, exist_ok=True)
        # final step output = last element of prior block
        sol_file.write_text(prior.split(f"--- {steps[-1]['name']} ---\n")[-1])
        return "completed"
    except CreditExhausted as e:
        rec.update(status="credit_exhausted", error=str(e)[:300],
                   finished_at=datetime.now(timezone.utc).isoformat())
        append_ledger(rec)
        with EXHAUSTION.open("a") as f:
            f.write(json.dumps({"family": family, "reason": str(e)[:300],
                                "ts": datetime.now(timezone.utc).isoformat(),
                                "policy": "skip family, continue others"}) + "\n")
        return "credit_exhausted"
    except Exception as e:
        rec.update(status="failed", error=str(e)[:300],
                   finished_at=datetime.now(timezone.utc).isoformat())
        append_ledger(rec)
        return "failed"


def build_store():
    """Rebuild the judge_v2-compatible store from solutions + ledger (idempotent)."""
    entries = []
    sol_dir = ROOT / "runs" / "study3" / "solutions"
    if sol_dir.exists():
        for f in sorted(sol_dir.glob("*.txt")):
            key = f.stem
            arm, family, pid, rep = key.split("__")
            entries.append({"runId": key, "problemId": pid,
                            "fulltext": f.read_text(), "status": "completed",
                            "family": family, "arm": arm, "rep": rep})
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps({"protocol": "13", "prompt_tag": PROMPT_TAG,
                                 "runs": entries}, indent=1))
    print(f"store: {STORE} ({len(entries)} solutions)")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--families", default="")
    ap.add_argument("--reps", type=int, default=0, help="override rep count")
    ap.add_argument("--ignore-window", action="store_true")
    ap.add_argument("--build-store", action="store_true")
    args = ap.parse_args()

    if args.build_store:
        build_store()
        return

    problems = load_problems()
    pids = PILOT_PROBLEMS if args.pilot else sorted(problems)
    reps = args.reps or (1 if args.pilot else 3)
    fams = args.families.split(",") if args.families else list(MODELS)
    tasks = [{"arm": arm, "family": fam, "problem": pid, "rep": r}
             for arm in ["D-SELF", "D-FRONT"] for fam in fams
             for pid in pids for r in range(1, reps + 1)]
    # deterministic interleave (seed 42, D17)
    import random
    random.Random(42).shuffle(tasks)

    done, exhausted = load_ledger()
    todo = [t for t in tasks
            if f"{t['arm']}__{t['family']}__{t['problem']}__rep{t['rep']}" not in done
            and t["family"] not in exhausted]
    print(f"Study 3 plan: {len(tasks)} tasks | done {len(tasks)-len(todo)-sum(1 for t in tasks if t['family'] in exhausted)} | "
          f"todo {len(todo)} | exhausted families: {sorted(exhausted) or 'none'}"
          + (" (WINDOW OVERRIDE)" if args.ignore_window else ""))
    if args.dry_run:
        from collections import Counter
        print(Counter((t["arm"], t["family"]) for t in tasks))
        return

    keys = {k: load_key(k) for k in
            {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
             "KIMI_API_KEY", "ALIBABA_API_KEY"}}
    from collections import Counter
    stats = Counter()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(run_task, t, problems, keys, args.ignore_window)
                for t in todo]
        for i, f in enumerate(futs, 1):
            res = f.result()
            stats[res] += 1
            if i % 20 == 0 or res in ("failed", "credit_exhausted", "design_failed"):
                print(f"[{i}/{len(todo)}] {res} | totals: {dict(stats)}")
    print(f"done: {dict(stats)}")
    build_store()


if __name__ == "__main__":
    main()
