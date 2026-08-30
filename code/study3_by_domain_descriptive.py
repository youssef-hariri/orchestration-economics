#!/usr/bin/env python3
"""Study 3 descriptive family x domain breakdown (Novelty).

DESCRIPTIVE ONLY (author directive 2026-08-30): no inferential statistics at
this grain -- cells hold ~9-12 runs, underpowered by design. Means and Cohen's
d vs F-S-N are reported without p-values, for the paper's supplementary
heatmap and the DeeWaanAI routing discussion.

Outputs (D54): results/study3_by_family_domain.json +
analysis/results/study3_by_family_domain.csv +
paper figures study3_family_domain_heatmap.png
"""
import csv
import json
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "code"))
from study3_analysis import mean_judgments, cohend  # noqa: E402

DOMAIN_MAP = json.load(open(ROOT / "data/problems/domain_map.json"))["map"]
ARMS = ["D-SELF", "D-FRONT"]


def fsn_means():
    """Frozen F-S-N Novelty per (family, problem)."""
    base = defaultdict(list)
    for row in csv.DictReader(open(ROOT / "evaluation/scores_aggregated.csv")):
        if row["cell"] == "F-S-N":
            base[(row["family"], row["problem_id"])].append(float(row["novelty"]))
    return {k: sum(v) / len(v) for k, v in base.items()}


def main():
    sol = mean_judgments()  # runId -> {dim: mean}
    # cell means per (family, problem, arm) over reps
    cell = defaultdict(list)
    for line in open(ROOT / "runs/logs/study3_ledger_v2.jsonl"):
        r = json.loads(line)
        if r.get("status") != "completed":
            continue
        rid = r["key"]
        if rid in sol:
            cell[(r["family"], r["problemId"], r["arm"])].append(sol[rid]["Novelty"])
    cell = {k: sum(v) / len(v) for k, v in cell.items()}
    fsn = fsn_means()

    fams = sorted({f for f, _, _ in cell})
    doms = json.load(open(ROOT / "data/problems/domain_map.json"))["domains"]

    rows = []
    for fam in fams:
        for dom in doms:
            probs = sorted({p for (f, p, a) in cell if f == fam and DOMAIN_MAP.get(p) == dom})
            if not probs:
                continue
            f_vals = [fsn[(fam, p)] for p in probs if (fam, p) in fsn]
            row = {"family": fam, "domain": dom, "n_problems": len(probs)}
            for arm in ARMS:
                vals = [cell[(fam, p, arm)] for p in probs if (fam, p, arm) in cell]
                row[f"mean_{arm}"] = round(st.mean(vals), 3) if vals else None
                row[f"d_vs_FSN_{arm}"] = (round(cohend(vals, f_vals), 3)
                                          if vals and f_vals and len(f_vals) > 1 else None)
            row["mean_FSN"] = round(st.mean(f_vals), 3) if f_vals else None
            rows.append(row)

    (ROOT / "results").mkdir(exist_ok=True)
    json.dump({"note": "DESCRIPTIVE ONLY: family x domain Novelty means and Cohen d vs F-S-N; "
                       "cells hold 2-5 problems x 3 reps -- underpowered for inference; no p-values by design",
               "rows": rows},
              open(ROOT / "results/study3_by_family_domain.json", "w"), indent=2)
    ar = ROOT / "analysis/results"
    ar.mkdir(parents=True, exist_ok=True)
    with open(ar / "study3_by_family_domain.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # --- heatmap: d vs F-S-N, family x domain, D-SELF | D-FRONT side by side
    sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
    from daimon_runtime import setup_plot
    setup_plot()
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns

    def grid(arm):
        g = np.full((len(doms), len(fams)), np.nan)
        for r in rows:
            v = r[f"d_vs_FSN_{arm}"]
            if v is not None:
                g[doms.index(r["domain"]), fams.index(r["family"])] = v
        return g

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    kw = dict(cmap="RdYlGn", center=0, vmin=-1.2, vmax=1.2, annot=True, fmt=".2f",
              xticklabels=[f.capitalize() for f in fams],
              yticklabels=[d.replace("_", "\n") for d in doms], cbar_kws={"label": "Cohen's d vs F-S-N (Novelty)"})
    for ax, arm in zip(axes, ARMS):
        sns.heatmap(grid(arm), ax=ax, **kw, cbar=arm == "D-FRONT")
        ax.set_title(f"{arm} (cheap-executed pipeline vs frontier solo)")
    fig.suptitle("Study 3 — descriptive family × domain effect on Novelty (no inference: 2–5 problems/cell)",
                 fontsize=11)
    out = ROOT / "paper/FULL-PAPER-DRAFT-BUSINESS-v12_with_figures/fig23_study3_family_domain.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    print("saved", out)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
