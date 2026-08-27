#!/usr/bin/env python3
"""Amendment A3 — exploratory advanced statistics on the LOCKED interim-2 data.

Read-only: loads runs/fulltext/main_fulltext.json + runs/logs/main_judgments.jsonl,
writes results/exploratory_analysis.json. See protocols/07-AMENDMENT-A3.

A3.1 LMM with random intercepts (problem, family)
A3.2 TOST equivalence on the no-persona H1 contrast (SESOI d = 0.20)
A3.3 Empirical-Bayes partial pooling across families
A3.4 Random-effects meta-analysis across families (DerSimonian-Laird)
A3.5 Dimension decomposition of the persona effect (BH-FDR)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import analyze_main as am  # noqa: E402

SEED = 42
N_BOOT = 1000
SESOI = 0.20  # A3.2 equivalence bound in standardized units (analyst choice, disclosed)


def _cell_codes(sub: pd.DataFrame) -> np.ndarray:
    """FT=1, FS=0, CT=3, CS=2."""
    tier = (sub["tier"] == "C").to_numpy().astype(np.int64)
    struct = (sub["structure"] == "T").to_numpy().astype(np.int64)
    return tier * 2 + struct


def contrast_raw(sub: pd.DataFrame) -> float:
    m = {(t, s): sub[(sub.tier == t) & (sub.structure == s)]["composite"].mean()
         for t in ("F", "C") for s in ("T", "S")}
    return (m[("F", "T")] - m[("F", "S")]) - (m[("C", "T")] - m[("C", "S")])


def boot_d_se(sub: pd.DataFrame, n_boot=N_BOOT, seed=SEED):
    """Bootstrap d and SE of the H1 contrast for a subset (numpy-fast)."""
    rng = np.random.default_rng(seed)
    y = sub["composite"].to_numpy(dtype=np.float64)
    codes = _cell_codes(sub)
    sd = float(np.std(y, ddof=1))
    n = len(y)
    ds = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        sums = np.bincount(codes[idx], weights=y[idx], minlength=4)
        cnts = np.bincount(codes[idx], minlength=4)
        cnts[cnts == 0] = 1
        means = sums / cnts
        ds[i] = ((means[1] - means[0]) - (means[3] - means[2])) / sd
    return float(np.mean(ds)), float(np.std(ds, ddof=1))


def a3_1_lmm(df):
    """Mixed model per protocol 03 sec 4."""
    out = {}
    try:
        m = smf.mixedlm("composite ~ C(tier)*C(structure)*C(persona)", df,
                        groups="problem",
                        vc_formula={"family": "0 + C(family)"}).fit(reml=True)
        out["model"] = "groups=problem, vc=family"
        pv = m.pvalues
        out["fe"] = {k: {"coef": round(float(m.fe_params[k]), 4),
                         "p": round(float(pv[k]), 5) if k in pv.index else None}
                     for k in m.fe_params.index}
        var = m.cov_re.iloc[0, 0] if m.cov_re.size else 0.0
        vc = float(np.sum(list(m.vcomp))) if hasattr(m, "vcomp") and m.vcomp is not None else 0.0
        out["var_components"] = {"problem": round(float(var), 4),
                                 "family_vc": round(vc, 4),
                                 "residual": round(float(m.scale), 4)}
    except Exception as e:  # fallback: family as second grouping via concat id
        out["model_error"] = str(e)[:200]
        df2 = df.copy()
        df2["pf"] = df2["problemId"] + "|" + df2["family"]
        m = smf.mixedlm("composite ~ C(tier)*C(structure)*C(persona)", df2,
                        groups="pf").fit(reml=True)
        out["model"] = "groups=problem|family (fallback)"
        pv = m.pvalues
        out["fe"] = {k: {"coef": round(float(m.fe_params[k]), 4),
                         "p": round(float(pv[k]), 5) if k in pv.index else None}
                     for k in m.fe_params.index}
    return out


def a3_2_tost(df):
    """TOST on the H1 contrast restricted to persona=N (bounds +-SESOI)."""
    sub = df[df.persona == "N"]
    d_hat, se = boot_d_se(sub)
    t_lo = (d_hat - (-SESOI)) / se   # H01: d <= -SESOI
    t_hi = (d_hat - SESOI) / se      # H02: d >= +SESOI
    dof = len(sub) - 4
    p = max(stats.t.sf(t_lo, dof), stats.t.cdf(t_hi, dof))
    return {"subset": "persona=N", "n": len(sub), "d": round(d_hat, 4),
            "se_boot": round(se, 4), "bounds": [-SESOI, SESOI],
            "p_tost": round(float(p), 5),
            "equivalent": bool(p < 0.05),
            "interpretation": ("equivalence established: interaction is "
                               "practically absent without personas"
                               if p < 0.05 else
                               "equivalence NOT established: null remains unproven")}


def a3_3_4_families(df):
    """Per-family d + SE via bootstrap, then empirical-Bayes pooling and DL meta."""
    fams = sorted(df.family.unique())
    rows = {}
    for f in fams:
        d, se = boot_d_se(df[df.family == f])
        rows[f] = {"d": d, "se": se}
    d_arr = np.array([rows[f]["d"] for f in fams])
    se_arr = np.array([rows[f]["se"] for f in fams])

    # DerSimonian-Laird tau^2
    w_fixed = 1 / se_arr ** 2
    mu_fixed = float(np.sum(w_fixed * d_arr) / np.sum(w_fixed))
    Q = float(np.sum(w_fixed * (d_arr - mu_fixed) ** 2))
    k = len(fams)
    C = float(np.sum(w_fixed) - np.sum(w_fixed ** 2) / np.sum(w_fixed))
    tau2 = max(0.0, (Q - (k - 1)) / C)
    I2 = max(0.0, (Q - (k - 1)) / Q) * 100 if Q > 0 else 0.0
    w_re = 1 / (se_arr ** 2 + tau2)
    mu_re = float(np.sum(w_re * d_arr) / np.sum(w_re))
    se_re = float(1 / np.sqrt(np.sum(w_re)))
    z = mu_re / se_re

    # Empirical-Bayes shrinkage toward the RE pooled mean
    shrunk = {}
    for f, d, se in zip(fams, d_arr, se_arr):
        lam = tau2 / (tau2 + se ** 2) if tau2 > 0 else 0.0
        shrunk[f] = round(float(lam * d + (1 - lam) * mu_re), 4)

    return {
        "per_family": {f: {"d": round(rows[f]["d"], 4), "se_boot": round(rows[f]["se"], 4)}
                       for f in fams},
        "meta": {"k": k, "Q": round(Q, 3), "tau2": round(tau2, 4),
                 "I2_pct": round(I2, 1),
                 "pooled_d": round(mu_re, 4), "se": round(se_re, 4),
                 "z": round(z, 3), "p": round(float(2 * stats.norm.sf(abs(z))), 5),
                 "ci95": [round(mu_re - 1.96 * se_re, 4),
                          round(mu_re + 1.96 * se_re, 4)]},
        "empirical_bayes_shrunk_d": shrunk,
    }


def a3_5_dimensions(df):
    """Per-dimension P-N effects with BH-FDR."""
    out = []
    for d_name in am.DIMS:
        col = f"d_{d_name}"
        p_vals = df[df.persona == "P"][col].dropna().to_numpy()
        n_vals = df[df.persona == "N"][col].dropna().to_numpy()
        _, p = stats.ttest_ind(p_vals, n_vals, equal_var=False)
        pooled = np.sqrt(((len(p_vals) - 1) * np.var(p_vals, ddof=1)
                          + (len(n_vals) - 1) * np.var(n_vals, ddof=1))
                         / (len(p_vals) + len(n_vals) - 2))
        d_eff = (np.mean(p_vals) - np.mean(n_vals)) / pooled if pooled > 0 else np.nan
        out.append({"dimension": d_name, "d_P_minus_N": round(float(d_eff), 4),
                    "p": round(float(p), 6)})
    _, p_fdr, _, _ = multipletests([r["p"] for r in out], method="fdr_bh")
    for r, pf in zip(out, p_fdr):
        r["p_fdr"] = round(float(pf), 6)
        r["sig_fdr"] = bool(pf < 0.05)
    return out


def main():
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    meta = {r["runId"]: r for r in store["runs"] if r.get("fulltext")}
    recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    df = pd.DataFrame(am.build_run_table(recs, meta))
    out = {
        "amendment": "A3 (author-approved 2026-08-06, EXPLORATORY)",
        "n_runs": len(df),
        "A3_1_lmm": a3_1_lmm(df),
        "A3_2_tost_no_persona": a3_2_tost(df),
    }
    fam_results = a3_3_4_families(df)
    out["A3_3_empirical_bayes"] = {
        "shrunk_d": fam_results["empirical_bayes_shrunk_d"],
        "pooled_d": fam_results["meta"]["pooled_d"],
        "note": "empirical-Bayes substitute for full MCMC (pymc unavailable)",
    }
    out["A3_4_meta_analysis"] = fam_results["meta"] | {
        "per_family": fam_results["per_family"]}
    out["A3_5_persona_dimensions"] = a3_5_dimensions(df)
    dst = ROOT / "results" / "exploratory_analysis.json"
    dst.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"saved -> {dst}")
    print(json.dumps({k: out[k] for k in ("A3_2_tost_no_persona", "A3_4_meta_analysis")},
                     indent=1))


if __name__ == "__main__":
    main()
