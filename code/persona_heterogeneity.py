#!/usr/bin/env python3
"""Persona-extended exploratory heterogeneity battery (post-hoc, NOT pre-registered).

Decision D45 (DESIGN-DECISIONS.md) / MANIFEST Entry 54. Extends the D44 battery
with the Persona axis (cells *-P), using the full 2x2x2 frozen main run
(1,900 runs; all 8 cells x 5 families). Zero API calls.

  P1 persona effect on Cultural Sensitivity by domain (the dimension personas
     were designed for; moderator logic per Borenstein et al. 2009; Holm 1979).
  P2 domain-specificity of the persona novelty/usefulness trade-off (interim-2:
     personas +0.154 novelty, -1.024 usefulness pooled; H4 composite d=-0.691).
  P3 length-controlled persona ANCOVA (Zheng et al. 2023; Dubois et al. 2024):
     do persona effects survive log-token control? composite + novelty models.
  P4 judge reliability N vs P (Shrout & Fleiss 1979 ICC): do culturally
     stylized answers split the panel more?
  P5 persona effect on variance (Brown & Forsythe 1974), pooled + by domain.

Paired logic: deltas computed at the problem level within family between
matched N/P cells, pooled across families (family as replication).
Output: results/persona_heterogeneity.json
"""
import sys, json
sys.path.insert(0, "code")
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
from refine_study2_analyze import agg, holm

ROOT = Path("research/orchestration-economics")
DIMS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]

