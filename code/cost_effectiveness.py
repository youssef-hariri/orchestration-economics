#!/usr/bin/env python3
"""Protocol 04 + Amendment A — cost-effectiveness frontier.

Locked rules (Amendment A, registered before computation):
- cost(run) = tokensUsed x blend(phi)/1e6, blend = phi*p_out + (1-phi)*p_in,
  frozen config/price_vector.json; primary phi=0.5, sensitivity {0.25, 0.75}.
- family->model from config/model_registry.json generators (C=cheap, F=frontier).
- quality = judge composite; T-EGR per D15 within-family vs F-S-N.
- refined C-T-P cost = original run cost + refine-call cost (real splits,
  deepseek-chat pricing). Judge cost excluded.
Outputs under results/cost/: cost_per_run.csv, cell_summary.csv,
pareto_frontier.csv, t_egr.json, cost_effectiveness_scatter.png/.pdf.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import analyze_main as am            # noqa: E402
import refine_study2_analyze as ra   # noqa: E402

PHIS = [0.25, 0.50, 0.75]
PHI_PRIMARY = 0.50
FAMS = ["kimi", "claude", "qwen", "gpt", "gemini"]
CELLS = ["C-S-N", "C-S-P", "C-T-N", "C-T-P", "F-S-N", "F-S-P", "F-T-N", "F-T-P"]
REFINE_PRICE = {"input": 0.14, "output": 0.28}  # deepseek-chat = v4-flash (registry)


def blend(prices, phi):
    return phi * prices["output"] + (1 - phi) * prices["input"]


def main():
    prices = json.load(open(ROOT / "config/price_vector.json"))["prices"]
    reg = json.load(open(ROOT / "config/model_registry.json"))["generators"]
    model_of = {}
    for fam, g in reg.items():
        model_of[(fam, "cheap")] = g["cheap_sibling"]["model"]
        model_of[(fam, "frontier")] = g["frontier"]["model"]

    ledger = json.load(open(ROOT / "runs/logs/main_run_ledger.json"))["results"]

    # ---- quality per run
    main_recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    qrows = ra.agg(main_recs)

    # ---- per-run cost table
    rows = []
    for r in ledger:
        if r["status"] != "completed":
            continue
        tier = "cheap" if r["tier"] == "cheap" else "frontier"
        model = model_of[(r["family"], tier)]
        p = prices[model]
        toks = r["totalTokensUsed"]
        q = qrows.get(r["runId"])
        row = {"runId": r["runId"], "cell": r["cell"], "family": r["family"],
               "model": model, "tokens": toks,
               "composite": q["composite"] if q else None,
               "novelty": q.get("Novelty") if q else None}
        for phi in PHIS:
            row[f"cost_{int(phi * 100)}"] = toks * blend(p, phi) / 1e6
        rows.append(row)
    rows = [x for x in rows if x["composite"] is not None]

    outdir = ROOT / "results/cost"
    outdir.mkdir(exist_ok=True)
    with open(outdir / "cost_per_run.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for x in rows:
            w.writerow(x)

    # ---- cell summary (primary phi) + sensitivity
    def cell_table(phi):
        key = f"cost_{int(phi * 100)}"
        tab = {}
        for c in CELLS:
            sel = [x for x in rows if x["cell"] == c]
            costs = np.array([x[key] for x in sel])
            quals = np.array([x["composite"] for x in sel])
            tab[c] = {"n": len(sel), "mean_cost": costs.mean(), "sd_cost": costs.std(ddof=1),
                      "mean_quality": quals.mean(), "sd_quality": quals.std(ddof=1),
                      "mean_tokens": np.mean([x["tokens"] for x in sel])}
        return tab

    tab50 = cell_table(PHI_PRIMARY)
    with open(outdir / "cell_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "n", "phi", "mean_cost_usd", "sd_cost", "mean_quality",
                    "sd_quality", "mean_tokens"])
        for phi in PHIS:
            t = cell_table(phi)
            for c in CELLS:
                v = t[c]
                w.writerow([c, v["n"], phi, round(v["mean_cost"], 6), round(v["sd_cost"], 6),
                            round(v["mean_quality"], 4), round(v["sd_quality"], 4),
                            round(v["mean_tokens"])])

    # ---- Pareto per phi (dominance: lower cost AND higher quality)
    def pareto(tab):
        pts = [(c, tab[c]["mean_cost"], tab[c]["mean_quality"]) for c in CELLS]
        front = []
        for c, mc, mq in pts:
            dominated = any(oc != c and oc_cost <= mc and oc_q >= mq
                            and (oc_cost < mc or oc_q > mq)
                            for oc, oc_cost, oc_q in pts)
            if not dominated:
                front.append(c)
        return sorted(front, key=lambda c: tab[c]["mean_cost"])

    fronts = {phi: pareto(cell_table(phi)) for phi in PHIS}
    stable = sorted(set.intersection(*[set(v) for v in fronts.values()]))
    with open(outdir / "pareto_frontier.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["phi", "pareto_cells"])
        for phi in PHIS:
            w.writerow([phi, ";".join(fronts[phi])])
        w.writerow(["stable_all_phi", ";".join(stable)])

    # ---- ICER vs cheapest cell (primary phi)
    cheapest = min(CELLS, key=lambda c: tab50[c]["mean_cost"])
    icers = {}
    for c in CELLS:
        dc = tab50[c]["mean_cost"] - tab50[cheapest]["mean_cost"]
        dq = tab50[c]["mean_quality"] - tab50[cheapest]["mean_quality"]
        icers[c] = {"d_cost": round(dc, 6), "d_quality": round(dq, 4),
                    "icer": round(dc / dq, 4) if dq > 1e-9 else None}

    # ---- T-EGR per D15 within family
    teg = {}
    for fam in FAMS:
        fr = [x for x in rows if x["family"] == fam]
        base = [x for x in fr if x["cell"] == "F-S-N"]
        if not base:
            continue
        bn = np.mean([x["novelty"] for x in base if x["novelty"] is not None])
        bc = np.mean([x[f"cost_{int(PHI_PRIMARY * 100)}"] for x in base])
        for c in CELLS:
            if c == "F-S-N":
                continue
            sel = [x for x in fr if x["cell"] == c]
            nov = np.mean([x["novelty"] for x in sel if x["novelty"] is not None])
            cost = np.mean([x[f"cost_{int(PHI_PRIMARY * 100)}"] for x in sel])
            teg.setdefault(c, []).append((nov / bn) / (cost / bc))
    t_egr = {c: round(float(np.mean(v)), 3) for c, v in teg.items()}

    # ---- Study 2 extension: refined C-T-P points
    refined_pts = []
    for fam in ["kimi", "claude", "qwen"]:
        pairs = (json.load(open(ROOT / "runs/refine/sample_pilot.json"))["pairs"]
                 + json.load(open(ROOT / "runs/refine/sample_extension.json"))["pairs"])
        sel = [p for p in pairs if p["family"] == fam]
        orig_costs, refine_costs, quals = [], [], []
        rlog = {}
        for lg in ["runs/logs/refine_pilot.jsonl", "runs/logs/refine_extension.jsonl"]:
            for line in open(ROOT / lg):
                j = json.loads(line)
                if j.get("usage"):
                    rlog[j["ctp_runId"]] = j
        jraw = []
        for jf in ["runs/logs/refine_judgments_pilot.jsonl",
                   "runs/logs/refine_judgments_extension.jsonl"]:
            jraw += [json.loads(l) for l in open(ROOT / jf) if l.strip()]
        rrows = ra.agg([x for x in jraw if not x.get("error") and not x.get("incomplete")])
        by_run = {(x["cell"], x["family"], x["runId"]): x for x in rows}
        for p in sel:
            o = by_run.get(("C-T-P", fam, p["ctp_runId"]))
            rl = rlog.get(p["ctp_runId"])
            q = rrows.get(f"R{p['ctp_runId']}")
            if o and rl and q:
                orig_costs.append(o[f"cost_{int(PHI_PRIMARY * 100)}"])
                refine_costs.append((rl["usage"]["prompt_tokens"] * REFINE_PRICE["input"]
                                     + rl["usage"]["completion_tokens"] * REFINE_PRICE["output"]) / 1e6)
                quals.append(q["composite"])
        refined_pts.append({"family": fam, "n": len(quals),
                            "mean_cost": float(np.mean(orig_costs) + np.mean(refine_costs)),
                            "mean_refine_cost": float(np.mean(refine_costs)),
                            "mean_quality": float(np.mean(quals))})

    result = {"phi_panel": PHIS, "primary_phi": PHI_PRIMARY,
              "cell_summary_primary": {c: {k: (round(v, 6) if isinstance(v, float) else v)
                                           for k, v in tab50[c].items()} for c in CELLS},
              "pareto_by_phi": {str(p): fronts[p] for p in PHIS},
              "pareto_stable": stable, "cheapest_cell": cheapest, "icer_vs_cheapest": icers,
              "t_egr_pooled_mean_per_cell": t_egr, "refined_ctp_points": refined_pts,
              "n_runs_priced": len(rows),
              "bias_note": "team intermediate outputs uncounted -> team costs slightly understated (Amendment A2)"}
    (outdir / "cost_effectiveness.json").write_text(json.dumps(result, indent=1) + "\n")

    # ---- scatter plot
    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = {"C": "#2b8cbe", "F": "#de2d26"}
    for c in CELLS:
        v = tab50[c]
        ax.errorbar(v["mean_cost"], v["mean_quality"], xerr=v["sd_cost"],
                    yerr=v["sd_quality"], fmt="o", ms=9,
                    color=cmap[c[0]], ecolor="gray", capsize=3)
        ax.annotate(c, (v["mean_cost"], v["mean_quality"]), textcoords="offset points",
                    xytext=(6, 5), fontsize=9)
    front_pts = sorted([(tab50[c]["mean_cost"], tab50[c]["mean_quality"]) for c in fronts[PHI_PRIMARY]])
    ax.plot([p[0] for p in front_pts], [p[1] for p in front_pts], "k--", lw=1,
            label="Pareto frontier (phi=0.5)")
    fam_color = {"kimi": "#1f77b4", "claude": "#d62728", "qwen": "#2ca02c"}
    for rp in refined_pts:
        ax.plot(rp["mean_cost"], rp["mean_quality"], "D", ms=10,
                markeredgecolor="black", color=fam_color[rp["family"]])
        ax.annotate(f"refined CTP ({rp['family']})", (rp["mean_cost"], rp["mean_quality"]),
                    textcoords="offset points", xytext=(6, -12), fontsize=8)
    ax.set_xlabel("Mean cost per run (USD, phi=0.5)")
    ax.set_ylabel("Mean judge composite quality")
    ax.set_title("Cost-effectiveness frontier: 8 cells + Study-2 refined C-T-P")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "cost_effectiveness_scatter.png", dpi=200)
    fig.savefig(outdir / "cost_effectiveness_scatter.pdf")

    # ---- console summary
    print(f"priced runs: {len(rows)}")
    print(f"{'cell':6s} {'cost$':>9s} {'quality':>8s} {'tokens':>8s}  T-EGR")
    for c in CELLS:
        v = tab50[c]
        print(f"{c:6s} {v['mean_cost']:9.5f} {v['mean_quality']:8.3f} "
              f"{v['mean_tokens']:8.0f}  {t_egr.get(c, 1.0)}")
    print("pareto:", {str(p): fronts[p] for p in PHIS}, "| stable:", stable)
    print("cheapest:", cheapest, "| ICER:", icers)
    for rp in refined_pts:
        print(f"refined {rp['family']:6s}: cost ${rp['mean_cost']:.5f} "
              f"(refine +${rp['mean_refine_cost']:.5f}) quality {rp['mean_quality']:.3f} n={rp['n']}")
    print(f"-> {outdir}")


if __name__ == "__main__":
    main()
