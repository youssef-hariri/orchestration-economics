#!/usr/bin/env python3
"""Protocol 09 / Study 2 — refinement pass (pilot).

Runs the FROZEN universal refiner prompt (Protocol 09 sec 4, D39 add-only rule)
over the sampled C-T-P answers with deepseek-chat (cheap workhorse; temp 0,
max_tokens 8192). Resumable JSONL. Then emits a judge_v2-compatible store
(runIds namespaced "R<ctp_runId>") for the frozen judging panel.

Outputs: runs/logs/refine_pilot.jsonl, runs/refine/refined_store_pilot.json
"""
import concurrent.futures
import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import judge_v2 as jv  # noqa: E402

REFINER = {"model": "deepseek-chat", "endpoint": "https://api.deepseek.com/v1",
           "env_key": "DEEPSEEK_API_KEY"}
MAX_TOKENS = 8192
WORKERS = 8

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


def call(prompt):
    payload = {"model": REFINER["model"],
               "messages": [{"role": "user", "content": prompt}],
               "temperature": 0, "max_tokens": MAX_TOKENS}
    req = urllib.request.Request(
        REFINER["endpoint"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {jv.KEYS[REFINER['env_key']]}",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-study2/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"], data.get("usage", {})
        except Exception:
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=str(ROOT / "runs/refine/sample_pilot.json"))
    ap.add_argument("--log", default=str(ROOT / "runs/logs/refine_pilot.jsonl"))
    ap.add_argument("--store", default=str(ROOT / "runs/refine/refined_store_pilot.json"))
    args = ap.parse_args()
    sample = json.load(open(args.sample))
    pairs = sample["pairs"]
    log_path = Path(args.log)
    done = set()
    refined = {}
    if log_path.exists():
        for line in open(log_path):
            j = json.loads(line)
            if j.get("refined_text"):
                done.add(j["ctp_runId"])
                refined[j["ctp_runId"]] = j

    tasks = [p for p in pairs if p["ctp_runId"] not in done]
    print(f"refine pilot: {len(pairs)} answers; {len(tasks)} pending, {len(done)} done; "
          f"model={REFINER['model']} temp=0 max_tokens={MAX_TOKENS}")

    lock = threading.Lock()
    counter = {"n": len(done)}
    sem = threading.Semaphore(WORKERS)

    def run_task(pair, out):
        prompt = (PROMPT.replace("{problem_text}", pair["problem_text"])
                  .replace("{solution_text}", pair["ctp_fulltext"]))
        with sem:
            rec = None
            try:
                text, usage = call(prompt)
                rec = {"ctp_runId": pair["ctp_runId"], "fsn_runId": pair["fsn_runId"],
                       "family": pair["family"], "problemId": pair["problemId"],
                       "refined_text": text if text and text.strip() else None,
                       "orig_len": len(pair["ctp_fulltext"]),
                       "refined_len": len(text) if text else 0,
                       "usage": usage, "refiner_model": REFINER["model"],
                       "prompt": "protocol09-v1",
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            except Exception as e:  # noqa: BLE001
                rec = {"ctp_runId": pair["ctp_runId"], "fsn_runId": pair["fsn_runId"],
                       "family": pair["family"], "problemId": pair["problemId"],
                       "error": str(e)[:300],
                       "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            counter["n"] += 1
            ok = rec.get("refined_text") is not None
            print(f"[{counter['n']}/{len(pairs)}] {rec['family']} ctp={rec['ctp_runId']}: "
                  f"{'OK ' + str(rec.get('refined_len')) + ' chars' if ok else rec.get('error')}")

    with open(log_path, "a") as out:
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futs = [pool.submit(run_task, p, out) for p in tasks]
            for f in concurrent.futures.as_completed(futs):
                f.result()

    # --- build judge_v2-compatible store
    refined = {}
    for line in open(log_path):
        j = json.loads(line)
        if j.get("refined_text"):
            refined[j["ctp_runId"]] = j
    store = {"source": "protocol09-study2-refiner", "prompt": "protocol09-v1",
             "refiner_model": REFINER["model"],
             "runs": [{"runId": f"R{j['ctp_runId']}", "problemId": j["problemId"],
                       "status": "completed", "fulltext": j["refined_text"],
                       "family": j["family"], "base_runId": j["ctp_runId"]}
                      for _, j in sorted(refined.items())]}
    dst = Path(args.store)
    dst.write_text(json.dumps(store, indent=1, ensure_ascii=False) + "\n")
    n_fail = len(pairs) - len(store["runs"])
    print(f"done -> {log_path}; store with {len(store['runs'])} refined answers -> {dst}; "
          f"failures={n_fail} ({n_fail / len(pairs) * 100:.1f}%)")


if __name__ == "__main__":
    main()
