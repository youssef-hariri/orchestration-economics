#!/usr/bin/env python3
"""POST-HOC ROBUSTNESS CHECK — NOT part of the frozen pre-registered analysis.

Why: Protocol 13's markdown (protocols/13-...md §4 H-D1 / §6 "LMM composite ~ arm")
named the COMPOSITE as the Study 3 primary outcome, but the frozen analysis
(code/study3_analysis.py) and every reported table/figure use NOVELTY. This script
re-runs Contrast A (D-FRONT vs D-SELF) on the COMPOSITE (mean of the 5 scored
dimensions) with the IDENTICAL method reused from study3_analysis.py — paired within
family x problem, normal-approx p from the paired t, Cohen's d, Holm across families —
to test whether the "authorship barely matters" conclusion is invariant to the DV choice.

Integrity constraints:
  * Imports and reuses the frozen functions from study3_analysis.py (no re-implementation).
  * Writes ONLY new files (results/study3_composite_robustness.json,
    analysis/results/study3_contrast_a_composite.csv).
  * Does NOT modify study3_analysis.py or study3_results.json.
  * No API calls / no new generation — re-analyzes stored judgments only.
"""
import csv
import json
import statistics as st
from collections import defaultdict

import study3_analysis as S  # reuse the EXACT frozen method

ROOT = S.ROOT
DIMS = S.DIMS  # ["Novelty","Usefulness","Flexibility","Elaboration","Cultural Sensitivity"]


def main():
    sol = S.mean_judgments()  # per-solution mean of the 9 judgments, per dimension

    # rep-aware per-(family, problem, arm) COMPOSITE = mean of the 5 dimensions
    cellrep = defaultdict(lambda: defaultdict(list))  # (fam,pid)[arm] -> [composite per rep]
    for rid, dims in sol.items():
        arm, fam, pid, rep = rid.split("__")
        comp = sum(dims[d] for d in DIMS) / len(DIMS)
        cellrep[(fam, pid)][arm].append(comp)
    cellavg = {k: {a: sum(v) / len(v) for a, v in arms.items()} for k, arms in cellrep.items()}

    fams = sorted({f for f, _ in cellrep})
    rows, pvals = [], []
    for f in fams:
        probs = sorted({p for ff, p in cellrep if ff == f})
        paired = [p for p in probs if "D-FRONT" in cellavg[(f, p)] and "D-SELF" in cellavg[(f, p)]]
        df = [cellavg[(f, p)]["D-FRONT"] for p in paired]
        ds = [cellavg[(f, p)]["D-SELF"] for p in paired]
        diffs = [a - b for a, b in zip(df, ds)]
        t = S.paired_t(diffs)
        p = 2 * (1 - S.norm_cdf(abs(t["t"]))) if t and t.get("t") is not None else 1.0
        pvals.append(p)
        rows.append({"family": f, **{k: v for k, v in (t or {}).items()},
                     "p_raw": round(p, 4), "d": round(S.cohend(df, ds) or 0, 3)})
    adj = S.holm(pvals)
    for r, a in zip(rows, adj):
        r["p_holm"] = a

    # pooled composite arm means (compare to Novelty pooled 4.03 vs 3.99)
    pool = defaultdict(list)
    for (f, p), arms in cellavg.items():
        for a, v in arms.items():
            pool[a].append(v)
    pooled = {a: round(st.mean(v), 3) for a, v in pool.items()}

    out = {
        "study": "study3_composite_robustness",
        "role": "POST-HOC robustness check on the composite DV (registered in Protocol 13 markdown); "
                "method identical to study3_analysis.py Contrast A; not a new confirmatory analysis",
        "composite_definition": "mean of " + ", ".join(DIMS),
        "primary_contrast_A_DFRONT_vs_DSELF_composite": rows,
        "pooled_composite_arm_means": pooled,
    }
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results/study3_composite_robustness.json", "w"), indent=2)
    ar = ROOT / "analysis/results"
    ar.mkdir(parents=True, exist_ok=True)
    with open(ar / "study3_contrast_a_composite.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # side-by-side vs the frozen Novelty result
    nov = {}
    try:
        nr = json.load(open(ROOT / "results/study3_results.json"))
        for r in nr.get("primary_contrast_A_DFRONT_vs_DSELF_novelty", []):
            nov[r["family"]] = r
    except Exception as e:
        print("  (could not load novelty results for comparison:", e, ")")

    print("\n=== Study 3 Contrast A (D-FRONT vs D-SELF): Novelty vs Composite ===")
    print(f"{'family':10s} {'nov_d':>7s} {'nov_pH':>8s} | {'comp_d':>7s} {'comp_pH':>8s} {'n':>4s}")
    for r in rows:
        n = nov.get(r["family"], {})
        print(f"{r['family']:10s} {str(n.get('d','-')):>7s} {str(n.get('p_holm','-')):>8s} | "
              f"{r['d']:>7.3f} {r['p_holm']:>8.4f} {r.get('n','-'):>4}")
    print("\npooled composite arm means:", pooled)
    nsig_comp = sum(1 for r in rows if r["p_holm"] < 0.05)
    nsig_nov = sum(1 for r in nov.values() if isinstance(r.get("p_holm"), (int, float)) and r["p_holm"] < 0.05)
    print(f"families with p_holm<0.05 -> Novelty: {nsig_nov}/5 | Composite: {nsig_comp}/5")


if __name__ == "__main__":
    main()
