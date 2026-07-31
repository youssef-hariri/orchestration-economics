#!/usr/bin/env python3
"""Pilot judging harness (D10 prompts verbatim, D26 LLM-judge-only, D32.4).

For every completed non-empty pilot solution: 3 judges x 3 prompt variants
= 9 scores per solution (config/experiment_config.json `judging`, frozen).
Blinding: prompts contain ONLY problem text + solution text (no arm/family/
cell identifiers); item order shuffled with seed 20260731.

Judges: config/model_registry.json `judges` (Together.ai, TOGETHER_API_KEY).
Together requires a custom User-Agent (known pitfall).

Resumable: one JSONL line per (solution, judge, variant) call, flushed
immediately; existing keys are skipped on restart.

Usage: TOGETHER_API_KEY=... python3 code/judge.py
Output: runs/logs/pilot_judgments.jsonl
"""

import json
import os
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN_LOG = ROOT / "runs/logs/pilot_gen_2026-07-31.json"
OUT = ROOT / "runs/logs/pilot_judgments.jsonl"
SEED = 20260731

DIMENSIONS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]

cfg = json.load(open(ROOT / "config/experiment_config.json"))["judging"]
judges = json.load(open(ROOT / "config/model_registry.json"))["judges"]
variants = {
    json.loads(l)["id"]: json.loads(l)["description"]
    for l in open(ROOT / "evaluation/judge_prompts/judge_variations.jsonl")
    if l.strip()
}
pilot = json.load(open(ROOT / "config/pilot_problems.json"))

API_KEY = os.environ.get("TOGETHER_API_KEY")
if not API_KEY:
    sys.exit("TOGETHER_API_KEY not set")

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
    body = json.dumps({
        "model": judge["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": cfg["temperature"],
        "max_tokens": cfg["max_tokens"],
    }).encode()
    req = urllib.request.Request(
        judge["endpoint"].rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "orchestration-economics-judge/1.0",
        },
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"], data.get("usage", {})
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
n = 0
with open(OUT, "a") as out:
    for sol in solutions:
        prob = pilot["problems"][sol["problemId"]]
        problem_text = f"{prob['background_context']}\n\n{prob['business_problem']}"
        for judge in judges:
            for var_id, template in variants.items():
                n += 1
                key = (sol["runId"], judge["family"], var_id)
                if key in done:
                    continue
                prompt = template.replace("{problem_text}", problem_text).replace(
                    "{solution_text}", sol["finalResponse"]
                )
                try:
                    text, usage = call_judge(judge, prompt)
                    rec = {
                        "runId": sol["runId"],
                        "problemId": sol["problemId"],
                        "judge_family": judge["family"],
                        "judge_model": judge["model"],
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
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                print(f"[{n}/{total}] run {sol['runId']} {judge['family']}/{var_id}: "
                      f"{rec.get('scores') or rec.get('error')}")
                time.sleep(0.3)

print(f"done -> {OUT}")
