#!/usr/bin/env python3
"""Main-run / repair judging harness v2 (Amendment A1 items A1.2–A1.3, D35–D36).

Differences vs judge_phaseA.py (which stays frozen for pilot reproducibility):

  A1.2 FULL-TEXT SOLUTIONS: solutions are read from a full-text store
  (runs/fulltext/*.json, built by capture_fulltext.py or main_run.mjs),
  NOT from the run_status-truncated finalResponse. The pilot showed the
  16,000-char run_status cap truncated 130/371 solutions and judges scored
  the truncated text (results/QUALITATIVE-NOTES.md, Finding 1).

  A1.3 JUDGE EMISSION INTEGRITY: max_tokens raised 512 -> 2048 (pilot:
  deepseek-chat justifications overflowed 512 tokens and dropped the 5th
  dimension in 356 judgments), plus a post-parse integrity check — any
  judgment missing one of the 5 dimensions is retried up to 2 extra times;
  failures are written with "incomplete": true for audit.

Everything else is unchanged from the frozen instrument: same 3 judges
(model_registry.json `judges`), same 3 verbatim D10 prompt variants,
temperature 0, blinded (problem + solution only), shuffled order seed
20260731, resumable JSONL, concurrent per-judge lanes (D34).

Usage:
  python3 code/judge_v2.py --store runs/fulltext/main_fulltext.json \
                           --out runs/logs/main_judgments.jsonl
  python3 code/judge_v2.py --store runs/fulltext/pilot_repair_capped.json \
                           --out runs/logs/pilot_repair_judgments.jsonl

NOT EXECUTED until the author opens the discount window (author instruction
2026-07-30). Zero credits consumed by preparing this file.
"""

import argparse
import concurrent.futures
import json
import os
import random
import re
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20260731
DIMENSIONS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]
MAX_TOKENS_A1 = 2048          # A1.3: was 512 in pilot (D36)
MAX_COMPLETION_RETRIES = 2    # extra attempts when dimensions are missing
WORKERS_PER_JUDGE = 8

cfg = json.load(open(ROOT / "config/experiment_config.json"))["judging"]
judges = json.load(open(ROOT / "config/model_registry.json"))["judges"]
variants = {
    json.loads(l)["id"]: json.loads(l)["description"]
    for l in open(ROOT / "evaluation/judge_prompts/judge_variations.jsonl")
    if l.strip()
}
problems = json.load(open(ROOT / "config/pilot_problems_phaseA.json"))["problems"]
main_problems_path = ROOT / "data/problems/business_problems_domain_15.json"
# Full problem bank (30): pilot 11 + authored sets live under data/problems;
# the store carries problemId, and every problem text is resolved below.
for extra in (ROOT / "data/problems").glob("*.json"):
    try:
        blob = json.load(open(extra))
        if isinstance(blob, dict) and "problems" in blob and isinstance(blob["problems"], dict):
            problems.update(blob["problems"])
        elif isinstance(blob, list):
            for p in blob:
                if isinstance(p, dict) and "id" in p:
                    problems.setdefault(p["id"], p)
        elif isinstance(blob, dict) and any(
            isinstance(v, dict) and "business_problem" in v for v in blob.values()
        ):
            # flat id->problem map (e.g. business_problems_30.json, the main bank)
            for pid, p in blob.items():
                if isinstance(p, dict):
                    problems.setdefault(pid, p)
    except Exception:
        pass


def load_key(env_key):
    names = [env_key] + (["TOGETHER_AI_API_KEY"] if env_key == "TOGETHER_API_KEY" else [])
    for name in names:
        if os.environ.get(name):
            return os.environ[name]
    for env_file in (ROOT / ".env", ROOT.parent.parent / ".env"):
        if not env_file.exists():
            continue
        for line in env_file.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip() in names and v.strip():
                return v.strip().strip('"').strip("'")
    sys.exit(f"{env_key} not set (env or .env)")


KEYS = {j["env_key"]: load_key(j["env_key"]) for j in judges}

SCORE_RE = {
    d: re.compile(rf"{d.split()[0]}[^:\n]*:\s*\**\s*\[?\s*([1-5])", re.IGNORECASE)
    for d in DIMENSIONS
}


def parse_scores(text):
    return {d: (int(m.group(1)) if (m := rx.search(text)) else None)
            for d, rx in SCORE_RE.items()}