def main():
    led = json.loads((ROOT / "runs/logs/main_run_ledger.json").read_text())["results"]
    recs = [json.loads(l) for l in open(ROOT / "runs/logs/main_judgments.jsonl") if l.strip()]
    dm = json.loads((ROOT / "data/problems/domain_map.json").read_text())["map"]
    comp = agg(recs)
    runs = []
    for r in led:
        if r["status"] != "completed":
            continue
        c = comp.get(r["runId"])
        if not c:
            continue
        runs.append(dict(runId=r["runId"], cell=r["cell"], family=r["family"],
                         problemId=r["problemId"], comp=c["composite"],
                         **{d: c[d] for d in DIMS},
                         toks=r["totalTokensUsed"],
                         persona=r["cell"].endswith("P"),
                         team=r["cell"][2] == "T",
                         frontier=r["cell"][0] == "F",
                         domain=dm.get(r["problemId"])))
    df = pd.DataFrame(runs)
    out = {"note": "EXPLORATORY persona extension of D44 (D45 / Entry 54). Not pre-registered.",
           "n_runs": len(df)}
    print(f"loaded {len(df)} runs")

    # ---------- P1+P2: persona effect (P - N) per dim, pooled and by domain ----------
    def dim_delta(dim, structure, tier):
        """problem-level persona deltas within (structure, tier), pooled families."""
        piv = df[(df.team == structure) & (df.frontier == tier)].pivot_table(
            index="problemId", columns="persona", values=dim, aggfunc="mean")
        return (piv[True] - piv[False]).dropna()

    p12 = {"pooled": [], "by_domain": []}
    for structure in (False, True):
        for tier in (False, True):
            tag = f"{'team' if structure else 'solo'}-{'frontier' if tier else 'cheap'}"
            for dim in DIMS:
                dlt = dim_delta(dim, structure, tier)
                if len(dlt) < 3:
                    continue
                t, p = stats.ttest_1samp(dlt, 0)
                p12["pooled"].append({"config": tag, "dim": dim, "n": int(len(dlt)),
                                      "delta": round(float(dlt.mean()), 4),
                                      "p": round(float(p), 5)})
    ps = [x["p"] for x in p12["pooled"]]
    for x, q in zip(p12["pooled"], holm(ps)):
        x["p_holm"] = q
    # by domain, cheap tier only (balanced full coverage), both structures, key dims
    for dom in sorted(df.domain.dropna().unique()):
        for structure in (False, True):
            sub = df[(df.domain == dom) & (df.team == structure) & (~df.frontier)]
            for dim in DIMS:
                piv = sub.pivot_table(index="problemId", columns="persona", values=dim, aggfunc="mean")
                if True not in piv.columns or False not in piv.columns:
                    continue
                dlt = (piv[True] - piv[False]).dropna()
                if len(dlt) < 3:
                    continue
                t, p = stats.ttest_1samp(dlt, 0)
                p12["by_domain"].append({"domain": dom, "team": structure, "dim": dim,
                                         "n": int(len(dlt)), "delta": round(float(dlt.mean()), 4),
                                         "p": round(float(p), 5)})
    psd = [x["p"] for x in p12["by_domain"]]
    for x, q in zip(p12["by_domain"], holm(psd)):
        x["p_holm"] = q
    out["P1_P2_persona_by_dim"] = p12

    # ---------- P3: length-controlled persona ANCOVA (cheap tier, full 5 families) ----------
    import statsmodels.formula.api as smf
    sub = df[~df.frontier].copy()
    sub["logtok"] = np.log(sub.toks)
    sub["cultsens"] = sub["Cultural Sensitivity"]
    p3 = {}
    for dv in ("comp", "Novelty", "Usefulness", "cultsens"):
        try:
            m = smf.mixedlm(f"{dv} ~ logtok + team * persona", sub, groups=sub["family"],
                            vc_formula={"problem": "0 + C(problemId)"}).fit(reml=True)
            p3[dv] = {"fixed_effects": {k: round(float(v), 4) for k, v in m.fe_params.items()},
                      "p_values": {k: round(float(v), 4) for k, v in m.pvalues.items()
                                   if not k.endswith("Var")}}
        except Exception as e:
            p3[dv] = {"error": str(e)}
    # raw persona means for reference
    raw = sub.groupby(["team", "persona"])[["comp"] + DIMS].mean().round(4)
    p3["raw_means"] = json.loads(raw.to_json(orient="index"))
    out["P3_length_ancova"] = p3

    # ---------- P4: ICC N vs P ----------
    rater_scores = defaultdict(dict)
    for rc in recs:
        sc = rc.get("scores") or {}
        if not all(isinstance(sc.get(d), (int, float)) for d in DIMS):
            continue
        rater_scores[rc["runId"]][f"{rc['judge_family']}|{rc['variant']}"] = \
            float(np.mean([sc[d] for d in DIMS]))

    def icc(run_ids):
        rid = [i for i in run_ids if len(rater_scores.get(i, {})) == 9]
        if len(rid) < 20:
            return None
        raters = sorted(set().union(*[rater_scores[i] for i in rid]))
        M = np.array([[rater_scores[i][rt] for rt in raters] for i in rid])
        n, k = M.shape
        g = M.mean(); rm = M.mean(axis=1); cm = M.mean(axis=0)
        ss_r = k * ((rm - g) ** 2).sum(); ss_c = n * ((cm - g) ** 2).sum()
        ss_e = ((M - g) ** 2).sum() - ss_r - ss_c
        BMS = ss_r / (n - 1); EMS = ss_e / ((n - 1) * (k - 1))
        return {"n_runs": n, "icc_3_1": round(float((BMS - EMS) / (BMS + (k - 1) * EMS)), 3),
                "icc_3_k": round(float((BMS - EMS) / BMS), 3)}

    p4 = {}
    for pers, lab in ((False, "neutral"), (True, "persona")):
        p4[lab] = icc(df[df.persona == pers].runId.tolist())
    out["P4_icc_n_vs_p"] = p4

    # ---------- P5: variance effect of persona ----------
    p5 = {"pooled_by_structure": {}, "by_domain_cheap": {}}
    for team in (False, True):
        s = df[(df.team == team) & (~df.persona) & (~df.frontier)].comp.values
        p = df[(df.team == team) & (df.persona) & (~df.frontier)].comp.values
        w, pv = stats.levene(s, p, center="median")
        p5["pooled_by_structure"]["team" if team else "solo"] = {
            "sd_N": round(float(s.std(ddof=1)), 4), "sd_P": round(float(p.std(ddof=1)), 4),
            "p_BF": round(float(pv), 4)}
    for dom in sorted(df.domain.dropna().unique()):
        s = df[(df.domain == dom) & (~df.persona) & (~df.frontier)].comp.values
        p = df[(df.domain == dom) & (df.persona) & (~df.frontier)].comp.values
        w, pv = stats.levene(s, p, center="median")
        p5["by_domain_cheap"][dom] = {"sd_N": round(float(s.std(ddof=1)), 4),
                                      "sd_P": round(float(p.std(ddof=1)), 4),
                                      "p_BF": round(float(pv), 4)}
    out["P5_persona_variance"] = p5

    out_path = ROOT / "results/persona_heterogeneity.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("saved:", out_path)

if __name__ == "__main__":
    main()
