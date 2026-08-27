#!/usr/bin/env python3
"""Protocol 11 / Study 2b — EXTENSION sample (Protocol 11 sec 4, locked).

Draws the remaining 37 C-T-P pairs per family (full locked pool = 57/family,
Protocol 11 sec 3), seed 20260822, disjoint from the pilot's 20 (kept intact and
pooled — no replacement). Stdlib-only. Output: runs/refine_b/sample_extension.json

Run ONLY after pilot gates G1+G2 pass (Protocol 11 sec 5) and the author decision
is logged in MANIFEST.
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20260822
FAMILIES = ["gpt", "gemini"]
N_PER_FAMILY_TOTAL = 57  # full locked pool


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

    pilot = json.load(open(ROOT / "runs/refine_b/sample_pilot.json"))
    pilot_ids_by_fam = {}
    for p in pilot["pairs"]:
        pilot_ids_by_fam.setdefault(p["family"], set()).add(p["ctp_runId"])

    fsn_index = {}
    for r in runs:
        if r["cell"] == "F-S-N" and r.get("fulltext"):
            key = (r["family"], str(r["problemId"]))
            fsn_index.setdefault(key, r)

    rng = random.Random(SEED)
    out = {"protocol": "11", "study": "Study2b-refiner", "phase": "extension",
           "seed": SEED, "pairs": []}
    for fam in FAMILIES:
        pool = [r for r in runs
                if r["cell"] == "C-T-P" and r["family"] == fam and r.get("fulltext")
                and (r["family"], str(r["problemId"])) in fsn_index]
        pool_ids = {r["runId"] for r in pool}
        ids = sorted(pool_ids - pilot_ids_by_fam.get(fam, set()))
        n_new = N_PER_FAMILY_TOTAL - len(pilot_ids_by_fam.get(fam, set()))
        assert n_new == 37, f"{fam}: expected 37 new pairs, got {n_new}"
        assert len(ids) >= n_new, f"{fam}: pool too small ({len(ids)})"
        picked = rng.sample(ids, n_new)
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
    dst = ROOT / "runs/refine_b/sample_extension.json"
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"study2b extension sample: {len(out['pairs'])} new pairs "
          f"(total will be {len(out['pairs']) + sum(len(v) for v in pilot_ids_by_fam.values())}) -> {dst}")


if __name__ == "__main__":
    main()
