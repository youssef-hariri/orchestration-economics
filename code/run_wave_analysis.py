#!/usr/bin/env python3
"""DISCLOSED runtime wrapper around the FROZEN code/analyze_wave.py (Protocol 12).

Protocol 12 §5.6 freezes analyze_wave.py byte-for-byte after judging; this
wrapper does NOT modify it. It substitutes a numerically robust LMM at
runtime and injects a complete fallback disclosure into the output JSON.
Justification is recorded as decision D52 (DESIGN-DECISIONS.md) and
MANIFEST entry 64.

Robustness rule (declared here BEFORE viewing gate outcomes, applied
uniformly to every LMM call):
  1. Fit the pre-registered spec: groups=family,
     vc_formula={problem, fam_prob}  (analyze_wave.lmm).
  2. On numpy.linalg.LinAlgError (singular RE cross-product on the observed
     imbalanced panel), fit BOTH single-vc specs (problem-only and
     fam_prob-only). HARD REQUIREMENT: both converge and their fixed-effect
     parameters agree within rtol=1e-6 (atol=1e-9). Otherwise this wrapper
     aborts — no further ad-hoc rescue is permitted.
  3. Sticky: once any fit falls back, every subsequent LMM in the same run
     uses the cross-validated single-vc (problem) structure, so that the
     W3a LRT compares models with identical random-effects structure.
  4. The returned model is the problem-only fit; the fam_prob-only fit is
     retained purely as a cross-check.

Diagnosis motivating this wrapper (pre-wave-data evidence, see D52): on the
completed wave dataset the dual-vc fit raises LinAlgError at W1, while each
single-vc fit converges and yields bit-identical fixed effects — the
pre-registered RE structure is numerically non-identifiable on the
imbalanced panel (kimi 58/52/24 of 90/90/60; gemini deferred), not a
researcher-degrees-of-freedom issue.

Usage: python3 code/run_wave_analysis.py [--promo]
Writes the same outputs as the frozen script, plus the disclosure block
"lmm_numerical_fallback_disclosure" inside the results JSON.
"""

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, "code")
import analyze_wave as aw  # noqa: E402  (frozen; never edited here)
import statsmodels.formula.api as smf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

DISCLOSURE = {
    "wrapper": "code/run_wave_analysis.py",
    "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "frozen_script": "code/analyze_wave.py",
    "frozen_script_sha256": hashlib.sha256(
        (ROOT / "code/analyze_wave.py").read_bytes()).hexdigest(),
    "reason": (
        "The pre-registered dual variance-component RE structure "
        "(groups=family; vc problem; vc family:problem) is numerically singular "
        "on the observed wave data (imbalanced panel: kimi credit-exhausted, "
        "gemini provider failure deferred). The fallback is a numerical "
        "necessity, not a model re-specification: on this data both single-vc "
        "models converge with identical fixed effects, verified per call below."),
    "rule_sticky": (
        "After the first fallback, all LMMs in this run use the single-vc "
        "(problem) structure so the W3a LRT compares identical RE structures."),
    "lmm_calls": [],
}
_STICKY = {"engaged": False}

VC_PROBLEM = {"problem": "0 + C(problemId)"}
VC_FAM_PROB = {"fam_prob": "0 + C(fam_prob)"}
VC_BOTH = dict(VC_PROBLEM, **VC_FAM_PROB)


def _fit(df, formula, vc):
    return smf.mixedlm(formula, df, groups=df["family"], vc_formula=vc).fit(reml=True)


def _fe(m):
    return {k: float(v) for k, v in m.fe_params.items()}


def robust_lmm(df, formula):
    entry = {"formula": formula, "n_rows": int(len(df)),
             "cells": sorted(map(str, df.cell.unique().tolist()))}
    if not _STICKY["engaged"]:
        try:
            m = _fit(df, formula, VC_BOTH)
            entry["spec"] = "pre-registered dual-vc"
            DISCLOSURE["lmm_calls"].append(entry)
            return m
        except np.linalg.LinAlgError as e:
            entry["pre_registered_spec_error"] = f"{type(e).__name__}: {e}"
            _STICKY["engaged"] = True
    else:
        entry["sticky_from_prior_fallback"] = True

    mp = _fit(df, formula, VC_PROBLEM)
    mf = _fit(df, formula, VC_FAM_PROB)
    if not (bool(mp.converged) and bool(mf.converged)):
        raise RuntimeError(
            f"single-vc fallback did not converge: problem={mp.converged}, "
            f"fam_prob={mf.converged} (formula: {formula})")
    fe_p, fe_f = _fe(mp), _fe(mf)
    if set(fe_p) != set(fe_f):
        raise RuntimeError("fixed-effect parameter sets differ between single-vc fits")
    for k in fe_p:
        if not np.isclose(fe_p[k], fe_f[k], rtol=1e-6, atol=1e-9):
            raise RuntimeError(
                f"single-vc fixed effects disagree for {k}: {fe_p[k]!r} vs {fe_f[k]!r}")
    entry["spec"] = ("fallback single-vc (problem); fam_prob-only fit cross-checked, "
                     "fixed effects identical within rtol=1e-6/atol=1e-9")
    entry["cross_check_fixed_effects"] = {k: round(v, 10) for k, v in fe_p.items()}
    DISCLOSURE["lmm_calls"].append(entry)
    return mp


def main():
    aw.lmm = robust_lmm  # runtime substitution only; frozen file untouched
    aw.main()

    promo = "--promo" in sys.argv
    out_path = ROOT / ("results/wave_analysis"
                       + ("_minimax_promo" if promo else "") + ".json")
    out = json.loads(out_path.read_text())
    n_fb = sum(1 for c in DISCLOSURE["lmm_calls"]
               if not c["spec"].startswith("pre-registered"))
    DISCLOSURE["n_lmm_calls"] = len(DISCLOSURE["lmm_calls"])
    DISCLOSURE["n_fallback_calls"] = n_fb
    DISCLOSURE["ran_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out["lmm_numerical_fallback_disclosure"] = DISCLOSURE
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"disclosure injected: {out_path} "
          f"({n_fb}/{len(DISCLOSURE['lmm_calls'])} LMM calls fell back)")


if __name__ == "__main__":
    main()
