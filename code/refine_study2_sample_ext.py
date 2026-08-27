#!/usr/bin/env python3
"""Protocol 09 / Study 2 — EXTENSION sample (Protocol 09 sec 8, locked).

Draws the remaining 37 C-T-P pairs per family (full pool = 57/family), seed
20260731, disjoint from the pilot's 20. Output: runs/refine/sample_extension.json
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

SEED = 20260731
FAMILIES = ["kimi", "claude", "qwen"]
N_PER_FAMILY_TOTAL = 57  # full locked pool


def main():
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    text_by_run = {r["runId"]: r for r in store["runs"]}
    meta = {r["runId"]: r for r in store["runs"] if r.get("fulltext")}
    recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    df = pd.DataFrame(am.build_run_table(recs, meta))

    pilot = json.load(open(ROOT / "runs/refine/sample_pilot.json"))
    pilot_ids = {p["ctp_runId"] for p in pilot["pairs"]}

    ctp = df[(df.tier == "C") & (df.structure == "T") & (df.persona == "P")]
    fsn = df[(df.tier == "F") & (df.structure == "S") & (df.persona == "N")]
    fsn_index = {(r.family, r.problemId): r for (_, r) in
                 fsn.sort_values("runId").drop_duplicates(
                     ["family", "problemId"], keep="first").iterrows()}

    rng = random.Random(SEED)
    out = {"protocol": "09", "study": "Study2-refiner", "phase": "extension",
           "seed": SEED, "pairs": []}
    for fam in FAMILIES:
        pool = ctp[ctp.family == fam]
        pool = pool[pool.apply(lambda r: (r.family, r.problemId) in fsn_index, axis=1)]
        ids = sorted(set(pool["runId"].tolist()) - pilot_ids)
        n_new = N_PER_FAMILY_TOTAL - 20
        assert len(ids) >= n_new, f"{fam}: pool too small ({len(ids)})"
        picked = rng.sample(ids, n_new)
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
    dst = ROOT / "runs/refine/sample_extension.json"
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"extension sample: {len(out['pairs'])} new pairs "
          f"(total will be {len(out['pairs']) + len(pilot_ids)}) -> {dst}")


if __name__ == "__main__":
    main()
