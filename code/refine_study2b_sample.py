#!/usr/bin/env python3
"""Protocol 11 / Study 2b — PILOT sample (Protocol 11 sec 4, locked).

Draws 20 random C-T-P pairs per family (gpt, gemini), seed 20260821, each paired
with the same-problem same-family F-S-N run of MINIMAL runId (Protocol 09 sec 9
pairing rule). Random, not top-scoring (avoids regression-to-mean / cherry-pick).
Stdlib-only. Output: runs/refine_b/sample_pilot.json
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20260821
FAMILIES = ["gpt", "gemini"]
N_PER_FAMILY = 20


def load_problems():
    """Mirror judge_v2.py problem-bank resolution (config pilot + data/problems)."""
    problems = json.load(open(ROOT / "config/pilot_problems_phaseA.json"))["problems"]
    for extra in sorted((ROOT / "data/problems").glob("*.json")):
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
                for pid, p in blob.items():
                    if isinstance(p, dict):
                        problems.setdefault(pid, p)
        except Exception:
            pass
    return problems


def main():
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    runs = sorted(store["runs"], key=lambda r: int(r["runId"]))
    text_by_run = {r["runId"]: r for r in runs}
    problems = load_problems()

    # F-S-N mate index: first (minimal) runId per (family, problemId)
    fsn_index = {}
    for r in runs:
        if r["cell"] == "F-S-N" and r.get("fulltext"):
            key = (r["family"], str(r["problemId"]))
            fsn_index.setdefault(key, r)

    rng = random.Random(SEED)
    out = {"protocol": "11", "study": "Study2b-refiner", "phase": "pilot",
           "seed": SEED, "pairs": []}
    for fam in FAMILIES:
        pool = [r for r in runs
                if r["cell"] == "C-T-P" and r["family"] == fam and r.get("fulltext")
                and (r["family"], str(r["problemId"])) in fsn_index]
        ids = sorted({r["runId"] for r in pool})
        assert len(ids) == 57, f"{fam}: locked pool fact violated ({len(ids)} != 57)"
        picked = rng.sample(ids, N_PER_FAMILY)
        for rid in sorted(picked):
            row = text_by_run[rid]
            mate = fsn_index[(fam, str(row["problemId"]))]
            prob = problems.get(str(row["problemId"]))
            assert prob, f"problem text missing for {row['problemId']}"
            out["pairs"].append({
                "ctp_runId": int(rid),
                "fsn_runId": int(mate["runId"]),
                "family": fam,
                "problemId": str(row["problemId"]),
                "problem_text": f"{prob['background_context']}\n\n{prob['business_problem']}",
                "ctp_fulltext": row["fulltext"],
            })
    dst = ROOT / "runs/refine_b/sample_pilot.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"study2b pilot sample: {len(out['pairs'])} pairs "
          f"({N_PER_FAMILY}/family x {FAMILIES}) -> {dst}")


if __name__ == "__main__":
    main()
