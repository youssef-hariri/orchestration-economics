#!/usr/bin/env python3
"""Exploratory heterogeneity & robustness analyses (post-hoc, NOT pre-registered).

Decision D44 (DESIGN-DECISIONS.md) / MANIFEST Entry 53. All analyses here are
EXPLORATORY moderator/robustness analyses on the frozen Study-1 main run
(1,900 completed runs, cells C-S-N/C-T-N/F-S-N). Confirmatory tests remain the
pre-registered H1-H6 in Protocol 01. Rationale and citations per analysis:

  A1 reliability/variance ....... ensemble variance reduction (Hansen &
                                  Salamon 1990; Dietterich 2000); Brown &
                                  Forsythe (1974) robust variance test.
  A2 difficulty moderation ...... moderator regression practice from
                                  meta-analysis (Borenstein et al. 2009).
  A3 length-controlled ANCOVA ... LLM-judge length bias (Zheng et al. 2023;
                                  Dubois et al. 2024); LMM per Westfall et
                                  al. (2014).
  A4 latency economics .......... cost-latency-quality tri-objective frontier
                                  (descriptive; no prior registration).
  A5 dimension decomposition .... BH-FDR (Benjamini & Hochberg 1995).
  A6 family rank stability ...... Kendall's W (Kendall & Babington Smith 1939).
  A7 judge reliability .......... Shrout & Fleiss (1979) ICC(3,1)/ICC(3,k).

Inputs (read-only): runs/logs/main_run_ledger.json,
runs/logs/main_judgments.jsonl, data/problems/domain_map.json,
config/price_vector.json, config/model_registry.json.
Output: results/exploratory_heterogeneity.json
"""
import sys, json
sys.path.insert(0, "code")
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path("research/orchestration-economics")
try:
    from refine_study2_analyze import agg, holm
except ImportError:
    from code.refine_study2_analyze import agg, holm

CELLS = ("C-S-N", "C-T-N", "F-S-N")
PHI = 0.5
DIMS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]

def load():
    led = json.loads((ROOT / "runs/logs/main_run_ledger.json").read_text())["results"]
    recs = [json.loads(l) for l in open(ROOT / "runs/logs/main_judgments.jsonl") if l.strip()]
    dm = json.loads((ROOT / "data/problems/domain_map.json").read_text())["map"]
    pv = json.loads((ROOT / "config/price_vector.json").read_text())["prices"]
    reg = json.loads((ROOT / "config/model_registry.json").read_text())["generators"]
    model_of = {(f, "cheap"): g["cheap_sibling"]["model"] for f, g in reg.items()} | \
               {(f, "frontier"): g["frontier"]["model"] for f, g in reg.items()}
    comp = agg(recs)  # runId -> {composite, per-dim}
    return led, recs, dm, pv, model_of, comp