def call_judge(judge, prompt):
    payload = {
        "model": judge["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": cfg["temperature"],
        "max_tokens": MAX_TOKENS_A1,
    }
    payload.update(judge.get("extra_params", {}))
    req = urllib.request.Request(
        judge["endpoint"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {KEYS[judge['env_key']]}",
            "Content-Type": "application/json",
            "User-Agent": "orchestration-economics-judge/2.0",
        },
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
            return (data["choices"][0]["message"]["content"],
                    data.get("usage", {}),
                    data.get("model", judge["model"]))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError("unreachable")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True, help="full-text store JSON (capture_fulltext.py / main_run.mjs)")
    ap.add_argument("--out", required=True, help="output judgments JSONL")
    args = ap.parse_args()

    store_path, out_path = Path(args.store), Path(args.out)
    solutions = [e for e in json.load(open(store_path))["runs"]
                 if e.get("status") == "completed" and (e.get("fulltext") or "").strip()]
    rng = random.Random(SEED)
    rng.shuffle(solutions)  # blinded presentation order (same seed as pilot)

    done = set()
    if out_path.exists():
        for line in open(out_path):
            if line.strip():
                j = json.loads(line)
                if not j.get("error") and not j.get("incomplete"):
                    done.add((j["runId"], j["judge_family"], j["variant"]))

    total = len(solutions) * len(judges) * len(variants)
    tasks = []
    for sol in solutions:
        prob = problems.get(sol["problemId"])
        if not prob:
            sys.exit(f"problem text missing for {sol['problemId']}")
        problem_text = f"{prob['background_context']}\n\n{prob['business_problem']}"
        for judge in judges:
            for var_id, template in variants.items():
                if (sol["runId"], judge["family"], var_id) in done:
                    continue
                prompt = (template.replace("{problem_text}", problem_text)
                          .replace("{solution_text}", sol["fulltext"]))  # A1.2: FULL text
                tasks.append((sol, judge, var_id, prompt))

    print(f"judge_v2: {len(solutions)} solutions x {len(judges)} judges x {len(variants)} variants; "
          f"{len(tasks)} calls pending ({len(done)} already done); max_tokens={MAX_TOKENS_A1} (A1.3)")

    write_lock = threading.Lock()
    counter = {"n": len(done)}
    semaphores = {j["family"]: threading.Semaphore(WORKERS_PER_JUDGE) for j in judges}

    def run_task(task, out):
        sol, judge, var_id, prompt = task
        with semaphores[judge["family"]]:
            rec = None
            for attempt in range(1 + MAX_COMPLETION_RETRIES):  # A1.3 integrity loop
                try:
                    text, usage, resolved = call_judge(judge, prompt)
                    scores = parse_scores(text)
                    rec = {
                        "runId": sol["runId"], "problemId": sol["problemId"],
                        "judge_family": judge["family"], "judge_model": judge["model"],
                        "judge_model_resolved": resolved, "variant": var_id,
                        "scores": scores, "raw": text, "usage": usage,
                        "max_tokens": MAX_TOKENS_A1, "harness": "judge_v2/A1",
                        "completion_retry": attempt,
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                    if all(v is not None for v in scores.values()):
                        break  # complete judgment
                except Exception as e:  # noqa: BLE001 - recorded, retried or audited
                    rec = {"runId": sol["runId"], "problemId": sol["problemId"],
                           "judge_family": judge["family"], "judge_model": judge["model"],
                           "variant": var_id, "error": str(e)[:300], "harness": "judge_v2/A1",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    break
            if rec and rec.get("scores") and any(v is None for v in rec["scores"].values()):
                rec["incomplete"] = True
        with write_lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            counter["n"] += 1
            print(f"[{counter['n']}/{total}] run {sol['runId']} {judge['family']}/{var_id}: "
                  f"{rec.get('scores') or rec.get('error')}"
                  f"{' INCOMPLETE' if rec.get('incomplete') else ''}")

    with open(out_path, "a") as out:
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS_PER_JUDGE * len(judges)) as pool:
            futures = [pool.submit(run_task, t, out) for t in tasks]
            for f in concurrent.futures.as_completed(futures):
                f.result()

    print(f"done -> {out_path}")


if __name__ == "__main__":
    main()
