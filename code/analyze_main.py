#!/usr/bin/env python3
"""Interim-2 main-run analysis (Protocol 03 + Amendment A2, author-approved 2026-08-05).

Primary layer (pre-registered, sole decision basis for R1/R2/R3):
  - run-level composite DV (9 judgments: 3 judges x 3 verbatim variants)
  - H1 tier x structure interaction contrast d = (FT - FS) - (CT - CS)
  - tier / structure / persona main effects (Welch)
  - O'Brien-Fleming interim-2 boundary check (Protocol 03 alpha spend)

A2 layers (estimation / robustness / evidence; never override the decision):
  A2.1 percentile bootstrap 95% CI (5,000 resamples, seed 42) on every primary d
  A2.2 Benjamini-Hochberg FDR on declared secondary contrast families
  A2.3 2x2x2 Type-II ANOVA, partial eta^2, assumption diagnostics
  A2.4 Rouder JZS Bayes factor (proper numerical integration; NOT Paper 2's approx)
  A2.5 leave-one-family-out sensitivity (5 folds)
  A2.6 leave-one-problem-out generalizability (19 folds)
  A2.7 sensitivity power: minimum detectable d at 80% power for achieved n
  (+ A1.4 legacy: length-adjusted interaction via OLS HC1)

Inputs: runs/fulltext/main_fulltext.json, runs/logs/main_judgments.jsonl
Output: results/interim2_analysis.json
"""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.integrate import quad
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import TTestIndPower

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]
BOOT_N = 5000
BOOT_SEED = 42
R_JZS = 0.707  # Rouder default Cauchy scale

# --- Protocol 03: interim-2 nominal boundary (O'Brien-Fleming, 2 looks).
# Interim-2 is the FINAL look of the 2-stage design; remaining alpha = full 0.05
# less interim-1 spend (OBF: spend at info fraction 0.5 approx 0.00057 -> the
# protocol froze interim-1 boundary z=3.29; interim-2 z boundary below).
INTERIM2_Z_BOUNDARY = 1.977  # OBF final-look boundary, see Protocol 03


def load_judgments(path):
    last = {}
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        last[(r["runId"], r["judge_family"], r["variant"])] = r
    recs = list(last.values())
    bad = [r for r in recs if r.get("error") or r.get("incomplete")]
    return [r for r in recs if not (r.get("error") or r.get("incomplete"))], len(bad)


def judgment_mean(scores):
    vals = [v for v in scores.values() if isinstance(v, (int, float))]
    return float(np.mean(vals)) if vals else None


def build_run_table(recs, meta):
    rows, by_run = [], {}
    for r in recs:
        m = judgment_mean(r.get("scores") or {})
        if m is None:
            continue
        by_run.setdefault(r["runId"], []).append((m, r["scores"]))
    for run_id, js in by_run.items():
        if run_id not in meta:
            continue
        md = meta[run_id]
        dim_means = {}
        for d in DIMS:
            vals = [s[d] for _, s in js if isinstance(s.get(d), (int, float))]
            dim_means[d] = float(np.mean(vals)) if vals else np.nan
        tier, structure, persona = md["cell"].split("-")
        rows.append({
            "runId": run_id, "problemId": md["problemId"], "cell": md["cell"],
            "tier": tier, "structure": structure, "persona": persona,
            "family": md["family"], "n_judg": len(js),
            "composite": float(np.mean([x[0] for x in js])),
            "capped": bool(md.get("cappedAt16012")),
            "fulltextLen": md.get("fulltextLen", np.nan),
            **{f"d_{d}": dim_means[d] for d in DIMS},
        })
    return pd.DataFrame(rows)


def welch_two(a, b):
    """Welch t on two independent samples; returns t, df, p, pooled-SD d."""
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(va / na + vb / nb)
    t = (a.mean() - b.mean()) / se if se > 0 else np.nan
    df = se ** 4 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    p = 2 * stats.t.sf(abs(t), df)
    pooled = math.sqrt(np.concatenate([a, b]).var(ddof=1))
    d = (a.mean() - b.mean()) / pooled if pooled > 0 else np.nan
    return t, df, p, d, na + nb


