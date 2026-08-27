# Interim-1 Decision Record — Orchestration Economics Pilot

**Date:** 2026-08-04 (UTC) · **Analyst:** Qoder agent (supervised) · **Script:** `code/sequential_analysis.py`
**Machine report:** `results/interim1_sequential_analysis.json`

## Data basis

- Phase A: 329 runs (6 cells × 5 families × 11 problems) + 2,961 judgments
- Phase B: 42 runs (F-T-N/F-T-P × claude+kimi × 11 problems) + 378 judgments
- Combined N = 371 runs; DV = mean over 3 judges × 3 variants × 5 dimensions
- Data SHA fingerprints archived in the JSON report (full traceability)

## Deviation from Protocol 03 (disclosed)

Protocol 03 assumed the pilot covers all 8 cells × 5 families (440 runs). The executed
pilot deferred F-T cells to Phase B for the 2 families selected by the preregistered
F-S-N novelty rule (claude + kimi), because F-T pipelines could not exist before family
selection. Consequence: the tier × structure interaction is **unestimable from Phase A
alone**; the interim test uses combined A+B data with F-T present for claude+kimi only.

## Results (tier × structure interaction, H1)

| Analysis | Statistic | p | Effect |
|---|---|---|---|
| Primary LMM, combined N=371 | b = −0.117 (SE 0.072), t(363) = −1.63 | 0.104 | β_std = −0.37 |
| LMM, balanced claude+kimi subset (n=88) | b = −0.076 (SE 0.078), t = −0.98 | 0.330 | — |
| Problem-level rm-ANOVA, balanced subset | F(1,10) = 17.70 | **0.0018** | partial η² = 0.64 |
| Per-problem contrast, claude only | mean d = −0.243, t(10) = −5.20 | 0.0004 | — |
| Per-problem contrast, kimi only | mean d = −0.097, t(10) = −1.28 | 0.231 | — |

Direction: d = (F-T − F-S) − (C-T − C-S) = **−0.167** → the team structure helps
**frontier** models more than cheap models — the **opposite** of H1's prediction.

Bayes factors: BIC approximation gave BF₀₁ = 767 (combined LMM) but BF₁₀ = 11.6
(balanced subset LMM) — mutually inconsistent; flagged unreliable for decision-making.

## Stopping-rule evaluation (pre-registered)

- Rule 1 (p < 0.01): **not triggered** on the primary LMM (p = 0.104)
- Rule 2 (p > 0.10 & BF₀₁ > 10): mechanically triggered, **but the BF is flagged unreliable**
- Rule 3 (continue): the pre-registered analysis options disagree materially

## Decision: CONTINUE to the main run (interim 2)

**Justification:**
1. The two pre-registered analysis options (LMM vs problem-level rm-ANOVA) give
   contradictory answers (p = 0.104 vs p = 0.0018). Stopping in either direction would
   rest on a single contested specification.
2. Where the interaction is significant, it runs **opposite to H1** and is driven by a
   single family (claude, p = 0.0004; kimi n.s.). A futility stop would bury a real,
   theoretically interesting effect; a success stop would claim H1 when the direction
   contradicts it.
3. The main run (19 problems × 8 cells × 5 families) restores full balance (F-T for all
   5 families), which is required to estimate the interaction without family confounding.

**Scientific note for the paper:** the pilot suggests the orchestration-economics thesis
("structure substitutes for tier") may be **reversed at the frontier**: frontier team
output slightly exceeds frontier solo, while cheap teams gain little. This deserves the
full balanced sample before any claim.

## What is NOT changed by this decision

- No new experiment runs are launched now (discount-time window pending, per experimenter).
- Pre-registration, protocols, and pilot data are frozen as-is.
- Main run resumes on the pre-registered plan when scheduled (19 remaining problems,
  all 8 cells × 5 families, 2–3 reps, c = 100).
