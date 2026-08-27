# INTERIM-2 DECISION — Orchestration Economics Main Run

**Date:** 2026-08-06 (UTC)
**Dataset:** main run (1,900 runs), judging campaign v2/A1 (3 judges × 3 verbatim variants)
**Protocol basis:** 01-PREREGISTRATION (H1–H5), 03-SEQUENTIAL-ANALYSIS (Rule 4 final analysis),
06-AMENDMENT-A2 (A2.1–A2.7 robustness suite), OSF registration [mjb8x](https://osf.io/mjb8x).

---

## 1. Data lock

Analysis inputs are frozen as of this document. No further writes are permitted to these files.

| File | SHA-256 |
|---|---|
| `runs/fulltext/main_fulltext.json` | `afeacbab26520381c883a2c3d245795ff49357c09dee745e0f1ae26a059a566e` |
| `runs/logs/main_judgments.jsonl` | `23c289a5797e53e43fb68e5c17ecd2994c3b718f9baf244dd031ba42ad51c4d1` |

**Integrity:** 1,900/1,900 runs completed with non-empty full text (5 model families × 380).
17,091/17,100 judgment cells (99.95%) have complete 5-dimension scores.
9 cells excluded as audited incompletes (null scores persisting across ≥4 retries; systematic,
all on old-batch runs): (3622, meta/var3), (3622, deepseek/var2), (3659, meta/var2),
(3663, meta/var2), (3667, deepseek/var2), (3714, deepseek/var2), (3751, deepseek/var2),
(3753, meta/var2), (3846, deepseek/var2), (4267, meta/var2). Affected runs retain ≥7 of 9
judgments each; composite DV computed over available judgments.

## 2. Primary result — H1 (tier × structure interaction)

Pre-registered direction (protocol 01 §2): the team structure improves quality **more** for
cheap_sibling models than for frontier models, i.e. contrast d = (FT−FS)−(CT−CS) < 0.

| Statistic | Value |
|---|---|
| Contrast d | **−0.227** |
| Welch t (df ≈ 1594.5) | −2.447 |
| p | 0.0145 |
| Bootstrap 95% CI (5,000 resamples, seed 42) | [−0.410, −0.040] |
| JZS BF₁₀ (r = 0.707) | 1.002 (inconclusive) |
| OBF interim-2 boundary (A2) | \|z\| ≥ 1.977 |

**Decision:** |z| = 2.447 > 1.977 and the bootstrap CI excludes zero in the pre-registered
direction. **The interim-2 boundary is crossed: H1 is supported.**

Caveat, reported per A2.4: the Bayesian evidence for the interaction is inconclusive
(BF₁₀ ≈ 1). The pre-registered decision basis is the frequentist sequential boundary
(protocol 03 §3); the BF is reported as recommended but does not gate the decision.

## 3. Secondary effects

| Effect | d | 95% CI (bootstrap) | BF₁₀ | Pre-registered expectation |
|---|---|---|---|---|
| H2 tier (F−C) | +0.294 | [0.201, 0.382] | 1.7 × 10⁷ | F > C — **supported** |
| H3 structure (T−S) | +0.117 | [0.030, 0.205] | 1.34 | T > S — **supported** |
| H4 persona (P−N) | −0.691 | [−0.761, −0.620] | 1.0 × 10⁵⁰ | P > N — **reversed**; N scores higher |
| H5 structure × persona | F = 1.23, p = 0.268 | — | — | **not supported** |

H4 reversal (large, direction opposite to pre-registration) and the tier × structure × persona
three-way interaction (F = 6.68, p = 0.0098, partial η² = 0.0035) are flagged for the final
report discussion; they do not alter the H1 decision.

## 4. Amendment A2 robustness summary

- **A2.2 BH-FDR (secondary family):** persona effects on Novelty/Usefulness/Flexibility/
  Elaboration survive FDR; Cultural Sensitivity does not (p_FDR = 0.087); kimi-family
  interaction survives (p_FDR = 0.0058), claude-family interaction does not.
- **A2.3 Type-II ANOVA:** tier × structure interaction F = 6.90, p = 0.0087, partial η² = 0.0036.
  Residuals non-normal (Shapiro p ≈ 0) and variances unequal (Levene p ≈ 0); the bootstrap CI
  and Welch df in §2 are the robustness safeguard, as specified in A2.3.
- **A2.5 leave-one-family-out:** d ranges −0.143 (drop kimi) to −0.303 (drop gemini);
  sign stable in all 5 folds; max |Δd| = 0.084. **No family drives the effect.**
- **A2.6 leave-one-problem-out:** d stable across all 19 folds (range −0.212 to −0.247);
  all folds remain negative. **No problem drives the effect.**
- **A2.7 sensitivity power:** min cell n = 190 (frontier cells); minimum detectable d at
  80% power = 0.288. The observed |d| = 0.227 for H1 is below this per-cell threshold —
  the interaction is detected via the within-subjects contrast across all 1,900 runs, not
  per-cell power. Reported per A2.7.
- **A1.4 length confound:** length-adjusted contrast coefficient p = 0.63; no confound.
- **Inter-judge reliability:** deepseek–zhipu r = 0.871, deepseek–meta r = 0.613,
  meta–zhipu r = 0.494.

## 5. Decision and next steps (protocol 03 Rule 4)

Interim 2 is the final scheduled look. Per Rule 4: **no further data collection.**
The interaction is significant in the pre-registered direction; report the effect size,
CI, and p-value in the final paper analysis. A2 §4 integrity clause honored: nothing in the
A2 outputs altered the sequential stopping logic; the boundary crossing alone governs.

Remaining work: qualitative analysis (protocol 02), cost-effectiveness analysis
(protocol 04), and the final paper write-up.

## 6. Amendment A3 — exploratory advanced statistics (EXPLORATORY, post-lock)

Approved 2026-08-06; protocol 07-AMENDMENT-A3. Read-only on the locked dataset; none of
these outputs alter the §2 decision. Full machine output: `results/exploratory_analysis.json`.

- **A3.1 LMM** (run-level, grouping problem|family): the run-level tier × structure
  two-way interaction coefficient is ≈ 0 (coef = −0.001, p = 0.97), while the three-way
  tier × structure × persona term is significant (coef = −0.151, p = 0.00035). The
  pre-registered interaction at the cell/problem level is therefore concentrated in
  persona-loaded conditions — consistent with the §2 subset pattern.
- **A3.2 TOST** (no-persona contrast, SESOI d = ±0.20): d = −0.008, SE = 0.126,
  p_TOST = 0.063 → equivalence **not** established. Honest phrasing: the interaction is
  small and non-significant without personas, but absence is not yet proven.
- **A3.3 Empirical-Bayes partial pooling**: shrunk per-family d: kimi −0.365, claude
  −0.305, qwen −0.255, gemini −0.230, gpt −0.198 (pooled −0.270). Under pooling, all
  families shift toward a negative effect; gpt's raw null estimate is largely noise.
- **A3.4 Random-effects meta-analysis** (5 families as studies): pooled d = −0.270
  [−0.472, −0.069], z = −2.64, p = 0.008; τ² = 0.015, I² = 28.5% (low-moderate
  heterogeneity). The interaction generalizes across model families as a whole.
- **A3.5 Persona dimension decomposition** (P−N, BH-FDR): Novelty **+0.154** (personas
  help novelty, p_FDR = 0.001); Usefulness **−1.024** and Elaboration **−0.966** drive the
  reversed persona main effect; Flexibility −0.299; Cultural Sensitivity −0.087 (n.s.).
  Interpretation for discussion: persona loading trades judged usefulness/elaboration for
  a small novelty gain.

Status of §5 unchanged: Rule 4 governs; A3 is exploratory and reported as such in the paper.
