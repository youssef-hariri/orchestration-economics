#!/usr/bin/env python3
"""Protocol 09 / Study 2 — pilot sample (locked, seed 20260730).

Randomly selects 20 C-T-P runs per family (kimi, claude, qwen) from the LOCKED
Study-1 data; each is paired with the same-problem same-family F-S-N run.
Random (not top-scoring) sampling avoids regression-to-mean and cherry-picking.
Output: runs/refine/sample_pilot.json
"""
import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import analyze_main as am  # noqa: E402
import judge_v2 as jv      # noqa: E402

SEED = 20260730
FAMILIES = ["kimi", "claude", "qwen"]
N_PER_FAMILY = 20


def main():
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    text_by_run = {r["runId"]: r for r in store["runs"]}
    meta = {r["runId"]: r for r in store["runs"] if r.get("fulltext")}
    recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    df = pd.DataFrame(am.build_run_table(recs, meta))

    ctp = df[(df.tier == "C") & (df.structure == "T") & (df.persona == "P")]
    fsn = df[(df.tier == "F") & (df.structure == "S") & (df.persona == "N")]
    fsn_index = {(r.family, r.problemId): r for (_, r) in
                 fsn.sort_values("runId").drop_duplicates(
                     ["family", "problemId"], keep="first").iterrows()}

    rng = random.Random(SEED)
    out = {"protocol": "09", "study": "Study2-refiner", "phase": "pilot",
           "seed": SEED, "n_per_family": N_PER_FAMILY, "pairs": []}
    for fam in FAMILIES:
        pool = ctp[ctp.family == fam]
        pool = pool[pool.apply(lambda r: (r.family, r.problemId) in fsn_index, axis=1)]
        ids = sorted(pool["runId"].tolist())
        picked = rng.sample(ids, N_PER_FAMILY)
        for rid in sorted(picked):
            row = pool[pool.runId == rid].iloc[0]
            mate = fsn_index[(fam, row["problemId"])]
            prob = jv.problems.get(row["problemId"])
            out["pairs"].append({
                "ctp_runId": int(rid),
                "fsn_runId": int(mate["runId"]),
                "family": fam,
                "problemId": str(row["problemId"]),
                "ctp_composite_audit": round(float(row["composite"]), 4),
                "fsn_composite_audit": round(float(mate["composite"]), 4),
                "problem_text": f"{prob['background_context']}\n\n{prob['business_problem']}",
                "ctp_fulltext": text_by_run[rid]["fulltext"],
            })
    dst = ROOT / "runs/refine/sample_pilot.json"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"pilot sample: {len(out['pairs'])} pairs -> {dst}")
    print(pd.DataFrame([{"ctp": p["ctp_runId"], "fsn": p["fsn_runId"], "family": p["family"],
                         "problem": p["problemId"]} for p in out["pairs"]]).to_string(index=False))


if __name__ == "__main__":
    main()
