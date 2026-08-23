#!/usr/bin/env python3
"""FROZEN confirmatory analysis for the Protocol-12 replication wave (OSF jg49x).

Implements the pre-registered W1-W7 gate tests of
DeeWaanAI-Next/protocols/12-PROTOCOL-WAVE-CONFIRMATORY-REPLICATION.md §4.
Per Protocol §5.6 this script is frozen BEFORE wave judging completes; any
post-data re-specification must be a documented, labeled sensitivity.

Requires scipy/numpy/pandas/statsmodels (this machine: /usr/local/bin/python3).

Inputs (read-only):
  runs/logs/wave_run_ledger.json        (merged per-run records, D34)
  runs/logs/wave_judgments.jsonl        (judge_wave.py -> judge_v2.py output)
  data/problems/fresh_domain_map_wave.json
  config/price_vector.json              (primary; D23: tokens x vector)
  config/price_vector_minimax_promo.json (D46 sensitivity, --promo flag)

Output: results/wave_analysis.json

Study-1 reference values below were computed ON THE FROZEN STUDY-1 ARTIFACTS
(runs/logs/main_run_ledger.json + main_judgments.jsonl) on 2026-08-23,
pre-wave-data, and are part of the pre-registration (Protocol 12 §4 W3b/W4).
"""

import hashlib
import json
import sys
import time

sys.path.insert(0, "code")
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from refine_study2_analyze import agg, holm  # noqa: E402  (frozen Study-1 helpers)

ROOT = Path(__file__).resolve().parent.parent
CELLS = ("C-S-N", "C-T-N", "F-S-N")
DIMS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]
PHI = 0.5  # input/output token blend, identical to Study-1 A4 economics
ALPHA = 0.05

# ---------- Pre-registered Study-1 references (computed 2026-08-23, frozen) ----------
# Per-domain C-T-N minus F-S-N (composite), Study-1 frozen data. Marketing is
# the ONLY positive domain (strongest positive); finance the strongest negative.
STUDY1_DOMAIN_EFFECT = {
    "finance_business_models": -0.1062,
    "hr_organization": -0.0528,
    "marketing_communications": +0.0037,
    "operations_supply_chain": -0.0583,
    "product_innovation": -0.1033,
    "strategy_market_entry": -0.0356,
}
STUDY1_DOMAIN_SIGN = {d: ("+" if v > 0 else "-") for d, v in STUDY1_DOMAIN_EFFECT.items()}
STUDY1_CAPGAP_PEARSON_R = -0.978  # n=5 families, exploratory (D44/D45)
W4_MIN_FAMILIES = 8               # Protocol 12 §7: below this W4 is deferred


def fisher_power(n, rho):
    """Two-sided alpha=.05 power to detect |rho| with n families (Fisher-z)."""
    if n < 4:
        return float("nan")
    z = np.arctanh(rho) * np.sqrt(n - 3)
    return float(stats.norm.cdf(z - 1.959964) + stats.norm.cdf(-z - 1.959964))


def load(promo=False):
    led = json.loads((ROOT / "runs/logs/wave_run_ledger.json").read_text())
    recs = [json.loads(l) for l in open(ROOT / "runs/logs/wave_judgments.jsonl") if l.strip()]
    dm = json.loads((ROOT / "data/problems/fresh_domain_map_wave.json").read_text())["map"]
    vec_file = "price_vector_minimax_promo.json" if promo else "price_vector.json"
    pv = json.loads((ROOT / f"config/{vec_file}").read_text())["prices"]
    reg = json.loads((ROOT / "config/model_registry.json").read_text())
    model_of = {}
    for section in ("generators", "wave_generators"):
        for f, g in reg[section].items():
            if not isinstance(g, dict) or "frontier" not in g:
                continue
            model_of[(f, "cheap")] = g["cheap_sibling"]["model"]
            model_of[(f, "frontier")] = g["frontier"]["model"]
    comp = agg(recs)
    return led, recs, dm, pv, model_of, comp, vec_file


