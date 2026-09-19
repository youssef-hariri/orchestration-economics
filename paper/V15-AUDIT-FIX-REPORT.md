# v15 Audit-Fix Report — 2026-09-17

Input: `paper/P5_v14.3-audit-2026-09-16/FINAL_AUDIT_REPORT.json` (162 claims; 143 match, 6 rounding, 5 discrepancy, 7 unverified, 1 method warning).
Output: `paper/P5_v15.tex` (from v14.3, 8 change clusters, diff-audited; compiles 44 pp, 0 undefined refs).

## Per-item verification and action

| Item | Audit claim | My verification | Action in v15 |
|---|---|---|---|
| M005 / D_025 | Retry count wrong (110 vs 234) | Both traceable: 234 = team runs with any failed-step entry; **110 = runs whose ledger total is actually understated** (total < sum of completed steps). Failed attempts all have 0 tokens / 0 latency = instant transport rejections, nothing billable. Median true/recorded on affected runs = 1.687 ✓ (paper's 1.69). Aggregate understatement = 4.4% of team tokens, **6.0% cost-weighted (φ=0.5; 5.5–6.1% across all φ)** — paper said "roughly 8%" | §3.3 + §7 mechanism rewritten (failed attempts consume nothing; run-total omits *completed* earlier steps); 8% → 6%. Also fixed a **leftover contradiction the audit missed**: "Disclosed threats (i)" still said intermediates are not in the cost ledger — rewritten as the retry-accounting disclosure. Artifact: `analysis/results/study1_retry_cost_gap.json` |
| S1_012 | CTP-vs-FSN d values untraceable | **Paper correct.** Recomputed from refine samples + audit composites: kimi −0.71, claude −1.42, qwen −2.17 exactly | Persisted `analysis/results/study2_baseline_audit_ctp_vs_fsn.json`; no text change |
| M004 | Price floor 3.4× wrong | Verified: qwen 3.12× (φ=0.5 blend), gemini 8.00× | "3.4×" → "3.1×" |
| M006 | 15+10+5 problem breakdown wrong | Verified: 30 = 15 inherited (`business_problems_15.json`) + 15 domain-extension (`business_problems_domain_15.json`), disjoint; `domain_map.json` = **six** domains × 5. The 10 post-cutoff cases belong to the wave, not Study 1. Paper also said "five domains" here while saying "six domains" elsewhere | §3.4 rewritten: 15 inherited + 15 drafted, six domains × five problems, post-cutoff pointer moved to wave |
| S2_011 | qwen changed codes include an insight code | Verified in `qual2_analysis.json` saturation_rq3: kimi's 6 all structural; qwen's 6 = 5 structural (no `structured_report`) + `diagnostic_reframe` (insight) | §4.2.2 rewritten per-family; "no insight code moved" scoped to the other three insight codes |
| S1_025 | r=−0.978 unverifiable | **Reproduced** from `exploratory_heterogeneity.json` cell means: gap = F−C, team effect = C-T-N − F-S-N → r=−0.979, ρ=−1.000 (paper's −0.978 within rounding of the original per-run computation). **But found real errors the audit missed**: claude's gap sign wrong in paper (−0.357 → +0.364; the two families were quoted under opposite sign conventions) and the "farthest/small" descriptors were swapped (kimi's cheap model scores *above* its frontier; claude's is farthest *below*). Also: team effect = lift − gap by construction → correlation partly mechanical | §4.1.x sentence rewritten (signs, descriptors, definitions, mechanical-coupling caveat). Artifact: `analysis/results/study1_capability_gap.json` (incl. lift-vs-gap r=+0.82 partial-compensation variant) |
| S2_007 | r=+0.68 no source | Root-caused: original used **word-count ratio**, not char ratio (char gives r=+0.35). Word ratio reproduces n=171, r=+0.670, ρ=+0.705 — i.e. paper's +0.68/+0.71 was 0.01 high | §4.2.1: r=+0.67, ρ=+0.70, "word-count ratio". Artifact: `analysis/results/study2_length_correlation.json` |
| S3_032 | P16 attrition no source | Verified exactly: 441/450 (gemini 90, claude 89, qwen 89, gpt 88, kimi 85; dedupe by run key) | Persisted `analysis/results/study3conf_attrition.json`; no text change |
| S3_033 | Judgment counts no source | Verified exactly: 3963/3969 valid; zhipu 1323, meta 1320, deepseek 1320; 6 persistent missing, all on 3 claude runs (deepseek/meta variants, 8–15 attempts each) | Persisted `analysis/results/study3conf_judgments_summary.json`; no text change |
| D_029 | 98.9–100% loop gates | Verified in `study3_results.json` pct_with_gates | None |
| M001 | 40–88% prior-work claim | External to our data (Hariri2026b) | None — confirm against the cited paper before submission |

## Statistics changed in v15 (flagged per protocol)

1. S2_007: r = +0.68 → **+0.67**, ρ = +0.71 → **+0.70** (now backed by a persisted artifact; p<0.001 and interpretation unchanged).
2. M005: "roughly 8%" → **roughly 6%** (cost-weighted recompute; the disclosed bias shrinks, no conclusion affected).
3. S1_025: claude gap **−0.357 → +0.364** + prose direction reversed + mechanical-coupling caveat added. Headline r=−0.978 kept (reproduced as −0.979 from rounded means).

## Lessons (audit-the-auditor)

- 2 of 7 actionable items were auditor artifacts: M005 compared different denominators (234 vs 110 — both real, different definitions); S1_012 was "untraceable" only because the values lived in a computed block, not a raw file.
- The audit missed 3 real errors: claude gap sign + swapped descriptors (S1_025 sentence), the stale "intermediates not in cost ledger" threat paragraph, and the metric ambiguity behind S2_007 (word vs char ratio).
- Persistence policy works: every number above now has a machine-readable artifact under `analysis/results/` with method + source files, so future stats materialize from files, not prose memory.
- When a headline correlation involves derived quantities that share a component (team effect and gap both contain the frontier mean), state the mechanical coupling explicitly — reviewers will.

## Not done (deferred)

- Figures: unchanged, per decision to handle figures after text is final.
- v15 not committed to git (per rule: paper drafts committed only when all changes are finished).
