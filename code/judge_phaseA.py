#!/usr/bin/env python3
"""Pilot judging harness (D10 prompts verbatim, D26 LLM-judge-only, D32.4).

For every completed non-empty pilot solution: 3 judges x 3 prompt variants
= 9 scores per solution (config/experiment_config.json `judging`, frozen).
Blinding: prompts contain ONLY problem text + solution text (no arm/family/
cell identifiers); item order shuffled with seed 20260731.

Judges: config/model_registry.json `judges` (D33 panel: deepseek-chat on
DeepSeek API, GLM-5.2 thinking-disabled + Llama-3.3-70B on Together).
Together requires a custom User-Agent (known pitfall).

Resumable: one JSONL line per (solution, judge, variant) call, flushed
immediately; existing keys are skipped on restart.

Concurrent: judging is latency-insensitive (scores are the measurement, not
timing), so calls run in a thread pool — 8 workers per judge provider lane,
JSONL appends serialized by a lock. DeepSeek's documented concurrency limit
is 2500; Together serverless handles small pools comfortably.

Usage: python3 code/judge.py   (per-judge keys read from env, or from the
repo/workspace .env, both git-ignored)
Output: runs/logs/pilot_phaseA_judgments.jsonl
"""

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
GEN_LOG = ROOT / "runs/logs/pilot_phaseA_2026-08-03.json"
OUT = ROOT / "runs/logs/pilot_phaseA_judgments.jsonl"
SEED = 20260731

DIMENSIONS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]

cfg = json.load(open(ROOT / "config/experiment_config.json"))["judging"]
judges = json.load(open(ROOT / "config/model_registry.json"))["judges"]
variants = {
    json.loads(l)["id"]: json.loads(l)["description"]
    for l in open(ROOT / "evaluation/judge_prompts/judge_variations.jsonl")
    if l.strip()
}
pilot = json.load(open(ROOT / "config/pilot_problems_phaseA.json"))

def load_key(env_key):
    """Env first (incl. TOGETHER_AI_API_KEY alias), then git-ignored .env files."""
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

gen = json.load(open(GEN_LOG))
solutions = [
    r for r in gen["results"]
    if r.get("status") == "completed" and (r.get("finalResponse") or "").strip()
]
# Blinded presentation order: shuffle; judge prompts never see arm identifiers.
rng = random.Random(SEED)
rng.shuffle(solutions)

done = set()
if OUT.exists():
    for line in open(OUT):
        if line.strip():
            j = json.loads(line)
            done.add((j["runId"], j["judge_family"], j["variant"]))

SCORE_RE = {
    d: re.compile(
        rf"{d.split()[0]}[^:\n]*:\s*\**\s*\[?\s*([1-5])", re.IGNORECASE
    )
    for d in DIMENSIONS
}


def parse_scores(text):
    scores = {}
    for d, rx in SCORE_RE.items():
        m = rx.search(text)
        scores[d] = int(m.group(1)) if m else None
    return scores


def call_judge(judge, prompt):
    payload = {
        "model": judge["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": cfg["temperature"],
        "max_tokens": cfg["max_tokens"],
    }
    payload.update(judge.get("extra_params", {}))  # e.g. GLM-5.2 thinking off (D33)
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        judge["endpoint"].rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEYS[judge['env_key']]}",
            "Content-Type": "application/json",
            "User-Agent": "orchestration-economics-judge/1.0",
        },
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            return (
                data["choices"][0]["message"]["content"],
                data.get("usage", {}),
                data.get("model", judge["model"]),  # resolved model (D33: deepseek-chat is an alias)
            )
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


total = len(solutions) * len(judges) * len(variants)
WORKERS_PER_JUDGE = 8

# task list preserves the blinded shuffled solution order within each judge lane
tasks = []
for sol in solutions:
    prob = pilot["problems"][sol["problemId"]]
    problem_text = f"{prob['background_context']}\n\n{prob['business_problem']}"
    for judge in judges:
        for var_id, template in variants.items():
            key = (sol["runId"], judge["family"], var_id)
            if key in done:
                continue
            prompt = template.replace("{problem_text}", problem_text).replace(
                "{solution_text}", sol["finalResponse"]
            )
            tasks.append((sol, judge, var_id, prompt))

write_lock = threading.Lock()
counter = {"n": len(done)}
semaphores = {j["family"]: threading.Semaphore(WORKERS_PER_JUDGE) for j in judges}


def run_task(task, out):
    sol, judge, var_id, prompt = task
    with semaphores[judge["family"]]:
        try:
            text, usage, resolved = call_judge(judge, prompt)
            rec = {
                "runId": sol["runId"],
                "problemId": sol["problemId"],
                "judge_family": judge["family"],
                "judge_model": judge["model"],
                "judge_model_resolved": resolved,
                "variant": var_id,
                "scores": parse_scores(text),
                "raw": text,
                "usage": usage,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        except Exception as e:  # noqa: BLE001 — recorded, judged later
            rec = {
                "runId": sol["runId"],
                "problemId": sol["problemId"],
                "judge_family": judge["family"],
                "judge_model": judge["model"],
                "variant": var_id,
                "error": str(e)[:300],
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
    with write_lock:
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out.flush()
        counter["n"] += 1
        print(f"[{counter['n']}/{total}] run {sol['runId']} {judge['family']}/{var_id}: "
              f"{rec.get('scores') or rec.get('error')}")


with open(OUT, "a") as out:
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=WORKERS_PER_JUDGE * len(judges)
    ) as pool:
        futures = [pool.submit(run_task, t, out) for t in tasks]
        for f in concurrent.futures.as_completed(futures):
            f.result()  # re-raise unexpected worker crashes

print(f"done -> {OUT}")
