#!/usr/bin/env python3
"""G0 gate report (D31/D32.4) — computed from pilot generation + judgments.

Inputs : runs/logs/pilot_gen_2026-07-31.json  (generation, incl. full outputs)
         runs/logs/pilot_judgments.jsonl      (9 scores per solution)
Outputs: runs/logs/pilot_g0_report.json + console summary.

G0a  empty-output rate per cell (status != completed OR empty final response)
G0b  judge reliability: Fleiss kappa on Novelty (median-across-variants per
     judge -> 3 raters, 5 categories), all dimensions reported; ICC(2,k)
     across the 9 judge-variant score columns for Novelty
G0c  cost vs section 4.4 envelope: per-run upper-bound cost = totalTokens x
     output price (input/output split unavailable in run_status; upper bound
     is conservative), projected to the main-run call counts from the 4.4
     budget table; fail at >1.5x the table's upper estimates
D32.5 special-arm family selection (applied, logged; frozen rule)
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent.parent
GEN_LOG = ROOT / "runs/logs/pilot_gen_2026-07-31.json"
JUDG = ROOT / "runs/logs/pilot_judgments.jsonl"
REGISTRY = ROOT / "pipelines/fixed/fixed_pipelines_registry.json"
OUT = ROOT / "runs/logs/pilot_g0_report.json"

KAPPA_THRESHOLD = 0.40
EMPTY_RATE_THRESHOLD = 0.05
COST_TOLERANCE = 1.5
# Section 4.4 budget table: calls and upper cost estimates (generation only).
MAIN_CHEAP_CALLS, MAIN_CHEAP_USD_HI = 4740, 17.0
MAIN_FSOLO_CALLS, MAIN_FSOLO_USD_HI = 600, 16.0

gen = json.load(open(GEN_LOG))
registry = json.load(open(REGISTRY))
prices = json.load(open(ROOT / "config/price_vector.json"))["prices"]

model_by_project = {
    e["projectId"]: e["definition"]["steps"][0]["model"] for e in registry["created"]
}

# ---------- G0a: empty-output rate per cell ----------
by_cell = defaultdict(list)
for r in gen["results"]:
    ok = r.get("status") == "completed" and bool((r.get("finalResponse") or "").strip())
    by_cell[(r["family"], r["cell"])].append(ok)

g0a = {}
worst_rate = 0.0
for (fam, cell), oks in sorted(by_cell.items()):
    rate = 1 - sum(oks) / len(oks)
    worst_rate = max(worst_rate, rate)
    g0a[f"{fam}/{cell}"] = {"runs": len(oks), "empty_or_failed": len(oks) - sum(oks), "rate": round(rate, 3)}
g0a_pass = worst_rate <= EMPTY_RATE_THRESHOLD

# ---------- G0b: judge reliability ----------
def fleiss_kappa(items):
    """items: list of per-item category-count lists (categories 1..5)."""
    items = [c for c in items if sum(c) > 0]
    n_raters = sum(items[0])
    if any(sum(c) != n_raters for c in items):
        raise ValueError("unequal rater counts")
    N = len(items)
    p_cat = [sum(c[k] for c in items) / (N * n_raters) for k in range(5)]
    P_i = [(sum(x * x for x in c) - n_raters) / (n_raters * (n_raters - 1)) for c in items]
    P_bar = mean(P_i)
    P_e = sum(p * p for p in p_cat)
    return (P_bar - P_e) / (1 - P_e) if P_e < 1 else float("nan")


def icc2k(matrix):
    """ICC(2,k) two-way random, average measures. matrix: items x raters."""
    n = len(matrix)
    k = len(matrix[0])
    grand = mean(v for row in matrix for v in row)
    row_means = [mean(r) for r in matrix]
    col_means = [mean(col) for col in zip(*matrix)]
    ss_tot = sum((v - grand) ** 2 for row in matrix for v in row)
    ss_r = k * sum((m - grand) ** 2 for m in row_means)
    ss_c = n * sum((m - grand) ** 2 for m in col_means)
    ss_e = ss_tot - ss_r - ss_c
    ms_r = ss_r / (n - 1)
    ms_c = ss_c / (k - 1)
    ms_e = ss_e / ((n - 1) * (k - 1))
    return (ms_r - ms_e) / (ms_r + (ms_c - ms_e) / n)


DIMENSIONS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]
g0b = {"available": JUDG.exists()}
if JUDG.exists():
    judgments = [json.loads(l) for l in open(JUDG) if l.strip()]
    ok_j = [j for j in judgments if "scores" in j]
    g0b["calls_total"] = len(judgments)
    g0b["calls_failed"] = len(judgments) - len(ok_j)
    # per (runId, judge): median across variants, per dimension
    per_rj = defaultdict(lambda: defaultdict(list))
    for j in ok_j:
        for d, v in j["scores"].items():
            if v is not None:
                per_rj[(j["runId"], j["judge_family"])][d].append(v)
    judges = sorted({j["judge_family"] for j in ok_j})
    kappas, parse = {}, {}
    for d in DIMENSIONS:
        counts, n_scored, n_expected = [], 0, 0
        for run_id in {j["runId"] for j in ok_j}:
            cats = [0] * 5
            complete = True
            for jf in judges:
                vals = per_rj.get((run_id, jf), {}).get(d, [])
                n_expected += 3
                n_scored += len(vals)
                if vals:
                    m = int(round(median(vals)))
                    cats[min(max(m, 1), 5) - 1] += 1
                else:
                    complete = False
            if complete:
                counts.append(cats)
        kappas[d] = round(fleiss_kappa(counts), 3) if counts else None
        parse[d] = round(n_scored / n_expected, 3) if n_expected else None
    g0b["fleiss_kappa_median_across_variants"] = kappas
    g0b["parse_rate_by_dimension"] = parse
    # ICC(2,k) for Novelty across 9 judge-variant columns
    cols = [(jf, v) for jf in judges for v in ("var1", "var2", "var3")]
    cell_scores = {}
    for j in ok_j:
        v = j["scores"].get("Novelty")
        if v is not None:
            cell_scores[(j["runId"], j["judge_family"], j["variant"])] = v
    mat = []
    for run_id in sorted({j["runId"] for j in ok_j}):
        row = [cell_scores.get((run_id, jf, v)) for jf, v in cols]
        if all(x is not None for x in row):
            mat.append(row)
    g0b["icc2k_novelty_9cols"] = round(icc2k(mat), 3) if len(mat) > 1 else None
    g0b["icc_items_complete"] = len(mat)
    g0b["kappa_pass"] = (kappas.get("Novelty") or -1) >= KAPPA_THRESHOLD

# ---------- G0c: cost vs envelope ----------
def run_cost_usd(r):
    model = model_by_project[r["projectId"]]
    tok = r.get("totalTokensUsed") or 0
    return tok * prices[model]["output"] / 1e6  # upper bound (all-at-output-price)


cheap_costs, fsolo_costs = [], []
cell_cost = defaultdict(list)
for r in gen["results"]:
    if r.get("status") != "completed":
        continue
    c = run_cost_usd(r)
    cell_cost[f"{r['family']}/{r['cell']}"].append(c)
    (cheap_costs if r["cell"].startswith("C-") else fsolo_costs).append(c)

proj_cheap = mean(cheap_costs) * MAIN_CHEAP_CALLS if cheap_costs else None
proj_fsolo = mean(fsolo_costs) * MAIN_FSOLO_CALLS if fsolo_costs else None
g0c = {
    "method": "upper bound: totalTokens x output price (no input/output split in run_status)",
    "mean_cost_per_cheap_run_usd": round(mean(cheap_costs), 4) if cheap_costs else None,
    "mean_cost_per_frontier_solo_run_usd": round(mean(fsolo_costs), 4) if fsolo_costs else None,
    "per_cell_mean_usd": {k: round(mean(v), 4) for k, v in sorted(cell_cost.items())},
    "projected_main_cheap_usd": round(proj_cheap, 2) if proj_cheap else None,
    "projected_main_frontier_solo_usd": round(proj_fsolo, 2) if proj_fsolo else None,
    "envelope_cheap_usd_hi_x1.5": MAIN_CHEAP_USD_HI * COST_TOLERANCE,
    "envelope_frontier_solo_usd_hi_x1.5": MAIN_FSOLO_USD_HI * COST_TOLERANCE,
}
g0c["pass"] = (
    proj_cheap is not None and proj_fsolo is not None
    and proj_cheap <= MAIN_CHEAP_USD_HI * COST_TOLERANCE
    and proj_fsolo <= MAIN_FSOLO_USD_HI * COST_TOLERANCE
)

# ---------- D32.5: special-arm family selection ----------
fam_stats = {}
for fam in sorted({r["family"] for r in gen["results"]}):
    runs = [r for r in gen["results"] if r["family"] == fam]
    complete = all(
        r.get("status") == "completed" and (r.get("finalResponse") or "").strip() for r in runs
    )
    team = [r for r in runs if r["cell"] in ("C-T-N", "C-T-P") and r.get("status") == "completed"]
    fam_stats[fam] = {
        "all_6_cells_complete": complete,
        "mean_team_cost_usd": round(mean(run_cost_usd(r) for r in team), 4) if team else None,
        "mean_team_latency_ms": round(mean(r["totalLatencyMs"] for r in team if r.get("totalLatencyMs"))) if team else None,
    }
eligible = {f: s for f, s in fam_stats.items() if s["all_6_cells_complete"] and s["mean_team_cost_usd"] is not None}
special_family = None
if eligible:
    special_family = min(
        eligible.items(), key=lambda kv: (kv[1]["mean_team_cost_usd"], kv[1]["mean_team_latency_ms"])
    )[0]

report = {
    "generated_from": {"gen_log": GEN_LOG.name, "judgments": JUDG.name if JUDG.exists() else None},
    "G0a_empty_output": {"per_cell": g0a, "worst_rate": round(worst_rate, 3),
                         "threshold": EMPTY_RATE_THRESHOLD, "pass": g0a_pass},
    "G0b_judge_reliability": g0b,
    "G0c_cost_envelope": g0c,
    "D32_5_special_arm_family": {"per_family": fam_stats, "selected": special_family},
}
OUT.write_text(json.dumps(report, indent=2) + "\n")

print(f"G0a empty-output: worst cell rate {worst_rate:.1%} (<= {EMPTY_RATE_THRESHOLD:.0%}) -> {'PASS' if g0a_pass else 'FAIL'}")
if g0b.get("available"):
    print(f"G0b Fleiss kappa: {g0b['fleiss_kappa_median_across_variants']}")
    print(f"    Novelty kappa >= {KAPPA_THRESHOLD} -> {'PASS' if g0b.get('kappa_pass') else 'FAIL'}; ICC(2,k) Novelty = {g0b.get('icc2k_novelty_9cols')}")
else:
    print("G0b: judgments not yet available")
print(f"G0c projected: cheap ${g0c['projected_main_cheap_usd']} (cap ${g0c['envelope_cheap_usd_hi_x1.5']}), "
      f"F-solo ${g0c['projected_main_frontier_solo_usd']} (cap ${g0c['envelope_frontier_solo_usd_hi_x1.5']}) -> {'PASS' if g0c['pass'] else 'FAIL'}")
print(f"D32.5 special-arm family -> {special_family}")
print(f"report -> {OUT}")
sys.exit(0)
