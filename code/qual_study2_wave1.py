#!/usr/bin/env python3
"""Protocol 10 sec 4 — Wave 1 inductive coding (blinded).

2 coders x 6 wave-1 triples x 3 texts = 36 calls. Each coder freely lists
observable features relevant to: frontier edge, refinement effects, saturation.
Outputs: runs/logs/qual2_wave1.jsonl
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
from qual_a4_closed import call  # noqa: E402

CODER_FAMILIES = ["deepseek", "zhipu"]
WORKERS_PER_CODER = 8

PROMPT = """You are a qualitative researcher. Below is ONE answer to a business problem \
(anonymized; you do not know which system produced it). List up to 10 OBSERVABLE \
features of this text, each as a short factual phrase. Focus on:
1) signs of original insight, reframing, or depth of reasoning;
2) specificity of evidence (numbers, named tools, concrete steps) vs generic advice;
3) structural properties (sections, tables, timelines, checklists);
4) signs of verbosity, repetition, or boilerplate padding;
5) rhetorical/cultural style (metaphors, tone, cultural adaptation).
Be descriptive, not evaluative. Return ONLY valid JSON: {{"features": ["...", ...]}}

=== BUSINESS PROBLEM ===
{problem_text}

=== ANSWER ===
{solution_text}"""


def main():
    pack = json.load(open(ROOT / "runs/qual2/triples.json"))
    triples = pack["triples"]
    # locked rule: 2 lowest tripleId per family
    wave1 = []
    for fam in ["kimi", "claude", "qwen"]:
        wave1 += sorted([t for t in triples if t["family"] == fam],
                        key=lambda t: t["tripleId"])[:2]
    coders = [j for j in jv.judges if j["family"] in CODER_FAMILIES]

    out_path = ROOT / "runs/logs/qual2_wave1.jsonl"
    done = set()
    if out_path.exists():
        for line in open(out_path):
            j = json.loads(line)
            if j.get("features"):
                done.add((j["key"], j["coder_family"]))

    tasks = []
    for t in wave1:
        for role, text in t["texts"].items():
            key = f"{t['tripleId']}:{role}"
            prompt = (PROMPT.replace("{problem_text}", t["problem_text"][:2000])
                      .replace("{solution_text}", text))
            for coder in coders:
                if (key, coder["family"]) not in done:
                    tasks.append((key, coder, prompt))
    total = len(wave1) * 3 * len(coders)
    print(f"wave1: {len(wave1)} triples x 3 texts x {len(coders)} coders; "
          f"{len(tasks)} pending, {len(done)} done")

    lock = threading.Lock()
    counter = {"n": len(done)}
    sems = {c["family"]: threading.Semaphore(WORKERS_PER_CODER) for c in coders}

    def run_task(task, out):
        key, coder, prompt = task
        with sems[coder["family"]]:
            rec = None
            for attempt in range(3):
                try:
                    text, usage = call(coder, prompt)
                    import re
                    m = re.search(r"\{.*\}", text, re.S)
                    feats = json.loads(m.group(0)).get("features") if m else None
                    rec = {"key": key, "coder_family": coder["family"],
                           "features": feats, "usage": usage,
                           "harness": "qual_study2/wave1",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    if feats:
                        break
                except Exception as e:  # noqa: BLE001
                    rec = {"key": key, "coder_family": coder["family"],
                           "error": str(e)[:300], "harness": "qual_study2/wave1",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    time.sleep(2 ** attempt * 2)
        with lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            counter["n"] += 1
            ok = bool(rec.get("features"))
            print(f"[{counter['n']}/{total}] {key} {coder['family']}: "
                  f"{'OK ' + str(len(rec['features'])) + ' features' if ok else rec.get('error', 'INCOMPLETE')}")

    with open(out_path, "a") as out:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=WORKERS_PER_CODER * len(coders)) as pool:
            futs = [pool.submit(run_task, t, out) for t in tasks]
            for f in concurrent.futures.as_completed(futs):
                f.result()
    print(f"done -> {out_path}")


if __name__ == "__main__":
    main()