def build_df(led, dm, pv, model_of, comp):
    rows = []
    for r in led["results"]:
        if r.get("status") != "completed" or r.get("cell") not in CELLS:
            continue
        c = comp.get(r.get("runId"))
        if not c:
            continue
        tier = "cheap" if r["tier"] == "cheap" else "frontier"
        model = model_of[(r["family"], tier)]
        if model not in pv:
            sys.exit(f"price vector missing model {model} (family {r['family']})")
        p = pv[model]
        toks = r.get("totalTokensUsed") or 0
        rows.append(dict(runId=r["runId"], cell=r["cell"], family=r["family"],
                         problemId=r["problemId"], model=model, comp=c["composite"],
                         **{d: c[d] for d in DIMS},
                         toks=toks, lat=r.get("totalLatencyMs") or np.nan,
                         cost=toks * (PHI * p["output"] + (1 - PHI) * p["input"]) / 1e6,
                         domain=dm.get(r["problemId"])))
    df = pd.DataFrame(rows)
    df["fam_prob"] = df.family.astype(str) + "|" + df.problemId.astype(str)
    df["logtok"] = np.log(df.toks.clip(lower=1))
    return df


def lmm(df, formula):
    """Pre-committed random-effects structure (Protocol 12 §4): random
    intercepts for family (groups) with variance components for problem and
    family x problem."""
    import statsmodels.formula.api as smf
    return smf.mixedlm(formula, df, groups=df["family"],
                       vc_formula={"problem": "0 + C(problemId)",
                                   "fam_prob": "0 + C(fam_prob)"}).fit(reml=True)


def fixed(m):
    return {k: {"coef": round(float(v), 4), "p": round(float(m.pvalues[k]), 5)}
            for k, v in m.fe_params.items()}