def main():
    led, recs, dm, pv, model_of, comp = load()
    fams = sorted({r["family"] for r in led})
    runs = []
    for r in led:
        if r["status"] != "completed" or r["cell"] not in CELLS:
            continue
        c = comp.get(r["runId"])
        if not c:
            continue
        tier = "cheap" if r["tier"] == "cheap" else "frontier"
        p = pv[model_of[(r["family"], tier)]]
        runs.append(dict(runId=r["runId"], cell=r["cell"], family=r["family"],
                         problemId=r["problemId"], comp=c["composite"],
                         **{d: c[d] for d in DIMS},
                         toks=r["totalTokensUsed"], lat=r["totalLatencyMs"],
                         cost=r["totalTokensUsed"] * (PHI * p["output"] + (1 - PHI) * p["input"]) / 1e6,
                         domain=dm.get(r["problemId"])))
    df = pd.DataFrame(runs)
    out = {"note": "EXPLORATORY post-hoc analyses per DESIGN-DECISIONS D44 / MANIFEST Entry 53. Not pre-registered.", "n_runs": len(df)}
    print(f"loaded {len(df)} analyzed runs")

    # ---------- A1 reliability / downside risk ----------
    a1 = {"cell_sd_cv": {}, "brown_forsythe_team_vs_solo": {}, "downside": {}, "domain_sd": {}}
    for (cell, fam), g in df.groupby(["cell", "family"]):
        a1["cell_sd_cv"][f"{fam}|{cell}"] = {"n": int(len(g)), "mean": round(float(g.comp.mean()), 4),
                                             "sd": round(float(g.comp.std(ddof=1)), 4),
                                             "cv": round(float(g.comp.std(ddof=1) / g.comp.mean()), 4)}
    for fam in fams:
        t = df[(df.family == fam) & (df.cell == "C-T-N")].comp.values
        s = df[(df.family == fam) & (df.cell == "C-S-N")].comp.values
        w, p = stats.levene(t, s, center="median")  # Brown-Forsythe
        a1["brown_forsythe_team_vs_solo"][fam] = {"sd_team": round(float(t.std(ddof=1)), 4),
                                                  "sd_solo": round(float(s.std(ddof=1)), 4),
                                                  "stat": round(float(w), 3), "p": round(float(p), 4)}
    for cell in CELLS:
        g = df[df.cell == cell].comp.values
        a1["downside"][cell] = {"p10": round(float(np.percentile(g, 10)), 3),
                                "p_below_4.0": round(float((g < 4.0).mean()), 4)}
    for (dom, cell), g in df.groupby(["domain", "cell"]):
        if cell != "C-T-N":
            continue
        s = df[(df.domain == dom) & (df.cell == "C-S-N")].comp.values
        w, p = stats.levene(g.comp.values, s, center="median")
        a1["domain_sd"][dom] = {"sd_team": round(float(g.comp.std(ddof=1)), 4),
                                "sd_solo": round(float(s.std(ddof=1)), 4), "p_BF": round(float(p), 4)}
    out["A1_reliability"] = a1

    # ---------- A2 difficulty moderation ----------
    diff = df.groupby("problemId").comp.mean()
    by_p = df.pivot_table(index="problemId", columns="cell", values="comp", aggfunc="mean")
    delta = (by_p["C-T-N"] - by_p["F-S-N"]).dropna()
    x, y = diff.loc[delta.index].values, delta.values
    rp, pp = stats.pearsonr(x, y); rs, ps = stats.spearmanr(x, y)
    slope, intercept, *_ = stats.linregress(x, y)
    out["A2_difficulty_moderation"] = {"n_problems": len(y), "pearson_r": round(float(rp), 3),
                                       "pearson_p": round(float(pp), 4), "spearman_rho": round(float(rs), 3),
                                       "spearman_p": round(float(ps), 4), "slope": round(float(slope), 3),
                                       "hardest_problem": diff.idxmin(), "hardest_score": round(float(diff.min()), 3),
                                       "easiest_problem": diff.idxmax(), "easiest_score": round(float(diff.max()), 3)}

    # ---------- A3 length-controlled ANCOVA ----------
    import statsmodels.formula.api as smf
    df["logtok"] = np.log(df.toks)
    try:
        m = smf.mixedlm("comp ~ logtok + C(cell, Treatment('C-S-N'))", df, groups=df["family"],
                        vc_formula={"problem": "0 + C(problemId)"}).fit(reml=True)
        fx = {k: round(float(v), 4) for k, v in m.fe_params.items()}
        pv_ = {k: round(float(v), 4) for k, v in m.pvalues.items()}
        out["A3_length_ancova"] = {"model": "LMM comp ~ logtok + cell + (1|family) + (1|problem)",
                                   "fixed_effects": fx, "p_values": pv_,
                                   "interpretation": "team/frontier coefficients AFTER controlling log(tokens)"}
    except Exception as e:  # pragma: no cover
        out["A3_length_ancova"] = {"error": str(e)}

    # ---------- A4 latency economics ----------
    a4 = {"cell_summary": {}, "pareto_frontier": [], "dominated": []}
    cs = {}
    for cell, g in df.groupby("cell"):
        cs[cell] = (float(g.cost.mean()), float(g.lat.mean()) / 1000.0, float(g.comp.mean()))
        a4["cell_summary"][cell] = {"cost": round(cs[cell][0], 5), "latency_s": round(cs[cell][1], 1),
                                    "quality": round(cs[cell][2], 3),
                                    "quality_per_dollar_minute": round(cs[cell][2] / (cs[cell][0] * cs[cell][1] / 60), 1)}
    for c, (cost, lat, q) in cs.items():
        dom_by = [o for o, (c2, l2, q2) in cs.items() if o != c and c2 <= cost and l2 <= lat and q2 >= q
                  and (c2 < cost or l2 < lat or q2 > q)]
        (a4["dominated"] if dom_by else a4["pareto_frontier"]).append(c)
    out["A4_latency_economics"] = a4

    # ---------- A5 dimension decomposition by domain ----------
    tests = []
    for dim in DIMS:
        piv = df.pivot_table(index="problemId", columns=["cell", "domain"], values=dim, aggfunc="mean")
        for dom in sorted(df.domain.dropna().unique()):
            if ("C-T-N", dom) not in piv.columns or ("F-S-N", dom) not in piv.columns:
                continue
            dlt = (piv[("C-T-N", dom)] - piv[("F-S-N", dom)]).dropna().values
            if len(dlt) < 3:  # main run uses 19/30 problems -> 3-4 problems per domain
                continue
            t, p = stats.ttest_1samp(dlt, 0)
            tests.append({"dim": dim, "domain": dom, "n": int(len(dlt)),
                          "delta": round(float(dlt.mean()), 4), "t": round(float(t), 3), "p": round(float(p), 5)})
    ps = [t_["p"] for t_ in tests]
    ph = holm(ps)
    for t_, qv in zip(tests, ph):
        t_["p_holm"] = qv
        t_["sig_holm"] = bool(qv is not None and qv < 0.05)
    out["A5_dimension_domains"] = {"n_tests": len(tests),
                                   "significant_holm": [t_ for t_ in tests if t_["sig_holm"]],
                                   "all": tests}

    # ---------- A6 family rank stability (Kendall's W) ----------
    def kendall_w(matrix):  # rows=raters(domains), cols=objects(families)
        m = np.asarray(matrix, float)
        k, n = m.shape
        ranks = np.apply_along_axis(stats.rankdata, 1, m)
        R = ranks.sum(axis=0)
        W = 12 * ((R - R.mean()) ** 2).sum() / (k ** 2 * (n ** 3 - n))
        return W
    a6 = {}
    for cell in ("C-T-N", "F-S-N"):
        piv = df[df.cell == cell].pivot_table(index="domain", columns="family", values="comp", aggfunc="mean")
        piv = piv[fams].dropna()
        a6[cell] = {"kendall_W": round(float(kendall_w(piv.values)), 3),
                    "rank_table": {d: {f: int(r) for f, r in zip(piv.columns, stats.rankdata(row, method="min"))}
                                   for d, row in piv.iterrows()}}
    out["A6_rank_stability"] = a6

    # ---------- A7 judge reliability ICC(3,1)/(3,k) per domain ----------
    rater_scores = defaultdict(dict)
    for rc in recs:
        sc = rc.get("scores") or {}
        if not all(isinstance(sc.get(d), (int, float)) for d in DIMS):
            continue
        rater = f"{rc['judge_family']}|{rc['variant']}"
        rater_scores[rc["runId"]][rater] = float(np.mean([sc[d] for d in DIMS]))
    run_dom = {r["runId"]: r["domain"] for r in runs}
    run_cell = {r["runId"]: r["cell"] for r in runs}
    a7 = {}
    for dom in sorted({d for d in run_dom.values() if d}):
        rid = [i for i, d in run_dom.items() if d == dom and run_cell.get(i) in CELLS and len(rater_scores.get(i, {})) == 9]
        if len(rid) < 20:
            continue
        raters = sorted(set().union(*[rater_scores[i] for i in rid]))
        M = np.array([[rater_scores[i][rt] for rt in raters] for i in rid])
        n, k = M.shape
        g = M.mean(); rm = M.mean(axis=1); cm = M.mean(axis=0)
        ss_r = k * ((rm - g) ** 2).sum(); ss_c = n * ((cm - g) ** 2).sum()
        ss_t = ((M - g) ** 2).sum(); ss_e = ss_t - ss_r - ss_c
        BMS = ss_r / (n - 1); EMS = ss_e / ((n - 1) * (k - 1))
        a7[dom] = {"n_runs": n, "k_raters": k,
                   "icc_3_1": round(float((BMS - EMS) / (BMS + (k - 1) * EMS)), 3),
                   "icc_3_k": round(float((BMS - EMS) / BMS), 3)}
    out["A7_judge_icc_by_domain"] = a7

    out_path = ROOT / "results/exploratory_heterogeneity.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("saved:", out_path)
    print(json.dumps({k: (v if not isinstance(v, dict) or len(str(v)) < 400 else f"<{len(v)} entries>") for k, v in out.items()}, indent=1, ensure_ascii=False)[:2000])

if __name__ == "__main__":
    main()
