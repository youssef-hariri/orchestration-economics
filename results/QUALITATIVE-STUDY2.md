# Study 2 Qualitative Analysis — Why Refinement Stops at Parity (Protocol 10)

**Date:** 2026-07-30 · **Status:** complete · **Protocol:** 10 (pre-registered before execution)
**Scope:** mechanism evidence for the negative superiority result (Entries 29–31).
No superiority claim may be derived from this report (Protocol 10 §7).

## 1. P0 free preliminary: length vs score change (n = 171)

| group | Pearson r | Spearman ρ |
|---|---|---|
| kimi | +0.560 (p<0.001) | +0.546 |
| claude | +0.209 (p=0.12, n.s.) | +0.068 |
| qwen | +0.473 (p<0.001) | +0.431 |
| pooled | +0.675 (p<0.001) | +0.707 |

Locked interpretation rule (|r| ≥ 0.3, p < 0.05): length inflation is a **prime
driver** of refinement gains for kimi and qwen (not a diluter — the opposite of
the dilution hypothesis). Claude's n.s. correlation is consistent with its
saturation: refinement barely changed claude answers, so neither length nor
score moved.

## 2. Reliability (Wave 2 closed coding, 90 texts × 2 blinded coders)

- Completion 180/180 (100%). **Pooled Cohen's κ = 0.824** (93.1% agreement) — gate passed.
- 7 of 13 codes κ-reliable (≥ 0.70): concise_maxims (0.84), operational_parameters
  (0.92), cultural_localization (0.89), phased_timeline (0.92), tables_matrices
  (1.00), quantified_targets (0.76), granular_ops_detail (0.74).
- 6 codes below threshold (disclosed, conclusions downgraded to medium
  reliability): diagnostic_reframe (0.54), named_concepts (0.49), assumption_test
  (0.56), structured_report (0.59), external_authority (0.56), redundancy_bloat
  (0.65). Low κ is largely a base-rate artifact (near-zero prevalence), percent
  agreement stays 82–98%.
- Artifacts: `results/qual2_kappa.json`, `results/qual2_codebook.json` (frozen),
  `runs/logs/qual2_closed.jsonl`, `runs/logs/qual2_wave1.jsonl`,
  `runs/qual2/triples.json` (30 triples, seed 20260801).

## 3. Findings by research question

### RQ1 — the frontier's residual edge
Among κ-reliable codes, only ONE code shows a ≥ 0.30 gap anywhere:
**concise_maxims** (qwen: frontier 1.00 vs refined 0.55, gap +0.45; kimi gap +0.20).
Medium-reliability signal: **redundancy_bloat** — frontier texts 0.00 across all
three families vs refined 0.65–0.95. Meanwhile refined answers MATCH OR EXCEED
the frontier on every structural code (operational_parameters, tables_matrices,
quantified_targets, granular_ops_detail: refined 1.00 vs frontier 0.50–0.90 in
kimi/qwen).
**Mechanism:** the frontier's remaining advantage is density — compressed maxims and
zero boilerplate — not content coverage. Refinement overshoots the frontier on
structure while undershooting on concision.

### RQ2 — style convergence or length inflation?
All 6 codes that changed between original and refined answers (kimi and qwen)
are structural RQ2 codes: operational_parameters, structured_report,
phased_timeline, tables_matrices, quantified_targets, granular_ops_detail.
No RQ1 insight code (diagnostic_reframe, assumption_test, concise_maxims) moved
materially. Convergence metric: kimi toward 4 / away 6 (net divergence), qwen
5 / 4, claude 0 / 2 (flat).
**Mechanism:** refinement adds scaffolding (tables, gates, numbers, week-level
plans) — which also explains the length inflation in P0 — but does not inject
the insight-density features that distinguish frontier answers.

### RQ3 — why claude saturated
Claude's original answers already scored at or near the ceiling of every
codebook code (1.00 on 8 of 13; ≥ 0.90 on 11). Changed codes orig→refined: **0**
(vs 6 for kimi and qwen). The refiner had nothing to add: claude C-T-P answers
were already structurally complete, so the generic refiner produced near-
identical text (quantitative echo: claude d barely moved, pooled baseline
already −1.42).

## 4. Integration with the quantitative results

1. Refinement works by adding structure + length (P0 r=+0.68; 6 structural codes
   change) → scores rise (H2.1 gap narrows 60–64% for kimi/qwen).
2. The gap that remains is the density gap: frontier answers are shorter, carry
   compressed maxims, and contain zero boilerplate — features a generic
   add-only refiner structurally cannot produce (it can only append).
3. Claude was already at the structural ceiling, so refinement had no lever —
   and claude's frontier is the strongest of the three, so its gap was never
   closable by scaffolding anyway.
4. Net: parity with the weakest frontier, never superiority — the quantitative
   ceiling (Entry 31) is explained by a qualitative mechanism: **orchestration
   buys coverage, the frontier wins on density**.

Paper sentence candidate: "Qualitative coding shows the refiner adds structural
completeness (timelines, tables, quantified targets) but not concision: frontier
answers contain zero boilerplate and universal compressed maxims, the one
dimension on which refinement never converges."

## 5. Limitations

- n = 30 triples (10/family); prevalence estimates are coarse.
- 6 codes below the κ threshold; any claim resting on them is medium-reliability
  only (redundancy_bloat notably).
- Coders are LLMs (blinded, temp 0), same machinery and precedent as A4.6.
- Truncated refined answers (37–38k chars, Entry 30) may inflate redundancy codes;
  direction of bias disclosed, not corrected.