def interaction_stats(df):
    """H1 contrast d=(FT-FS)-(CT-CS); returns dict with t, df, p, d_std, cells."""
    cells = {}
    for t in ("F", "C"):
        for s in ("T", "S"):
            x = df[(df.tier == t) & (df.structure == s)]["composite"].to_numpy()
            if len(x) < 2:
                return None
            cells[(t, s)] = x
    contrast = (cells[("F", "T")].mean() - cells[("F", "S")].mean()
                - cells[("C", "T")].mean() + cells[("C", "S")].mean())
    se = math.sqrt(sum(x.var(ddof=1) / len(x) for x in cells.values()))
    t = contrast / se if se > 0 else np.nan
    df_w = se ** 4 / sum((x.var(ddof=1) / len(x)) ** 2 / (len(x) - 1) for x in cells.values())
    p = 2 * stats.t.sf(abs(t), df_w)
    pooled = math.sqrt(np.concatenate(list(cells.values())).var(ddof=1))
    return {"contrast": contrast, "t": t, "df": df_w, "p": p,
            "d_std": contrast / pooled, "n": sum(len(x) for x in cells.values()),
            "cells": cells}


def boot_ci_interaction(df, n_boot=BOOT_N, seed=BOOT_SEED):
    rng = np.random.default_rng(seed)
    cells = {(t, s): df[(df.tier == t) & (df.structure == s)]["composite"].to_numpy()
             for t in ("F", "C") for s in ("T", "S")}
    if any(len(x) < 2 for x in cells.values()):
        return None
    ds = []
    for _ in range(n_boot):
        b = {k: rng.choice(x, size=len(x), replace=True) for k, x in cells.items()}
        c = (b[("F", "T")].mean() - b[("F", "S")].mean()
             - b[("C", "T")].mean() + b[("C", "S")].mean())
        pooled = np.concatenate(list(b.values())).std(ddof=1)
        if pooled > 0:
            ds.append(c / pooled)
    return float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))


def boot_ci_two(a, b, n_boot=BOOT_N, seed=BOOT_SEED):
    rng = np.random.default_rng(seed)
    ds = []
    for _ in range(n_boot):
        ba = rng.choice(a, size=len(a), replace=True)
        bb = rng.choice(b, size=len(b), replace=True)
        pooled = np.concatenate([ba, bb]).std(ddof=1)
        if pooled > 0:
            ds.append((ba.mean() - bb.mean()) / pooled)
    return float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))


def jzs_bf(t, n_eff, df, r=R_JZS):
    """Rouder JZS Bayes factor BF10 for a t contrast (numerical integration).
    BF10 = num / den, den = (1 + t^2/df)^(-(df+1)/2);
    num = int_0^inf (1+N r^2 g)^(-1/2) (1 + t^2/((1+N r^2 g) df))^(-(df+1)/2)
          * (2pi)^(-1/2) g^(-3/2) exp(-1/(2g)) dg.
    """
    den = (1 + t ** 2 / df) ** (-(df + 1) / 2)

    def integrand(g):
        if g <= 0:
            return 0.0
        v = 1 + n_eff * r ** 2 * g
        return (v ** -0.5
                * (1 + t ** 2 / (v * df)) ** (-(df + 1) / 2)
                * (2 * math.pi) ** -0.5 * g ** -1.5 * math.exp(-1 / (2 * g)))
    num, _ = quad(integrand, 0, np.inf, limit=200)
    return num / den if den > 0 else np.nan


def sensitivity_power(n_per_group, alpha, power=0.80):
    """A2.7: minimum detectable d at given power for two equal-sized groups."""
    return TTestIndPower().solve_power(effect_size=None, nobs1=n_per_group,
                                       ratio=1.0, alpha=alpha, power=power)


