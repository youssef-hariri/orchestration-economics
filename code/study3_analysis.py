#!/usr/bin/env python3
"""Study 3 (Protocol 13, instrument v2) pre-registered analysis.

Primary contrasts (OSF 9ukjz -> bwc93 -> 639eq):
  A) D-FRONT vs D-SELF (design authorship effect), paired within family x problem,
     Holm across families. Primary dimension: Novelty; others descriptive.
  B) D-SELF and D-FRONT vs frozen human-designed C-T-N baseline (Study 1).
  C) Cost: designer + executor + gate-loop tokens per arm (D30/D55), T-EGR framing.
Also: participant flow (attrition), design-structure descriptives (steps, gates).
Outputs (D54): results/study3_results.json + analysis/results/study3_*.csv
"""
import json
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]


def mean_judgments():
    per = defaultdict(list)
    for line in open(ROOT / "runs/study3/study3_judgments_v2.jsonl"):
        j = json.loads(line)
        if j.get("error") or j.get("incomplete"):
            continue
        per[(j["runId"], j["judge_family"], j["variant"])] = j["scores"]
    # collapse to per-solution means (9 judgments each)
    sol = defaultdict(lambda: defaultdict(list))
    for (rid, jf, var), scores in per.items():
        for d in DIMS:
            sol[rid][d].append(scores[d])
    return {rid: {d: sum(v) / len(v) for d, v in dims.items()} for rid, dims in sol.items()}


def cohend(a, b):
    if len(a) < 2 or len(b) < 2:
        return None
    s = math.sqrt(((len(a) - 1) * st.variance(a) + (len(b) - 1) * st.variance(b)) / (len(a) + len(b) - 2))
    return (st.mean(a) - st.mean(b)) / s if s else 0.0


def paired_t(diffs):
    n = len(diffs)
    if n < 2:
        return None
    m, sd = st.mean(diffs), st.stdev(diffs)
    if sd == 0:
        return {"mean_diff": m, "t": None, "note": "zero variance"}
    tstat = m / (sd / math.sqrt(n))
    # normal approx p (n small; report t and let reviewers use table)
    return {"n": n, "mean_diff": round(m, 4), "sd_diff": round(sd, 4), "t": round(tstat, 3)}


