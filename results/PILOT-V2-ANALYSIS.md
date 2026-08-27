# Pilot v2 Re-Judge Analysis (Amendment A1.5 executed)

**Date:** 2026-08-04 (judging executed inside the author-approved discount window)
**Input:** 371 frozen pilot solutions, judged from the **full-text store** (`runs/fulltext/pilot_fulltext.json`)
**Instrument:** `code/judge_v2.py` (harness `judge_v2/A1`): same 3 judges × 3 verbatim D10 variants, temp 0, seed-blinded order; `max_tokens` 512 → 2048; completeness gate with ≤2 retries (A1.2); audit fields on every record (A1.3).
**Output:** `runs/logs/pilot_v2_judgments.jsonl` (append-only, deduped last-wins in analysis)
**Machine-readable results:** `results/pilot_v2_analysis.json`
**Analysis code:** `code/analyze_pilot_v2.py`
**Status:** exploratory/descriptive only — pilot data never enter confirmatory inference (D31/D32). **Main run NOT started; awaiting author confirmation.**

---

## 1. Judgment integrity (A1.2 gate worked)

| | v1 (frozen, capped text) | v2 (full text, A1) |
|---|---|---|
| Judgment records | 3,339 | 3,339 unique cells (371 × 3 judges × 3 variants) |
| Complete judgments | 3,339 with **442 null dimension scores (2.65%)** | **3,337 complete, 0 null scores** |
| Audited failures | 0 (nulls silently emitted) | 2 `incomplete` (run 997, Llama var2/var3) |
| Transport errors | — | 5 transient zhipu timeouts, all recovered on resume |

The 2 persistent incompletes are **format non-compliance** (the Llama judge answered run 997 in discursive prose instead of the rubric format; reproduced across 6 attempts at temp 0). They are logged `incomplete: true` and excluded — never silently dropped, per A1.2. Run 997 keeps 7/9 judgments.

Provider alias note: registry `deepseek-chat` resolves to `deepseek-v4-flash` at the provider in **both v1 and v2** — the instrument is identical across versions.

**Cost:** $12.59 total (zhipu $7.46, meta $4.44, deepseek $0.70). Judging only; zero generation spend.

## 2. v1 vs v2 agreement

- Run-level composite correlation: **Pearson r = 0.921, Spearman ρ = 0.911** (n = 371).
- Mean shift v2 − v1 = **+0.029** overall; **+0.049 on previously capped runs, +0.017 on non-capped** — seeing the full text raises scores slightly, exactly where the cap had bitten. The v2 table is a corrected refinement of v1, not a different measurement.

## 3. The tier × structure interaction (the interim-1 anomaly)

