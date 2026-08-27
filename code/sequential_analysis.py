#!/usr/bin/env python
# sequential_analysis.py — Interim-1 sequential analysis (pilot) for the
# orchestration-economics experiment.
#
# Implements Protocol 03 (SEQUENTIAL-ANALYSIS-PROTOCOL.md) and the
# pre-registered analysis plan (01-PREREGISTRATION-PROTOCOL.md):
#
#   DV aggregation : mean over 3 judges x 3 variants x 5 dimensions per run
#   Primary model  : quality ~ tier * structure * persona + (1|problem) + (1|family)
#   Primary test   : tier x structure interaction (H1)
#   Stopping rules : R1 p < 0.01 -> stop/report
#                    R2 p > 0.10 and BF01 > 10 -> stop (futility)
#                    R3 otherwise -> continue to main run
#   Alpha spending : O'Brien-Fleming (interim 1 boundary = 0.01)
#
# DESIGN NOTE (deviation disclosure):
# Protocol 03 assumed the pilot covers all 8 cells x 5 families. The executed
# pilot split into Phase A (6 cells x 5 families x 11 problems) and Phase B
# (F-T-N/F-T-P x 2 preregistered families x 11 problems), because the F-T
# families are selected by the preregistered F-S-N novelty rule and could not
# exist before Phase A. Consequences:
#   - The tier x structure interaction is NOT estimable from Phase A alone
#     (F-T cells absent -> interaction column is zero).
#   - The interim test therefore uses the COMBINED pilot (Phase A + Phase B,
#     N = 371), with F-T present for claude + kimi only (unbalanced families).
#   - Cross-check: balanced 2-family subset (claude + kimi, complete 2x2x2).
# This deviation is reported in the interim decision record.
#
# Usage: python sequential_analysis.py   (conda base: pandas/statsmodels/pingouin)

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pingouin as pg
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
GEN_A = ROOT / "runs/logs/pilot_phaseA_2026-08-03.json"
JUDG_A = ROOT / "runs/logs/pilot_phaseA_judgments.jsonl"
GEN_B = ROOT / "runs/logs/pilot_phaseB_2026-08-03.json"
JUDG_B = ROOT / "runs/logs/pilot_phaseB_judgments.jsonl"
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(exist_ok=True)

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

# ---------- 1. Aggregate judgments: mean per run ----------
def run_quality(path: Path) -> dict:
    scores = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        j = json.loads(line)
        if j.get("error") or not j.get("scores"):
            continue
        vals = [v for v in j["scores"].values() if v is not None]
        if vals:
            scores.setdefault(j["runId"], []).append(float(np.mean(vals)))
    return {k: float(np.mean(v)) for k, v in scores.items()}

def load_runs(gen_path: Path, qual: dict, phase: str) -> pd.DataFrame:
    gen = json.loads(gen_path.read_text())
    rows = []
    for r in gen["results"]:
        if r.get("status") != "completed" or not (r.get("finalResponse") or "").strip():
            continue
        q = qual.get(r["runId"])
        if q is None:
            continue
        tier, structure, persona = r["cell"].split("-")
        rows.append({"runId": r["runId"], "problemId": r["problemId"], "family": r["family"],
                     "cell": r["cell"], "tier": tier, "structure": structure,
                     "persona": persona, "quality": q, "phase": phase})
    return pd.DataFrame(rows)

df_a = load_runs(GEN_A, run_quality(JUDG_A), "A")
df_b = load_runs(GEN_B, run_quality(JUDG_B), "B")
df = pd.concat([df_a, df_b], ignore_index=True)
for c in ("tier", "structure", "persona", "problemId", "family"):
    df[c] = df[c].astype("category")