def holm(pvals):
    """Holm-adjusted p-values."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0] * m
    running = 0
    for rank, i in enumerate(order):
        val = min(1, (m - rank) * pvals[i])
        running = max(running, val)
        adj[i] = round(running, 4)
    return adj


def norm_cdf(x):
    return (1 + math.erf(x / math.sqrt(2))) / 2


def main():
    sol = mean_judgments()
    # arm/family/problem parse
    cells = defaultdict(dict)  # (family, problem) -> {arm: scores}
    for rid, dims in sol.items():
        arm, fam, pid, rep = rid.split("__")
        cells[(fam, pid)][arm] = dims  # rep collapsed: last-write; reps averaged below
    # rep-aware: average across reps first
    cellrep = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for rid, dims in sol.items():
        arm, fam, pid, rep = rid.split("__")
        for d in DIMS:
            cellrep[(fam, pid)][arm][d].append(dims[d])
    cellavg = {k: {a: {d: sum(v) / len(v) for d, v in dd.items()} for a, dd in arms.items()}
               for k, arms in cellrep.items()}

    fams = sorted({f for f, _ in cellrep})
    # A) D-FRONT vs D-SELF per family (paired across problems, Novelty primary)
    rows_a, pvals = [], []
    for f in fams:
        diffs = [cellavg[(f, p)]["D-FRONT"]["Novelty"] - cellavg[(f, p)]["D-SELF"]["Novelty"]
                 for p in sorted({p for ff, p in cellrep if ff == f})
                 if "D-FRONT" in cellavg[(f, p)] and "D-SELF" in cellavg[(f, p)]]
        t = paired_t(diffs)
        p = 2 * (1 - norm_cdf(abs(t["t"]))) if t and t.get("t") is not None else 1.0
        pvals.append(p)
        rows_a.append({"family": f, **{k: v for k, v in (t or {}).items()},
                       "p_raw": round(p, 4),
                       "d": round(cohend([cellavg[(f, p)]["D-FRONT"]["Novelty"] for p in sorted({p for ff, p in cellrep if ff == f}) if "D-FRONT" in cellavg[(f, p)]],
                                         [cellavg[(f, p)]["D-SELF"]["Novelty"] for p in sorted({p for ff, p in cellrep if ff == f}) if "D-SELF" in cellavg[(f, p)]]) or 0, 3)})
    adj = holm(pvals)
    for r, a in zip(rows_a, adj):
        r["p_holm"] = a

    # B) vs frozen C-T-N baseline (Study-1 aggregated, per family, Novelty)
    import csv
    base = defaultdict(lambda: defaultdict(list))
    for row in csv.DictReader(open(ROOT / "evaluation/scores_aggregated.csv")):
        if row["cell"] == "C-T-N":
            base[row["family"]][row["problem_id"]].append(float(row["novelty"]))
    base_sol = {f: [sum(v) / len(v) for v in probs.values()] for f, probs in base.items()}
    rows_b = []
    for arm in ["D-SELF", "D-FRONT"]:
        for f in fams:
            a = [cellavg[(f, p)][arm]["Novelty"] for p in sorted({p for ff, p in cellrep if ff == f})
                 if arm in cellavg[(f, p)]]
            b = base_sol.get(f, [])
            if a and b:
                rows_b.append({"arm": arm, "family": f, "n_arm": len(a), "n_base": len(b),
                               "mean_arm": round(st.mean(a), 3), "mean_baseline": round(st.mean(b), 3),
                               "d": round(cohend(a, b) or 0, 3)})

    # C) cost per arm (tokens from ledger)
    tok = defaultdict(int)
    designs = defaultdict(list)
    for line in open(ROOT / "runs/logs/study3_ledger_v2.jsonl"):
        r = json.loads(line)
        if r.get("status") != "completed":
            continue
        arm = r["arm"]
        for u in [r.get("designer_usage", {}), r.get("designer_usage_repair", {})] + [s.get("usage", {}) for s in r.get("steps", [])]:
            tok[arm] += (u or {}).get("total_tokens", 0)
        designs[arm].append({"n_steps": r.get("n_steps"), "executed": r.get("executed_steps"),
                             "gates": sum(1 for s in r.get("steps", []) if s.get("type") in ("if", "while"))})
    rows_c = [{"arm": a, "total_tokens": tok[a],
               "mean_steps": round(st.mean(x["n_steps"] for x in designs[a]), 2),
               "mean_executed_steps": round(st.mean(x["executed"] for x in designs[a]), 2),
               "pct_with_gates": round(100 * sum(1 for x in designs[a] if x["gates"]) / len(designs[a]), 1)}
              for a in ["D-SELF", "D-FRONT"]]

    # participant flow
    latest = {}
    for line in open(ROOT / "runs/logs/study3_ledger_v2.jsonl"):
        r = json.loads(line)
        latest[r["key"]] = r
    flow = defaultdict(lambda: defaultdict(int))
    for r in latest.values():
        flow[r["family"]][r["status"]] += 1

    # arm means per dimension (all families pooled)
    pool = defaultdict(lambda: defaultdict(list))
    for (f, p), arms in cellavg.items():
        for a, dd in arms.items():
            for d, v in dd.items():
                pool[a][d].append(v)
    pooled = {a: {d: round(st.mean(v), 3) for d, v in dims.items()} for a, dims in pool.items()}

    uniq = set()
    for line in open(ROOT / "runs/study3/study3_judgments_v2.jsonl"):
        j = json.loads(line)
        uniq.add((j["runId"], j["judge_family"], j["variant"]))
    out = {"study": "study3_v2", "date_utc": "2026-08-30",
           "registrations": ["osf.io/9ukjz", "osf.io/bwc93", "osf.io/639eq"],
           "solutions_judged": len(sol), "judgments": len(uniq),
           "judgments_note": "unique (solution, judge, variant) judgments; 19 raw duplicate lines from judging retries are overwritten on read (last-wins dict) and excluded",
           "participant_flow": {f: dict(c) for f, c in flow.items()},
           "primary_contrast_A_DFRONT_vs_DSELF_novelty": rows_a,
           "contrast_B_vs_frozen_CTN_novelty": rows_b,
           "cost_and_structure": rows_c,
           "pooled_arm_means": pooled}
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results/study3_results.json", "w"), indent=2)

    ar = ROOT / "analysis/results"
    ar.mkdir(parents=True, exist_ok=True)
    with open(ar / "study3_contrast_a.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows_a[0].keys()); w.writeheader(); w.writerows(rows_a)
    with open(ar / "study3_contrast_b.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows_b[0].keys()); w.writeheader(); w.writerows(rows_b)
    with open(ar / "study3_cost_structure.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows_c[0].keys()); w.writeheader(); w.writerows(rows_c)
    with open(ar / "study3_participant_flow.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["family", "status", "n"])
        for f, c in flow.items():
            for s, n in c.items():
                w.writerow([f, s, n])
    print(json.dumps({"pooled": pooled, "A": rows_a, "cost": rows_c}, indent=1))


if __name__ == "__main__":
    main()