def main():
    promo = "--promo" in sys.argv
    led, recs, dm, pv, model_of, comp, vec_file = load(promo)
    out = {
        "protocol": "12-PROTOCOL-WAVE-CONFIRMATORY-REPLICATION.md",
        "osf": "jg49x",
        "analysis_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "analyzed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "price_vector": f"config/{vec_file}",
        "alpha": ALPHA,
        "gates": {},
    }

    df = build_df(led, dm, pv, model_of, comp)
    if df.empty:
        sys.exit("no analyzable wave runs (completed + judged) found")
    fams = sorted(df.family.unique())
    out["n_runs"] = len(df)
    out["families"] = fams

    # Credit-exhaustion shortfall (Protocol 12 §5.4 disclosure).
    exhausted = led.get("familiesExhausted") or []
    per_fam = df.groupby("family").runId.count().to_dict()
    out["completion"] = {
        "per_family_completed": {f: int(per_fam.get(f, 0)) for f in fams},
        "expected_per_family": 240,
        "families_exhausted": exhausted,
    }

    # ---------------- W1: pooled team effect replication ----------------
    m1 = lmm(df[df.cell.isin(["C-S-N", "C-T-N"])],
             "comp ~ C(cell, Treatment('C-S-N'))")
    k = [x for x in m1.fe_params.index if "C-T-N" in x][0]
    w1 = {"model": "LMM comp ~ cell + (1|family) + (1|problem) + (1|family:problem), cells C-S-N/C-T-N",
          "fixed_effects": fixed(m1),
          "team_effect_coef": round(float(m1.fe_params[k]), 4),
          "team_effect_p": round(float(m1.pvalues[k]), 5)}
    w1["gate"] = "PASS" if (w1["team_effect_p"] < ALPHA and w1["team_effect_coef"] > 0) else "FAIL"
    out["W1_team_effect"] = w1

    # ---------------- W2: upgrade threshold replication ----------------
    m2 = lmm(df[df.cell.isin(["C-T-N", "F-S-N"])],
             "comp ~ C(cell, Treatment('C-T-N'))")
    k2 = [x for x in m2.fe_params.index if "F-S-N" in x][0]
    w2 = {"model": "same LMM, cells C-T-N/F-S-N (reference C-T-N)",
          "fixed_effects": fixed(m2),
          "frontier_over_team_coef": round(float(m2.fe_params[k2]), 4),
          "frontier_over_team_p": round(float(m2.pvalues[k2]), 5)}
    w2["gate"] = "PASS" if (w2["frontier_over_team_p"] < ALPHA and w2["frontier_over_team_coef"] > 0) else "FAIL"
    out["W2_upgrade_threshold"] = w2

    # ---------------- W3: domain contingency ----------------
    sub = df[df.cell.isin(["C-S-N", "C-T-N", "F-S-N"])].copy()
    m_full = lmm(sub, "comp ~ logtok + C(cell, Treatment('C-S-N')) * C(domain)")
    m_reduced = lmm(sub, "comp ~ logtok + C(cell, Treatment('C-S-N')) + C(domain)")
    lr_stat = float(2 * (m_full.llf - m_reduced.llf))
    n_inter = len(m_full.fe_params) - len(m_reduced.fe_params)
    p_inter = float(stats.chi2.sf(lr_stat, n_inter))
    # Per-domain team effect — Study-1 A0/MANIFEST-54 definition: C-T-N minus F-S-N.
    per_domain = {}
    tests = []
    for dom in sorted(STUDY1_DOMAIN_EFFECT):
        piv = df[df.domain == dom].pivot_table(index="problemId", columns="cell",
                                               values="comp", aggfunc="mean")
        if "C-T-N" not in piv.columns or "F-S-N" not in piv.columns:
            per_domain[dom] = {"status": "missing_cells"}
            continue
        dlt = (piv["C-T-N"] - piv["F-S-N"]).dropna().values
        t, p = stats.ttest_1samp(dlt, 0)
        per_domain[dom] = {"n_problems": int(len(dlt)), "delta": round(float(dlt.mean()), 4),
                           "t": round(float(t), 3), "p": round(float(p), 5),
                           "study1_ref": STUDY1_DOMAIN_EFFECT[dom]}
        tests.append((dom, p))
    ps = [p for _, p in tests]
    ph = holm(ps) if ps else []
    for (dom, p), q in zip(tests, ph):
        per_domain[dom]["p_holm"] = round(float(q), 5)
    wave_sign = {d: ("+" if v.get("delta", 0) > 0 else "-")
                 for d, v in per_domain.items() if "delta" in v}
    sign_matches = sum(1 for d, s in wave_sign.items() if STUDY1_DOMAIN_SIGN.get(d) == s)
    strongest_pos = max((d for d in wave_sign if wave_sign[d] == "+"),
                        key=lambda d: per_domain[d]["delta"], default=None)
    strongest_neg = min((d for d in wave_sign),
                        key=lambda d: per_domain[d]["delta"], default=None)
    g3a = p_inter < ALPHA
    g3b = (sign_matches >= 4 and strongest_pos == "marketing_communications"
           and strongest_neg == "finance_business_models")
    out["W3_domain_contingency"] = {
        "gate3a_interaction": {"LRT_chi2": round(lr_stat, 3), "df": n_inter,
                               "p": round(p_inter, 5), "gate": "PASS" if g3a else "FAIL",
                               "model": "LMM comp ~ logtok + cell*domain + RE(family, problem, family:problem)"},
        "gate3b_directional": {"per_domain": per_domain, "sign_matches": f"{sign_matches}/6",
                               "strongest_positive": strongest_pos, "strongest_negative": strongest_neg,
                               "study1_reference": STUDY1_DOMAIN_EFFECT,
                               "gate": "PASS" if g3b else "FAIL"},
        "gate": "PASS" if (g3a and g3b) else "FAIL",
    }

    # ---------------- W4: capability-gap mechanism ----------------
    fam_means = {f: {c: float(df[(df.family == f) & (df.cell == c)].comp.mean())
                     for c in CELLS if len(df[(df.family == f) & (df.cell == c)]) > 0}
                 for f in fams}
    complete = [f for f in fams if all(c in fam_means[f] for c in CELLS)]
    w4 = {"families_complete": len(complete), "families": complete,
          "study1_reference_r": STUDY1_CAPGAP_PEARSON_R}
    if len(complete) >= W4_MIN_FAMILIES:
        delta = np.array([fam_means[f]["F-S-N"] - fam_means[f]["C-S-N"] for f in complete])
        tau = np.array([fam_means[f]["C-T-N"] - fam_means[f]["C-S-N"] for f in complete])
        rp, pp = stats.pearsonr(delta, tau)
        rs, ps_ = stats.spearmanr(delta, tau)
        w4.update({"capability_gap_delta": {f: round(float(d), 4) for f, d in zip(complete, delta)},
                   "team_effect_tau": {f: round(float(t), 4) for f, t in zip(complete, tau)},
                   "pearson_r": round(float(rp), 4), "pearson_p": round(float(pp), 5),
                   "spearman_rho": round(float(rs), 4), "spearman_p": round(float(ps_), 5),
                   "power_at_n_for_rho_0.80": round(fisher_power(len(complete), 0.80), 3),
                   "power_at_n_for_rho_0.70": round(fisher_power(len(complete), 0.70), 3)})
        w4["gate"] = "PASS" if (pp < ALPHA and rp < 0) else "FAIL"
    else:
        w4["gate"] = "DEFERRED"
        w4["reason"] = f"< {W4_MIN_FAMILIES} complete families (Protocol 12 §7); deferred and disclosed"
    out["W4_capability_gap"] = w4

    # ---------------- W5: variance / downside replication ----------------
    w5 = {"per_domain_brown_forsythe": {}, "downside": {}}
    for dom in sorted({d for d in df.domain.dropna().unique()}):
        t = df[(df.domain == dom) & (df.cell == "C-T-N")].comp.values
        s = df[(df.domain == dom) & (df.cell == "C-S-N")].comp.values
        if len(t) < 10 or len(s) < 10:
            continue
        wstat, p = stats.levene(t, s, center="median")  # Brown-Forsythe
        w5["per_domain_brown_forsythe"][dom] = {
            "sd_team": round(float(t.std(ddof=1)), 4), "sd_solo": round(float(s.std(ddof=1)), 4),
            "stat": round(float(wstat), 3), "p": round(float(p), 5),
            "p_below_4.0_team": round(float((t < 4.0).mean()), 4),
            "p_below_4.0_solo": round(float((s < 4.0).mean()), 4)}
    mkt = w5["per_domain_brown_forsythe"].get("marketing_communications")
    if mkt:
        w5["gate"] = "PASS" if (mkt["p"] < ALPHA and mkt["sd_team"] < mkt["sd_solo"]) else "FAIL"
    else:
        w5["gate"] = "DEFERRED"
        w5["reason"] = "marketing domain missing sufficient data"
    tp = df[df.cell == "C-T-N"].comp.values
    sp = df[df.cell == "C-S-N"].comp.values
    wstat, p = stats.levene(tp, sp, center="median")
    w5["pooled"] = {"sd_team": round(float(tp.std(ddof=1)), 4), "sd_solo": round(float(sp.std(ddof=1)), 4),
                    "p": round(float(p), 5), "note": "reported without gate (Protocol 12 §4 W5)"}
    out["W5_variance"] = w5

    # ---------------- W6: economics replication (T-EGR) ----------------
    cs = {}
    for cell in CELLS:
        g = df[df.cell == cell]
        cost, lat, q = float(g.cost.mean()), float(g.lat.mean()) / 1000.0, float(g.comp.mean())
        cs[cell] = {"cost_usd": round(cost, 5), "latency_s": round(lat, 1),
                    "quality": round(q, 4),
                    "quality_per_dollar_minute": round(q / (cost * lat / 60), 1) if cost > 0 and lat > 0 else None}
    fsn, ctn = cs["F-S-N"], cs["C-T-N"]
    pareto = []
    for c, m in cs.items():
        dominated = any(o["cost_usd"] <= m["cost_usd"] and o["latency_s"] <= m["latency_s"]
                        and o["quality"] >= m["quality"]
                        and (o["cost_usd"] < m["cost_usd"] or o["latency_s"] < m["latency_s"]
                             or o["quality"] > m["quality"])
                        for o2, o in cs.items() if o2 != c)
        if not dominated:
            pareto.append(c)
    tegr = {}
    for cell in ("C-S-N", "C-T-N"):
        tegr[cell] = round((cs[cell]["quality"] / fsn["quality"]) / (cs[cell]["cost_usd"] / fsn["cost_usd"]), 3) \
            if fsn["quality"] > 0 and fsn["cost_usd"] > 0 else None
    gate6 = (fsn["quality_per_dollar_minute"] is not None
             and ctn["quality_per_dollar_minute"] is not None
             and fsn["quality_per_dollar_minute"] > ctn["quality_per_dollar_minute"]
             and "F-S-N" in pareto)
    out["W6_economics"] = {"cell_summary": cs, "pareto_frontier": pareto,
                           "T_EGR_vs_FSN": tegr,
                           "note": "T-EGR = (quality_cell/quality_FSN)/(cost_cell/cost_FSN); >1 = more efficient than frontier solo. Cost = tokens x price vector (D23), PHI=0.5 blend as Study-1 A4.",
                           "gate": "PASS" if gate6 else "FAIL"}

    # ---------------- W7: judge reliability audit (no gate) ----------------
    from collections import defaultdict
    rater_scores = defaultdict(dict)
    for rc in recs:
        sc = rc.get("scores") or {}
        if not all(isinstance(sc.get(d), (int, float)) for d in DIMS):
            continue
        rater_scores[rc["runId"]][f"{rc['judge_family']}|{rc['variant']}"] = \
            float(np.mean([sc[d] for d in DIMS]))
    run_dom = {r["runId"]: dm.get(r["problemId"]) for r in led["results"]}
    w7 = {}
    for dom in sorted({d for d in run_dom.values() if d}):
        rid = [i for i, d in run_dom.items() if d == dom and len(rater_scores.get(i, {})) == 9]
        if len(rid) < 20:
            continue
        raters = sorted(set().union(*[rater_scores[i] for i in rid]))
        M = np.array([[rater_scores[i][rt] for rt in raters] for i in rid])
        n, k = M.shape
        g = M.mean(); rm = M.mean(axis=1); cm = M.mean(axis=0)
        ss_r = k * ((rm - g) ** 2).sum(); ss_c = n * ((cm - g) ** 2).sum()
        ss_e = ((M - g) ** 2).sum() - ss_r - ss_c
        BMS = ss_r / (n - 1); EMS = ss_e / ((n - 1) * (k - 1))
        w7[dom] = {"n_runs": n, "k_raters": k,
                   "icc_3_1": round(float((BMS - EMS) / (BMS + (k - 1) * EMS)), 3),
                   "icc_3_k": round(float((BMS - EMS) / BMS), 3)}
    out["W7_judge_icc_by_domain"] = w7

    # ---------------- Upgrade-gate summary (Protocol 12 §1, binding) ----------------
    out["upgrade_gate_summary"] = {
        "rule": "an exploratory Study-1 finding upgrades to a headline claim only if its wave gate PASSes at pre-registered alpha and direction",
        "domain_contingency": out["W3_domain_contingency"]["gate"],
        "capability_gap_mechanism": w4["gate"],
        "marketing_variance_advantage": w5["gate"],
        "core_replications": {"W1_team_effect": w1["gate"], "W2_upgrade_threshold": w2["gate"],
                              "W6_economics": out["W6_economics"]["gate"]},
    }

    out_path = ROOT / ("results/wave_analysis" + ("_minimax_promo" if promo else "") + ".json")
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"saved: {out_path}")
    print(json.dumps(out["upgrade_gate_summary"], indent=1))
    print(f"W3a p={out['W3_domain_contingency']['gate3a_interaction']['p']} | "
          f"W3b signs {out['W3_domain_contingency']['gate3b_directional']['sign_matches']} | "
          f"W4 r={w4.get('pearson_r')} p={w4.get('pearson_p')} ({w4['gate']})")


if __name__ == "__main__":
    main()