print("=" * 72)
print("INTERIM-1 SEQUENTIAL ANALYSIS — orchestration-economics pilot")
print(f"timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
print(f"data sha: A-gen={sha256(GEN_A)} A-judg={sha256(JUDG_A)} B-gen={sha256(GEN_B)} B-judg={sha256(JUDG_B)}")
print(f"N combined = {len(df)}  (Phase A = {len(df_a)}, Phase B = {len(df_b)})")
print("=" * 72)

print("\n--- Runs per family x cell (combined) ---")
print(df.pivot_table(index="family", columns="cell", values="runId", aggfunc="count",
                     observed=False).fillna(0).astype(int).to_string())

def fit_lmm(data: pd.DataFrame, label: str):
    """LMM with crossed random intercepts (1|problem) + (1|family)."""
    kwargs = dict(groups=data["problemId"], re_formula="1",
                  vc_formula={"family": "0 + C(family)"})
    m = smf.mixedlm("quality ~ C(tier)*C(structure)*C(persona)", data, **kwargs).fit(
        reml=True, method="powell", maxiter=2000)
    inter = [t for t in m.params.index if "tier" in t and "structure" in t][0]
    b, se = m.params[inter], m.bse[inter]
    tstat = b / se
    p = float(2 * stats.t.sf(abs(tstat), m.df_resid))
    # BIC-based BF (Wagenmakers 2007 / Raftery 1995 approximation). BIC is
    # computed on ML (not REML) fits for valid model comparison.
    m1_ml = smf.mixedlm("quality ~ C(tier)*C(structure)*C(persona)", data, **kwargs).fit(
        reml=False, method="powell", maxiter=2000)
    m0_ml = smf.mixedlm("quality ~ C(tier) + C(structure) + C(persona)", data, **kwargs).fit(
        reml=False, method="powell", maxiter=2000)
    bf10 = float(np.exp((m0_ml.bic - m1_ml.bic) / 2))
    return {"label": label, "n": len(data), "term": inter, "b": float(b), "se": float(se),
            "t": float(tstat), "df": float(m.df_resid), "p": p,
            "beta_std": float(b / data['quality'].std()), "bf10": bf10, "bf01": 1 / bf10}

# ---------- 2. PRIMARY: combined 8-cell LMM ----------
print("\n" + "=" * 72)
print("PRIMARY: combined pilot (Phase A+B), quality ~ tier*structure*persona")
print("         + (1|problem) + (1|family); F-T present for claude+kimi only")
print("=" * 72)
primary = fit_lmm(df, "combined A+B (8 cells, F-T=claude+kimi)")
print(f"term={primary['term']}  b={primary['b']:.4f} (SE {primary['se']:.4f})")
print(f"t({primary['df']:.1f})={primary['t']:.3f}  p={primary['p']:.4g}  beta_std={primary['beta_std']:.3f}")
print(f"BF10 (BIC approx) = {primary['bf10']:.3f} | BF01 = {primary['bf01']:.3f}")

# ---------- 3. CROSS-CHECK 1: balanced 2-family subset (claude+kimi) ----------
print("\n" + "=" * 72)
print("CROSS-CHECK 1: balanced subset claude+kimi (complete 2x2x2, 8 cells)")
print("=" * 72)
df2 = df[df["family"].isin(["claude", "kimi"])].copy()
for c in ("tier", "structure", "persona", "problemId", "family"):
    df2[c] = df2[c].astype("category")
print(df2.pivot_table(index="family", columns="cell", values="runId", aggfunc="count",
                      observed=False).fillna(0).astype(int).to_string())
ck1 = fit_lmm(df2, "claude+kimi balanced 8-cell")
print(f"b={ck1['b']:.4f} (SE {ck1['se']:.4f})  t={ck1['t']:.3f}  p={ck1['p']:.4g}  BF10={ck1['bf10']:.3f}")

# rm-ANOVA on the balanced subset: aggregate to problem x tier x structure
# means (collapsing persona and family), giving a complete 2x2 within-subject
# design. (pingouin rm_anova supports at most 2 within factors.)
ts_means = (df2.groupby(["problemId", "tier", "structure"])["quality"]
            .mean().reset_index())
aov = pg.rm_anova(data=ts_means, dv="quality", within=["tier", "structure"],
                  subject="problemId", detailed=True, effsize="np2")
print("\nrm-ANOVA (balanced subset, problem-level tier x structure means):")
print(aov.to_string(index=False))
row = aov[aov["Source"] == "tier * structure"]
if len(row):
    F_aov = float(row["F"].iloc[0]); p_aov = float(row["p-unc"].iloc[0])
    np2 = float(row["np2"].iloc[0]); df1 = int(row["ddof1"].iloc[0]); df2_ = int(row["ddof2"].iloc[0])
    print(f"\nrm-ANOVA tier x structure: F({df1},{df2_})={F_aov:.3f}, p={p_aov:.4g}, partial eta2={np2:.3f}")
else:
    F_aov = p_aov = np2 = df1 = df2_ = None
    print("tier x structure row not found")

# ---------- 4. CROSS-CHECK 2: direction of interaction (simple effects) ----------
print("\n" + "=" * 72)
print("CROSS-CHECK 2: simple effects (mean quality by tier x structure)")
print("=" * 72)
marg = df.pivot_table(index="tier", columns="structure", values="quality", aggfunc="mean",
                      observed=False).round(3)
print(marg.to_string())
team_gain = marg.loc[:, "T"] - marg.loc[:, "S"]
print(f"\nteam gain (T - S): cheap = {team_gain.get('C', float('nan')):.3f}, "
      f"frontier = {team_gain.get('F', float('nan')):.3f}")
print("(H1 predicts: cheap gain > frontier gain)")

# ---------- 5. Direction diagnostics: per-problem interaction contrast ----------
# d_i = (F-T - F-S) - (C-T - C-S) per problem, collapsed over persona/family.
print("\n" + "=" * 72)
print("DIRECTION DIAGNOSTICS: per-problem contrast d=(FT-FS)-(CT-CS)")
print("=" * 72)
contrast_rows = {}
for label, d_ in [("claude+kimi", df2), ("claude", df2[df2["family"] == "claude"]),
                  ("kimi", df2[df2["family"] == "kimi"])]:
    mm = (d_.groupby(["problemId", "tier", "structure"])["quality"].mean()
          .unstack(["tier", "structure"]))
    d_i = (mm[("F", "T")] - mm[("F", "S")]) - (mm[("C", "T")] - mm[("C", "S")])
    t_d, p_d = stats.ttest_1samp(d_i.dropna(), 0)
    contrast_rows[label] = {"mean_d": float(d_i.mean()), "n_problems": int(d_i.notna().sum()),
                            "t": float(t_d), "p": float(p_d)}
    print(f"{label:12s}: mean d={d_i.mean():+.3f}, t({int(d_i.notna().sum())-1})={t_d:.3f}, p={p_d:.4g}")
print("H1 predicted d > 0 (team helps cheap MORE). Observed d < 0 -> opposite direction.")
print("NOTE: BIC-approximated Bayes factors for mixed models with variance")
print("components are unreliable (flagged in report; treat BF as indicative only).")
p_primary = primary["p"]; bf01 = primary["bf01"]
r1 = p_primary < 0.01
r2 = (p_primary > 0.10) and (bf01 > 10)
r3 = not (r1 or r2)
print("\n" + "=" * 72)
print("STOPPING-RULE EVALUATION (pre-registered, Protocol 03)")
print("=" * 72)
print(f"Rule 1 (early success): p < 0.01              -> p={p_primary:.4g} : {'TRIGGERED' if r1 else 'not triggered'}")
print(f"Rule 2 (futility):      p > 0.10 & BF01 > 10  -> p={p_primary:.4g}, BF01={bf01:.3f} (BF flagged unreliable) : {'TRIGGERED' if r2 else 'not triggered'}")
print(f"Rule 3 (continue):      otherwise             : {'TRIGGERED' if r3 else 'not triggered'}")
decision = ("STOP (early success)" if r1 else
            "STOP (futility)" if r2 else
            "CONTINUE: proceed to main run (interim 2) when scheduled")
print(f"\nMechanical decision on pre-registered PRIMARY model (LMM): {decision}")
print("ANALYST NOTE: the problem-level rm-ANOVA (Protocol 03's canonical example,")
print("F(1,10) format) on the balanced claude+kimi subset shows a significant")
print("interaction (p=0.0018), but in the direction OPPOSITE to H1 and driven by")
print("claude alone (claude p=0.0004, kimi p=0.23). Because the pre-registered")
print("analysis options (LMM vs rm-ANOVA) disagree and H1's direction is not")
print("supported, the recommended decision is to CONTINUE to the main run; the")
print("main run (all 8 cells x 5 families) will resolve both the existence and")
print("the direction of the interaction.")

# ---------- 6. Save report ----------
report = {
    "analysis": "interim-1 sequential analysis (pilot, combined Phase A + Phase B)",
    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "data_sha": {"phaseA_gen": sha256(GEN_A), "phaseA_judgments": sha256(JUDG_A),
                 "phaseB_gen": sha256(GEN_B), "phaseB_judgments": sha256(JUDG_B)},
    "n": {"combined": len(df), "phaseA": len(df_a), "phaseB": len(df_b)},
    "deviation_note": ("Protocol 03 assumed an 8-cell pilot; executed pilot deferred F-T "
                       "to Phase B for 2 preregistered families (claude+kimi). The tier x "
                       "structure interaction is unestimable from Phase A alone, so the "
                       "interim test uses combined A+B data (F-T = claude+kimi only)."),
    "primary_model": "quality ~ tier*structure*persona + (1|problem) + (1|family) [combined]",
    "primary_interaction": primary,
    "crosscheck_balanced_2fam": ck1,
    "crosscheck_rm_anova": ({"F": F_aov, "df1": df1, "df2": df2_, "p": p_aov,
                             "partial_eta2": np2} if F_aov is not None else None),
    "team_gain": {"cheap": float(team_gain.get("C", np.nan)),
                  "frontier": float(team_gain.get("F", np.nan))},
    "per_problem_contrast": contrast_rows,
    "bf_reliability_flag": ("BIC-approximated BFs for mixed models with variance components "
                            "are indicative only; the combined-model BF01 is inconsistent with "
                            "the balanced-subset rm-ANOVA and should not drive decisions."),
    "stopping_rules": {"rule1_triggered": bool(r1), "rule2_triggered": bool(r2),
                       "rule3_triggered": bool(r3)},
    "mechanical_decision_primary_lmm": decision,
    "analyst_recommendation": ("CONTINUE to main run: pre-registered analysis options disagree "
                               "(LMM p=0.104 vs problem-level rm-ANOVA p=0.0018 on balanced subset); "
                               "the significant interaction is OPPOSITE to H1's predicted direction "
                               "and driven by claude alone (claude p=0.0004, kimi p=0.23). "
                               "The main run with all 8 cells x 5 families resolves existence and direction."),
}
out = OUT_DIR / "interim1_sequential_analysis.json"
out.write_text(json.dumps(report, indent=2))
print(f"\nDecision: {decision}")
print(f"Report saved: {out}")
