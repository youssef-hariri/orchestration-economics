# v13 Audit Report — 2026-09-05
**Scope:** full verification of paper v13 (`paper/FULL-PAPER-DRAFT-BUSINESS-v13_with_figures/`) against frozen data artifacts. Pre-v13 content was verified in the v11 audit (MANIFEST Entry, line 968); this pass re-verified all Study 3 / Protocol 16 numbers and diffed v12→v13 for unintended changes.

## Verified accurate (all match frozen artifacts)

**Study 3 (Protocol 13)** — sources: `study3_contrast_a.csv`, `study3_contrast_b.csv`, `study3_economics.csv`, `study3_vs_fsn_full.csv`, `study3_results.json`, `study3_vs_fsn_by_domain.csv`
- Contrast A table (tab:study3-authorship): all 5 families' Δ, t, d, p_raw, p_holm exact ✓
- Contrast B ranges: D-SELF d = 0.15–0.67, D-FRONT d = 0.24–1.33 ✓
- Economics table (tab:study3-econ): all costs, cost ratios, ΔQ values ✓
- Pooled authorship gap 4.03 vs 3.99 ✓; pooled vs FSN d = −0.22 / −0.05 ✓
- Structure: 98.9%/100% gated loops; 5.3–5.4 designed / 5.8–6.2 executed steps; 34.8M vs 24.3M tokens ✓
- Kimi p_holm 0.006/0.013 ✓; Gemini n.s. after Holm ✓; participant flow 544/570 + 26 attrition (21 kimi design_failed, 4 failed, 1 claude design_failed) ✓; 4,896 judgments ✓
- Domain claims (D-FRONT ≥ FSN in strategy/marketing/HR/product; loses finance/operations) ✓ (product d = −0.031 ≈ "meets", within noise of parity)

**Protocol 16 (study3conf)** — sources: `study3conf_gates.csv`, `study3conf_results.json`, judgment ledger
- Gate table R1–R5: all d, 90% CIs, verdicts exact ✓ (R1 +1.25 PASS; R2 −0.23 fail; R3 −0.83 fail; R4 −0.88 fail; R5 −1.90 PASS)
- Counts: 441/450, per-family completion (90/89/89/88/85), 9 attrition ✓; 3,963/3,969 judgments, 6 INCOMPLETE (0.15%) ✓
- Predictions (+0.85/+0.55/+0.46/±0.30/−3.15) match Study 3 D-SELF point estimates ✓
- Probe cost range $0.01–$0.73 matches econ table D-SELF column ✓

**v12→v13 integrity:** diff confirms only intended additions plus two sanctioned edits to existing text (DeeWaanAI naming in Study 3 intro; decision-rule caveat pointer). All v11-audited numbers untouched ✓

## Discrepancies found and FIXED

1. **"Kimi's 22% designer-stage attrition" (decision-rule paragraph) — mislabeled.** The 22% figure (MANIFEST Entry 73) is *total* kimi-lane attrition (25/114 = 21.9%). The designer-stage rate is 21/57 D-SELF design attempts = **36.8%**. v13 now reads "21 of 57 Kimi self-design attempts — 37% — failed at the design stage." (Note: MANIFEST Entry 73's "22% attrition" line is historically accurate as total attrition; only the paper's "designer-stage" label was wrong.)

2. **Abstract overclaim (minor).** "beat the frontier-solo baseline for Gemini, Qwen, and Kimi" lacked the multiplicity caveat (only Kimi survives Holm; Gemini p_holm = 0.387/0.192, Qwen 0.126/0.049). Added: "significant after multiplicity control only for Kimi."

3. **Abstract omission.** Protocol 16 (the paper's newest confirmatory result) was absent from the abstract. Added 2-sentence summary (extremes transport: Kimi +1.25 / Claude −1.90; mid-tier does not; → benchmarking-as-routing).

## Recompile
38 pages, 0 undefined references, no new overfull warnings. Committed with this report.
