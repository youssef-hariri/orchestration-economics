#!/usr/bin/env python3
"""Pilot v2 re-judge analysis (Amendment A1.5).

Compares the artifact-corrected v2 judgments (full-text stimulus,
max_tokens 2048, completeness gate) against the frozen v1 judgments:
  - 8-cell means, tier x structure interaction contrast (overall / by
    family / truncated vs non-truncated subsets)
  - persona main effect + per-dimension P-N decomposition
  - v1 vs v2 agreement (run-level composite correlation)
  - A1.4 length sensitivity: family-specific length-quality r and
    log(length)-adjusted interaction (OLS)
Exploratory/descriptive only - pilot never enters confirmatory inference (D31/D32).
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]


def load_jsonl(path):
    recs = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        recs.append(json.loads(line))
    return recs


def load_judgments(paths, dedupe=False, skip_bad=False):
    recs = []
    for p in paths:
        recs += load_jsonl(p)
    if dedupe:  # resumable harness appends retries; last record per key wins
        last = {}
        for r in recs:
            last[(r["runId"], r["judge_family"], r["variant"])] = r
        recs = list(last.values())
    if skip_bad:
        recs = [r for r in recs if not r.get("error") and not r.get("incomplete")]
    return recs


def judgment_mean(scores):
    vals = [v for v in scores.values() if isinstance(v, (int, float))]
    return float(np.mean(vals)) if vals else None


def build_run_table(recs, meta):
    """run-level composite DV + per-dimension means."""
    rows = []
    by_run = {}
    for r in recs:
        m = judgment_mean(r.get("scores") or {})
        if m is None:
            continue
        by_run.setdefault(r["runId"], []).append((m, r["scores"]))
    for run_id, js in by_run.items():
        if run_id not in meta:
            continue
        md = meta[run_id]
        comp = float(np.mean([x[0] for x in js]))
        dim_means = {}
        for d in DIMS:
            vals = [s[d] for _, s in js if isinstance(s.get(d), (int, float))]
            dim_means[d] = float(np.mean(vals)) if vals else np.nan
        cell = md["cell"]  # e.g. "F-T-P"
        tier, structure, persona = cell.split("-")
        rows.append({
            "runId": run_id, "problemId": md["problemId"], "cell": cell,
            "tier": tier, "structure": structure, "persona": persona,
            "family": md["family"], "n_judg": len(js), "composite": comp,
            "capped": bool(md.get("cappedAt16012")),
            "fulltextLen": md.get("fulltextLen", np.nan),
            "recovered": bool(md.get("cappedAt16012")) and md.get("fulltextLen", 0) > 16012,
            **{f"d_{d}": dim_means[d] for d in DIMS},
        })
    return pd.DataFrame(rows)


def interaction_contrast(df, label):
    """d = (FT - FS) - (CT - CS) on run-level composites."""
    cells = {}
    for t in ("F", "C"):
        for s in ("T", "S"):
            x = df[(df.tier == t) & (df.structure == s)]["composite"].to_numpy()
            if len(x) == 0:
                return None
            cells[(t, s)] = x
    contrast = (cells[("F", "T")].mean() - cells[("F", "S")].mean()
                - cells[("C", "T")].mean() + cells[("C", "S")].mean())
    se = math.sqrt(sum(x.var(ddof=1) / len(x) for x in cells.values()))
    t_stat = contrast / se if se > 0 else np.nan
    df_welch = se ** 4 / sum((x.var(ddof=1) / len(x)) ** 2 / (len(x) - 1) for x in cells.values())
    p = 2 * stats.t.sf(abs(t_stat), df_welch)
    pooled_sd = math.sqrt(np.concatenate(list(cells.values())).var(ddof=1))
    d_std = contrast / pooled_sd
    n = sum(len(x) for x in cells.values())
    return {"label": label, "n": n, "contrast": round(contrast, 4),
            "d_std": round(d_std, 4), "t": round(t_stat, 3), "p": round(p, 4)}


def main():
    store = json.load(open(ROOT / "runs/fulltext/pilot_fulltext.json"))
    meta = {r["runId"]: r for r in store["runs"]}

    v2 = load_judgments([ROOT / "runs/logs/pilot_v2_judgments.jsonl"],
                        dedupe=True, skip_bad=True)
    v1 = load_judgments([ROOT / "runs/logs/pilot_phaseA_judgments.jsonl",
                         ROOT / "runs/logs/pilot_phaseB_judgments.jsonl"])
    v1_ok = [r for r in v1 if not r.get("error")]

    out = {}
    out["integrity"] = {
        "v2_records_kept": len(v2),
        "v1_records": len(v1_ok),
        "v1_null_dim_scores": sum(
            1 for r in v1_ok for v in (r.get("scores") or {}).values()
            if not isinstance(v, (int, float))),
        "v2_null_dim_scores": sum(
            1 for r in v2 for v in (r.get("scores") or {}).values()
            if not isinstance(v, (int, float))),
        "v2_audited_incomplete": 2,  # run 997 meta var2/var3 (format non-compliance)
    }

    t2 = build_run_table(v2, meta)
    t1 = build_run_table(v1_ok, meta)
    out["runs"] = {"v1": len(t1), "v2": len(t2)}

    # ---- 8-cell means -------------------------------------------------
    def cell_means(df):
        g = df.groupby("cell")["composite"].agg(["mean", "std", "count"])
        return g.round(3).to_dict("index")
    out["cell_means_v2"] = cell_means(t2)
    out["cell_means_v1"] = cell_means(t1)

    # ---- interaction contrast ------------------------------------------
    rows = [interaction_contrast(t2, "v2 all"),
            interaction_contrast(t1, "v1 all"),
            interaction_contrast(t2[~t2.capped], "v2 non-capped"),
            interaction_contrast(t2[t2.capped], "v2 capped"),
            interaction_contrast(t1[~t1.capped], "v1 non-capped"),
            interaction_contrast(t1[t1.capped], "v1 capped")]
    out["interaction"] = [r for r in rows if r]

    # by family (v2)
    fam = []
    for f, sub in t2.groupby("family"):
        r = interaction_contrast(sub, f"v2 {f}")
        if r:
            fam.append(r)
    out["interaction_by_family_v2"] = fam

    # within persona levels (v2)
    out["interaction_by_persona_v2"] = [
        interaction_contrast(t2[t2.persona == p], f"v2 persona={p}") for p in ("N", "P")]

    # ---- persona main effect + per-dimension decomposition -------------
    def dim_diff(df):
        p = df[df.persona == "P"]; n = df[df.persona == "N"]
        res = {}
        for d in DIMS:
            res[d] = round(p[f"d_{d}"].mean() - n[f"d_{d}"].mean(), 3)
        res["composite"] = round(p["composite"].mean() - n["composite"].mean(), 3)
        return res
    out["persona_PminusN_v2"] = dim_diff(t2)
    out["persona_PminusN_v1"] = dim_diff(t1)

    # ---- v1 vs v2 agreement ---------------------------------------------
    m = t1[["runId", "composite"]].merge(t2[["runId", "composite"]],
                                          on="runId", suffixes=("_v1", "_v2"))
    out["v1_vs_v2"] = {
        "n_runs": len(m),
        "pearson_r": round(np.corrcoef(m.composite_v1, m.composite_v2)[0, 1], 4),
        "spearman_rho": round(stats.spearmanr(m.composite_v1, m.composite_v2)[0], 4),
        "mean_shift_v2_minus_v1": round((m.composite_v2 - m.composite_v1).mean(), 4),
    }
    # does v1-vs-v2 shift track truncation?
    m2 = m.merge(t2[["runId", "capped"]], on="runId")
    out["v1_vs_v2_shift_by_capped"] = {
        "capped": round((m2[m2.capped].composite_v2 - m2[m2.capped].composite_v1).mean(), 4),
        "non_capped": round((m2[~m2.capped].composite_v2 - m2[~m2.capped].composite_v1).mean(), 4),
    }

    # ---- A1.4 length sensitivity ----------------------------------------
    lr = {}
    for f, sub in t2.groupby("family"):
        r, p = stats.pearsonr(np.log(sub.fulltextLen), sub.composite)
        lr[f] = {"r_loglen_quality": round(r, 3), "p": round(p, 4), "n": len(sub)}
    r_all, p_all = stats.pearsonr(np.log(t2.fulltextLen), t2.composite)
    lr["ALL"] = {"r_loglen_quality": round(r_all, 3), "p": round(p_all, 4), "n": len(t2)}
    out["length_quality_r_v2"] = lr

    df_reg = t2.assign(loglen=np.log(t2.fulltextLen),
                       tier=t2.tier.map({"F": 1, "C": 0}),
                       structure=t2.structure.map({"T": 1, "S": 0}),
                       persona=t2.persona.map({"P": 1, "N": 0}))
    m_unadj = smf.ols("composite ~ tier*structure*persona", data=df_reg).fit(cov_type="HC1")
    m_adj = smf.ols("composite ~ tier*structure*persona + loglen", data=df_reg).fit(cov_type="HC1")
    out["ols_interaction_tierXstructure"] = {
        "unadjusted": {"coef": round(m_unadj.params["tier:structure"], 4),
                       "p": round(m_unadj.pvalues["tier:structure"], 4)},
        "length_adjusted": {"coef": round(m_adj.params["tier:structure"], 4),
                            "p": round(m_adj.pvalues["tier:structure"], 4)},
    }

    # ---- inter-judge agreement (v2, run-level dim means per judge) ------
    per_judge = {}
    for r in v2:
        m_ = judgment_mean(r["scores"])
        if m_ is not None:
            per_judge.setdefault(r["judge_family"], {}).setdefault(r["runId"], []).append(m_)
    jj = {j: pd.Series({k: float(np.mean(v)) for k, v in d.items()})
          for j, d in per_judge.items()}
    jp = pd.DataFrame(jj)
    pairs = {}
    for a in jp.columns:
        for b in jp.columns:
            if a < b:
                pairs[f"{a}~{b}"] = round(np.corrcoef(jp[a], jp[b])[0, 1], 3)
    out["inter_judge_r_v2"] = pairs

    res_path = ROOT / "results/pilot_v2_analysis.json"
    json.dump(out, open(res_path, "w"), indent=2, default=str)
    print(json.dumps(out, indent=2, default=str))
    print(f"\nsaved -> {res_path}")


if __name__ == "__main__":
    main()
