#!/usr/bin/env python3
"""Amendment A4 — Wave 1 purposive sample from the LOCKED interim-2 data.

Groups (A4 sec 3):
  W1a persona-team winners : top composite C-T-P, 2 per family (10)
  W1b frontier baseline    : top composite F-S-N, 2 per family (10)
  W1c non-responder probe  : gpt + gemini C-T-P nearest family median (5 + 5)

Read-only. Composite scores stay in this file for audit only; qual_a4_code.py
never passes scores or cell labels to coders (blinding, A4 sec 2).
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import analyze_main as am      # noqa: E402
import judge_v2 as jv          # noqa: E402  (problem bank)


def main():
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    text_by_run = {r["runId"]: r for r in store["runs"]}
    meta = {r["runId"]: r for r in store["runs"] if r.get("fulltext")}
    recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    df = pd.DataFrame(am.build_run_table(recs, meta))

    picks = []

    def take(sub, group, n_per_family):
        for fam, g in sub.groupby("family"):
            top = g.sort_values(["composite", "runId"], ascending=[False, True]).head(n_per_family)
            for _, r in top.iterrows():
                picks.append((r["runId"], group))

    # W1a: persona-team winners
    take(df[(df.tier == "C") & (df.structure == "T") & (df.persona == "P")], "W1a", 2)
    # W1b: frontier baseline
    take(df[(df.tier == "F") & (df.structure == "S") & (df.persona == "N")], "W1b", 2)
    # W1c: gpt + gemini C-T-P nearest family median
    ctp = df[(df.tier == "C") & (df.structure == "T") & (df.persona == "P")]
    for fam in ("gpt", "gemini"):
        g = ctp[ctp.family == fam]
        med = g["composite"].median()
        near = g.assign(dist=(g["composite"] - med).abs()).sort_values(
            ["dist", "runId"]).head(5)
        for _, r in near.iterrows():
            picks.append((r["runId"], "W1c"))

    out = {"wave": 1, "amendment": "A4", "n": len(picks), "runs": []}
    for runId, group in picks:
        row = df[df.runId == runId].iloc[0]
        entry = text_by_run[runId]
        prob = jv.problems.get(row["problemId"])
        out["runs"].append({
            "runId": runId, "group": group,
            "family": row["family"], "tier": row["tier"],
            "structure": row["structure"], "persona": row["persona"],
            "problemId": row["problemId"],
            "composite": round(float(row["composite"]), 4),  # audit only
            "problem_text": f"{prob['background_context']}\n\n{prob['business_problem']}",
            "fulltext": entry["fulltext"],
        })
    dst = ROOT / "runs/qual/sample_wave1.json"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"wave1 sample: {len(picks)} runs -> {dst}")
    print(pd.DataFrame([{"runId": r["runId"], "group": r["group"], "family": r["family"],
                         "cell": r["tier"] + r["structure"] + r["persona"],
                         "composite": r["composite"]} for r in out["runs"]]).to_string(index=False))


if __name__ == "__main__":
    main()