Convention: d = (F-T − F-S) − (C-T − C-S) on run-level composite means (1–5 scale); negative = team structure helps frontier models *less* (opposite to naive additive expectation; H1's "structure substitutes for tier" predicts cheap teams gain most, i.e. also negative via CT−CS; see INTERIM1-DECISION.md for the pre-registered framing).

**⚠ Estimability:** in the pilot, F-T cells exist **only for claude + kimi** (Phase B). Any all-five-families contrast confounds family composition with the interaction and is reported for completeness only; the balanced claude+kimi subset is the honest estimate.

### 3.1 All five families (confounded — reference only)

| Analysis | n | contrast | p |
|---|---|---|---|
| v2 pooled | 371 | +0.122 | 0.035 |
| v1 pooled | 371 | +0.088 | 0.134 |

The sign flip vs §3.2 is precisely the family confound the main run eliminates.

### 3.2 Balanced claude + kimi subset (the estimable interaction)

| Subset | v1 contrast (p) | v2 contrast (p) |
|---|---|---|
| All (n=173) | −0.162 (0.016) | **−0.117 (0.031)** |
| Non-capped (n=106) | −0.016 (0.924) | −0.099 (0.205) |
| Capped (n=67) | −0.281 (0.002) | −0.244 (0.016) |
| Capped & **full text recovered** (n=48) | — | **+0.059 (0.430)** |
| Capped & genuine model ceiling (n≈19) | — | not estimable (cells n=2–3) |
| Per-problem means, all | −0.167 (0.0018) | −0.124 (0.010) |
| Per-problem means, non-capped | −0.002 (0.991) | −0.120 (0.047, k=9) |
| OLS tier×structure (ck) | — | b=−0.117 (0.030) → length-adjusted b=−0.108 (0.041) |

**Reading:**
1. The A1 correction **attenuates** the anomaly (−0.162 → −0.117; per-problem −0.167 → −0.124) but does **not erase it**.
2. Where the judge actually saw recovered full text (the 48 capped-but-recovered ck runs), the reversal **disappears** (+0.059, n.s.) — confirming the F1 artifact attribution for those runs.
3. The residual pooled signal concentrates in (a) the genuine model-ceiling runs whose stimulus is still inherently capped (unsolvable without regeneration; tiny cells), and (b) a weak, statistically fragile negative signal in the non-capped subset (pooled p=0.205; per-problem p=0.047 on 9 problems — contradictory weightings).
4. Length adjustment (A1.4) barely moves the coefficient (−0.117 → −0.108), so the residual is not a simple length artifact; log(length) itself predicts quality (+0.076, p=0.029) within ck.

**Conclusion:** F1 truncation explained the *strong, concentrated* form of the interim-1 reversal. A weak residual reversal survives correction and **cannot be adjudicated with pilot data** (F-T n=21 per persona cell, family-limited). This is exactly what the balanced main run (F-T for all 5 families, 19 problems, 2–3 reps) is for. Interim-1's CONTINUE decision is **confirmed, not undermined**, by this result.

## 4. Persona effect (F3 construct tension replicated under v2)

Per-dimension P − N (run-level dimension means):

| Dimension | v1 | v2 |
|---|---|---|
| Novelty | +0.126 | **+0.239** |
| Cultural Sensitivity | +0.066 | +0.068 |
| Flexibility | −0.126 | −0.053 |
| Elaboration | −0.481 | −0.448 |
| Usefulness | −0.526 | −0.576 |
| Composite | −0.194 | −0.154 |

Same signature, sharper: personas raise Novelty/CS and cut Elaboration/Usefulness. The construct–rubric tension (F3) is robust to full-text judging and stands as an interpretive finding for the paper.

## 5. 8-cell means (v1 → v2)

| cell | v1 | v2 | Δ |
|---|---|---|---|
| C-S-N | 4.337 | 4.343 | +0.01 |
| C-S-P | 4.126 | 4.160 | +0.03 |
| C-T-N | 4.396 | 4.404 | +0.01 |
| C-T-P | 4.122 | 4.206 | +0.08 |
| F-S-N | 4.457 | 4.461 | 0.00 |
| F-S-P | 4.296 | 4.303 | +0.01 |
| F-T-N | 4.507 | 4.533 | +0.03 |
| F-T-P | 4.476 | 4.579 | +0.10 |

Largest corrections where truncation was heaviest (team × persona cells) — consistent with A1.1.

## 6. Length sensitivity (A1.4), now on true full-text length

Family-specific r(log length, quality), v2: claude **−0.269** (p=0.012), gpt −0.334 (p=0.006), kimi +0.310 (p=0.004), gemini +0.687, qwen +0.586; pooled +0.521. The family dependence is confirmed with uncapped lengths (claude's negative correlation strengthens once true lengths are used). The pre-registered length-adjusted sensitivity analysis for the main run is justified as specified.

## 7. Inter-judge agreement (v2, run-level composites)

deepseek~zhipu r = 0.893 · deepseek~meta r = 0.454 · meta~zhipu r = 0.355. The Llama judge is the low-agreement member (consistent with its format non-compliance on run 997); the ensemble weighting is unchanged per the frozen instrument.

## 8. Decisions & next step

1. The v2 pilot table replaces v1 **for appendix/descriptive purposes only**; v1 files are retained untouched as the historical record (per LAUNCH-CHECKLIST hard rule 2).
2. Amendment A1 items A1.1–A1.4 are now empirically validated on real data; A1.5 is executed (this document).
3. **The main run (1,900 generations + 17,100 judgments) remains FROZEN pending explicit author confirmation.** Nothing in this analysis changes the launch plan; it only strengthens the case that the balanced main run is the correct adjudicator of the residual interaction.

### Limitations
- Run-level tests treat runs as independent (problem/family clustering only handled in the per-problem variant); pilot is descriptive by pre-registration.
- F-T pilot cells exist for 2 families only; all interaction statements are family-conditional.
- The 19 genuine model-ceiling runs were judged on inherently capped text; regeneration was out of scope (judging-only repair, A1.5).
