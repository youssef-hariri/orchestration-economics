# Study 2 Report — End-of-Pipeline Refinement Stage (Protocol 09)

**Date:** 2026-07-30 · **Phase:** pilot (60 pairs) + extension to full pool
(171 pairs, Protocol 09 §8) · **Status:** COMPLETE — pool exhausted; gate G2 NOT
passed twice (pilot, pooled); superiority claim rejected; mechanism claim confirmed.

## 1. What was done

- 20 random C-T-P answers per family (kimi, claude, qwen), each paired with the
  same-problem same-family F-S-N frontier answer (locked Study-1 data).
- One frozen universal refiner prompt (Protocol 09 §4, add-only rule), deepseek-chat,
  temp 0 → 60/60 completed, 0 failures (**G1 feasibility PASS**, completion 100% ≥ 95%).
- Judged with the frozen D10 panel (3 judges × 3 variants, 540 judgments, 0 failures).
- Refined answers are 1.69× longer than originals (length logged for sensitivity).

## 2. Results

### H2.1 primary — refined vs frontier (FSN), composite, paired
| family | d | diff | 95% CI (boot) | p (Holm) | verdict |
|---|---|---|---|---|---|
| kimi | +0.080 | +0.024 | [−0.105, +0.147] | 1.000 | n.s. |
| claude | −0.903 | −0.130 | [−0.197, −0.070] | 1.000 | worse |
| qwen | −0.642 | −0.140 | [−0.229, −0.047] | 1.000 | worse |

### Baseline check (same sample, pre-refinement)
The random sample was UNFAVORABLE: original C-T-P vs F-S-N was kimi −0.078,
claude −0.154, qwen −0.424 composite (d = −0.26 / −1.07 / −2.19). Study 1's family
advantage is a population average; at n=20 random problems the realized baseline can
run strongly negative.

### Gap change (what refinement actually did)
- kimi: −0.078 → **+0.024** (gap closed and flipped positive)
- claude: −0.154 → −0.130 (gap narrowed by the full +0.024 gain)
- qwen: −0.424 → −0.140 (gap narrowed by the full +0.284 gain)
Refinement recovered exactly its own gain in every family; it did not create a win
because the starting point was behind.

### H2.2 Novelty protection — ALL PASS (margin −0.10)
kimi +0.039, claude +0.042, qwen +0.156 (refined vs original C-T-P). The add-only
rule worked: novelty was preserved or raised.

### H2.3 repair — refined vs original C-T-P
- kimi: Usefulness **+0.233** (FDR 0.002), Elaboration +0.089 (FDR 0.030),
  composite **+0.102 (d=1.53, FDR 0.000)**
- qwen: Usefulness **+0.539** (FDR 0.000), Elaboration **+0.506** (FDR 0.001),
  composite **+0.284 (d=1.48, FDR 0.000)**
- claude: no significant change (composite +0.024, FDR 0.220) — claude C-T-P answers
  were already ~30–35k chars; little room for an add-only pass.

## 3. Gate decision (pre-registered rule applied mechanically)

G2 rule: proceed only if ALL three families show d ≥ 0.2 with CI excluding 0.
Observed: kimi +0.080 (CI includes 0), claude −0.903, qwen −0.642 → **G2 FAIL.
The full run is NOT triggered. The pilot is reported descriptively.** No threshold
was adjusted after seeing data.

## 4. Honest interpretation

1. The mechanism works: a cheap add-only refiner measurably raises Usefulness and
   Elaboration without touching Novelty (kimi, qwen strongly; claude saturated).
2. Superiority over the frontier was not demonstrated in this pilot — mostly because
   the random n=20 baseline ran negative, and partly because the frontier's own
   answers remain strong. The observed refined-vs-frontier d's (−0.6 to +0.08) imply
   a superiority trial would need a much larger n than the 8/d² estimate assumed.
3. Candidate next moves (author decision required, any must be pre-registered):
   (a) extend the pilot to 50–100/family to stabilize the baseline and re-estimate d;
   (b) condition the claim on problems where the team is competitive (interaction
       analysis, not a superiority claim); (c) close the paper with Study 1 + this
       pilot as a mechanism demonstration.

## 5. Artifacts

- Sample: `runs/refine/sample_pilot.json`; refined store: `runs/refine/refined_store_pilot.json`
- Refine log: `runs/logs/refine_pilot.jsonl`; judgments: `runs/logs/refine_judgments_pilot.jsonl`
- Machine results: `results/refine_study2_pilot.json`
- Harness: `code/refine_study2_sample.py`, `code/refine_study2_run.py`,
  `code/refine_study2_analyze.py`; protocol: `DeeWaanAI-Next/protocols/09-PROTOCOL-STUDY2-REFINER.md`

## 6. Extension to full pool (Protocol 09 §8 amendment, author-approved)

The universe of C-T-P runs with an F-S-N mate is exactly **57 per family**; the
extension drew the remaining 37/family (seed 20260731, disjoint from the pilot's
20) and pooled everything: **171 pairs, 171 refinements, 1,539+540 judgments**.
No prompt, panel, or threshold was touched.

### Execution audit
- G1 feasibility: 171/171 refinements (100%), length ratio 1.75.
- Judgments: 988/999 on first pass; re-run recovered all 7 zhipu timeouts.
  4 judgments stayed INCOMPLETE (R3622 ×3, R3873 ×1): two very long refined texts
  (37–38k chars) pushed judge rationales past the frozen max_tokens=2048 cap.
  Affected runs retain 6–8 valid judgments each; disclosed, not patched (frozen
  harness rule).