def main():
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    meta = {r["runId"]: r for r in store["runs"] if r.get("fulltext")}
    judgeable = len(meta)
    recs, n_bad = load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    t = build_run_table(recs, meta)
    out = {"amendment": "A2 (author-approved 2026-08-05)",
           "integrity": {
               "judgeable_runs": judgeable, "runs_with_judgments": len(t),
               "judgment_records": len(recs), "dropped_error_incomplete": n_bad,
               "complete": len(t) == judgeable}}

    # ---------------- PRIMARY LAYER (pre-registered) ----------------
    ix = interaction_stats(t)
    out["primary"] = {}
    if ix:
        ci = boot_ci_interaction(t)  # A2.1
        bf = jzs_bf(ix["t"], ix["n"] / 4, ix["df"])  # A2.4 (contrast n_eff approx)
        out["primary"]["H1_tier_x_structure_interaction"] = {
            "d": round(ix["d_std"], 4), "contrast": round(ix["contrast"], 4),
            "t": round(ix["t"], 3), "df": round(ix["df"], 1), "p": round(ix["p"], 5),
            "n": ix["n"], "bootstrap95CI": [round(ci[0], 4), round(ci[1], 4)] if ci else None,
            "BF10_JZS": round(bf, 3),
            "passes_interim2_boundary": abs(ix["t"]) >= INTERIM2_Z_BOUNDARY}
    # main effects
    for name, (a_sel, b_sel) in {
        "tier_F_minus_C": ((t.tier == "F"), (t.tier == "C")),
        "structure_T_minus_S": ((t.structure == "T"), (t.structure == "S")),
        "persona_P_minus_N": ((t.persona == "P"), (t.persona == "N")),
    }.items():
        a, b = t[a_sel].composite.to_numpy(), t[b_sel].composite.to_numpy()
        tv, dfv, pv, dv, nv = welch_two(a, b)
        ci = boot_ci_two(a, b)
        out["primary"][name] = {
            "d": round(dv, 4), "t": round(tv, 3), "p": round(pv, 5), "n": nv,
            "bootstrap95CI": [round(ci[0], 4), round(ci[1], 4)],
            "BF10_JZS": round(jzs_bf(tv, (len(a) * len(b)) / (len(a) + len(b)), dfv), 3)}

    # ---------------- A2.3 factorial ANOVA + eta^2 ----------------
    import statsmodels.api as sm
    aov = smf.ols("composite ~ C(tier)*C(structure)*C(persona)", data=t).fit()
    at = sm.stats.anova_lm(aov, typ=2)
    rss = at.loc["Residual", "sum_sq"]
    out["A2_3_anova"] = {
        "terms": {i: {"F": round(r.F, 3), "p": round(r["PR(>F)"], 5),
                      "partial_eta2": round(r.sum_sq / (r.sum_sq + rss), 4)}
                  for i, r in at.iterrows() if i != "Residual"},
        "shapiro_resid_p": round(stats.shapiro(aov.resid[:5000])[1], 5),
        "levene_p": round(stats.levene(*[g.composite.to_numpy()
                                          for _, g in t.groupby("cell")])[1], 5)}

    # ---------------- A2.2 FDR on secondary families ----------------
    secondary = []
    for d in DIMS:  # per-dimension persona contrasts
        a = t[t.persona == "P"][f"d_{d}"].to_numpy()
        b = t[t.persona == "N"][f"d_{d}"].to_numpy()
        _, _, p, dv, nv = welch_two(a, b)
        secondary.append({"test": f"persona_{d}", "d": dv, "p": p, "n": nv})
    for f, sub in t.groupby("family"):  # per-family interactions
        r = interaction_stats(sub)
        if r:
            secondary.append({"test": f"interaction_{f}", "d": r["d_std"],
                              "p": r["p"], "n": r["n"]})
    for p_ in ("N", "P"):  # interaction within persona level
        r = interaction_stats(t[t.persona == p_])
        if r:
            secondary.append({"test": f"interaction_persona_{p_}", "d": r["d_std"],
                              "p": r["p"], "n": r["n"]})
    ps = [s["p"] for s in secondary]
    _, padj, _, _ = multipletests(ps, alpha=0.05, method="fdr_bh")
    for s, q in zip(secondary, padj):
        s["d"] = round(s["d"], 4); s["p"] = round(s["p"], 5)
        s["p_fdr"] = round(q, 5); s["sig_fdr"] = bool(q < 0.05)
    out["A2_2_secondary_fdr"] = secondary

    # ---------------- A2.5 leave-one-family-out ----------------
    loo_f = []
    for f in t.family.unique():
        r = interaction_stats(t[t.family != f])
        if r:
            loo_f.append({"removed": f, "d": round(r["d_std"], 4),
                          "p": round(r["p"], 5), "n": r["n"]})
    full_d = ix["d_std"] if ix else np.nan
    out["A2_5_leave_one_family_out"] = {
        "full_d": round(full_d, 4), "folds": loo_f,
        "max_abs_change": round(max(abs(x["d"] - full_d) for x in loo_f), 4),
        "sign_stable": bool(all(np.sign(x["d"]) == np.sign(full_d) for x in loo_f))}

    # ---------------- A2.6 leave-one-problem-out ----------------
    loo_p = []
    for pid in sorted(t.problemId.unique()):
        r = interaction_stats(t[t.problemId != pid])
        if r:
            loo_p.append({"removed": pid, "d": round(r["d_std"], 4), "p": round(r["p"], 5)})
    out["A2_6_leave_one_problem_out"] = {
        "folds": loo_p,
        "max_abs_change": round(max(abs(x["d"] - full_d) for x in loo_p), 4),
        "sign_stable": bool(all(np.sign(x["d"]) == np.sign(full_d) for x in loo_p))}

    # ---------------- A2.7 sensitivity power ----------------
    n_cell = t.groupby("cell").size()
    out["A2_7_sensitivity_power"] = {
        "per_cell_n": n_cell.to_dict(),
        "min_detectable_d_at_80pct": round(sensitivity_power(int(n_cell.min()), 0.05), 4)}

    # ---------------- A1.4 legacy: length-adjusted interaction ----------------
    reg = t.assign(loglen=np.log(t.fulltextLen),
                   tier=t.tier.map({"F": 1, "C": 0}),
                   structure=t.structure.map({"T": 1, "S": 0}),
                   persona=t.persona.map({"P": 1, "N": 0}))
    m_u = smf.ols("composite ~ tier*structure*persona", data=reg).fit(cov_type="HC1")
    m_a = smf.ols("composite ~ tier*structure*persona + loglen", data=reg).fit(cov_type="HC1")
    out["A1_4_length_adjustment"] = {
        "unadjusted": {"coef": round(m_u.params["tier:structure"], 4),
                       "p": round(m_u.pvalues["tier:structure"], 5)},
        "length_adjusted": {"coef": round(m_a.params["tier:structure"], 4),
                            "p": round(m_a.pvalues["tier:structure"], 5)}}

    # ---------------- inter-judge agreement ----------------
    per_judge = {}
    for r in recs:
        m = judgment_mean(r["scores"])
        if m is not None:
            per_judge.setdefault(r["judge_family"], {}).setdefault(r["runId"], []).append(m)
    jp = pd.DataFrame({j: pd.Series({k: float(np.mean(v)) for k, v in dd.items()})
                       for j, dd in per_judge.items()})
    out["inter_judge_r"] = {f"{a}~{b}": round(np.corrcoef(jp[a], jp[b])[0, 1], 3)
                            for a in jp.columns for b in jp.columns if a < b}

    res_path = ROOT / "results/interim2_analysis.json"
    json.dump(out, open(res_path, "w"), indent=2, default=str)
    print(json.dumps(out, indent=2, default=str))
    print(f"\nsaved -> {res_path}")


if __name__ == "__main__":
    main()