### H2.1 primary — refined vs FSN, pooled (n = 57/family)
| family | d | diff | 95% CI (boot) | p (Holm) | verdict |
|---|---|---|---|---|---|
| kimi | −0.295 | −0.074 | [−0.137, −0.008] | 1.000 | significantly worse |
| claude | −1.301 | −0.204 | [−0.248, −0.164] | 1.000 | significantly worse |
| qwen | −0.809 | −0.168 | [−0.223, −0.113] | 1.000 | significantly worse |

### Baseline audit at full n (original C-T-P vs F-S-N, same 171 pairs)
kimi −0.184 (d=−0.71), claude −0.222 (d=−1.42), qwen −0.471 (d=−2.17), all CIs
excluding 0. The pilot's "unlucky baseline" hypothesis is corrected: with the full
pool the gap is **real and systematic** in every family — a random C-T-P answer is
reliably below its frontier F-S-N counterpart, consistent with Study 1's
Usefulness penalty.

### Gap recovery (refinement's actual effect)
- kimi: −0.184 → −0.074 (**60% of the gap recovered**)
- claude: −0.222 → −0.204 (8% — saturated, same as pilot)
- qwen: −0.471 → −0.168 (**64% of the gap recovered**)

### H2.2 Novelty protection — ALL PASS (pooled)
kimi +0.043, claude +0.021, qwen +0.177 vs original C-T-P (margin −0.10).

### H2.3 repair (pooled)
kimi Usefulness +0.275 / Elaboration +0.111 (both FDR 0.000); qwen +0.520 /
+0.464 (both FDR 0.000); claude n.s. (saturated).

### Gate decision (mechanical, second and final application)
G2 requires d ≥ 0.2 with CI excluding 0 in all three families. Observed: all three
significantly negative. **G2 FAIL. The pool is exhausted — no further extension is
possible — so the superiority claim is REJECTED for this intervention.**

### Final interpretation (supersedes §4)
1. **Mechanism confirmed, superiority refuted.** A frozen add-only refiner reliably
   raises Usefulness/Elaboration (d ≈ 1.0–1.5 vs original) while protecting Novelty,
   and recovers 60–64% of the C-T-P-vs-frontier gap in kimi/qwen. But it cannot
   produce a win: the starting gap at full n is larger than the refiner's gain.
2. The C-T-P cell's deficit vs F-S-N is not pilot noise — it is a population effect.
   Any "design beats frontier" claim would need a stronger intervention than an
   add-only editor pass, or a different comparison (e.g., best-of-cell selection).
3. Claim discipline for the paper: report Study 2 as a **mechanism demonstration
   with a negative superiority result** (registered, fully pooled, zero threshold
   changes). This is the honest, publishable shape of the abductive cycle.

### Extension artifacts
- Sample: `runs/refine/sample_extension.json`; store: `runs/refine/refined_store_extension.json`
- Refine log: `runs/logs/refine_extension.jsonl`; judgments: `runs/logs/refine_judgments_extension.jsonl`
- Machine results (pooled): `results/refine_study2_pooled.json`
- Sampler: `code/refine_study2_sample_ext.py`

## 7. Cross-family secondary analysis (Protocol 09 §9, author-asked)

Question: can cheap+design+persona beat frontiers of OTHER families, even where it
loses to its own? Locked rule BEFORE computation: full 6-direction matrix, minimal-
runId F-S-N mate per problem, no selection; descriptive only (family quality is
confounded with design). Zero new API calls.

### (A) Original C-T-P vs cross-family F-S-N (n = 57/direction, Holm)
| direction | diff | d | 95% CI |
|---|---|---|---|
| kimi→claude | −0.288 | −1.46 | [−0.343, −0.235] |
| kimi→qwen | −0.091 | −0.50 | [−0.137, −0.042] |
| claude→kimi | −0.118 | −0.65 | [−0.162, −0.069] |
| claude→qwen | −0.026 | −0.16 | [−0.064, +0.015] |
| qwen→kimi | −0.563 | −2.19 | [−0.627, −0.495] |
| qwen→claude | −0.667 | −2.84 | [−0.730, −0.607] |

No direction is positive. The original C-T-P answer loses to EVERY frontier,
including other families' weaker ones.

### (B) Refined C-T-P vs cross-family F-S-N (n = 57/direction)
| direction | diff | d | 95% CI |
|---|---|---|---|
| kimi→claude | −0.178 | −0.92 | [−0.231, −0.130] |
| kimi→qwen | **+0.019** | +0.10 | [−0.028, +0.066] |
| claude→kimi | −0.100 | −0.51 | [−0.148, −0.047] |
| claude→qwen | −0.007 | −0.05 | [−0.048, +0.029] |
| qwen→kimi | −0.260 | −1.09 | [−0.321, −0.198] |
| qwen→claude | −0.364 | −1.85 | [−0.412, −0.313] |

### Interpretation
1. The author's hypothesis was testable at zero cost and is REJECTED in its strong
   form: no family's pipeline beats another family's frontier.
2. Refinement does produce two effective TIES with the weakest frontier (qwen F-S-N):
   refined kimi→qwen +0.019 and refined claude→qwen −0.007, both CIs including 0.
   Refinement lifts each family to parity with the weakest frontier but no further.
3. The frontier strength ordering implied by the matrix: claude > kimi > qwen; the
   cross-family gaps are dominated by that ordering (the confound in action).
4. Paper sentence candidate: "Under the most favorable cross-family comparison, the
   refined orchestrated answer reaches statistical parity with the weakest frontier
   model but never exceeds any frontier."
- Artifacts: `results/cross_family.json`, `code/cross_family.py`.
