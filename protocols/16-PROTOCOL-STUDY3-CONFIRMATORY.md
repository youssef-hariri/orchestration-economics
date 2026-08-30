# Protocol 16 — Study 3 Confirmatory Replication: Is the Family-Specific Orchestration Rule Robust Out-of-Sample?

**Status: REGISTERED — OSF Open-Ended Registration `zkm8v` (https://osf.io/zkm8v),
timestamped 2026-08-30 BEFORE first data collection (D59/D60; runner `code/study3conf_run.py`).**
(The OSF API returned a transient 502 on submit but the registration succeeded; id recovered
from the draft's registration link, state file updated.)

**Lineage:** Study 3 (Protocol 13, OSF 9ukjz/bwc93/639eq) produced a family-specific
routing rule — cheap auto-designed pipelines beat frontier solo for gemini/qwen/kimi,
tie gpt, lose for claude — but on the SAME 19 problems as Study 1. This protocol is the
out-of-sample confirmatory test, exactly as the wave (Protocol 12) was for Study 1.

---

## 1. Research question

Does the Study 3 per-family sign pattern (D-SELF vs F-S-N on Novelty) replicate on
fresh, post-cutoff problems the design stage has never seen?

## 2. Scope decisions (pre-registered, justified from Study 3 results)

- **D-SELF arm only.** Study 3 Contrast A found no authorship effect in 4/5 families
  (the claude exception is an executor-capability artifact: D-FRONT was still far below
  opus-solo, d = −2.84). Per this pre-declared decision rule, D-FRONT is dropped; the
  authorship evidence stands from Study 3 and is not retested here.
- **Comparator:** the wave's already-completed, already-judged F-S-N runs on the same
  30 fresh problems (Protocol 12; frozen judgments) — zero new frontier-solo generation.
- **Problems:** the 30 wave problems (`fresh_business_cases_10.json` +
  `fresh_business_cases_20_wave.json`), post-cutoff, zero overlap with Study 1/3.
- **Families:** the 5 core families (kimi, qwen, gpt, claude, gemini) — the replication
  must match the claim. No new families (generalization is a separate question).

## 3. Design

**1 arm (D-SELF) × 5 families × 30 problems × 3 reps = 450 runs.**
Instrument: identical to Study 3 v2 (D56, `protocol13-v2` platform-verbatim auto-design
prompt, free roles, if/while gates, 1–7 steps, temp 0.3, no approval steps). Executor =
family's pinned cheap sibling; designer = same cheap sibling. Same validation, same
repair-retry rule, same `design_failed` disclosed attrition handling (D57 rule:
completion ≥ 80% per family excluding moderation blocks, reported both ways).

## 4. Binding pre-registered predictions (upgrade gates, Novelty, one-sided α = 0.05)

From Study 3's frozen results (`results/study3_vs_frontier_solo.json`):

| Gate | Family | Prediction (D-SELF vs F-S-N) |
|---|---|---|
| R1 | kimi | d > 0 (Study 3: +0.85) |
| R2 | qwen | d > 0 (Study 3: +0.55) |
| R3 | gemini | d > 0 (Study 3: +0.46) |
| R4 | gpt | \|d\| < 0.30 (equivalence; Study 3: −0.07) |
| R5 | claude | d < −1.0 (Study 3: −3.15) |

A gate passes if the confirmatory estimate is in the predicted direction/range at the
stated alpha (R4: TOST-style bound, both one-sided tests at α = 0.05). The headline
claim "family moderates orchestration gains" requires R1–R3 and R5 to pass; R4 guards
the gpt tie. No post-hoc relabeling in either direction (D44/wave discipline).

## 5. Judging and analysis

Frozen three-judge panel (deepseek-chat, GLM-5.2, Llama-3.3-70B) × 3 verbatim variants,
judge_v2 unchanged; DeepSeek judged in off-peak windows. Primary analysis: per-family
Cohen's d on Novelty vs the frozen wave F-S-N per-problem means; problem-level pairing
where the wave provides per-problem F-S-N scores. Analysis script frozen and hash-locked
before judging. All stat results ship as JSON in `results/` + CSV in `analysis/results/`
(D54). Provider/credit events disclosed, not imputed (qwen deferred to its discount
window; kimi designer via Moonshot, executor per registry).

## 6. Budget note

D-SELF-only + zero comparator regeneration halves the cost vs a naive replication
(~450 cheap-tier pipeline runs; no D-FRONT, no new F-S-N, judge cost on 450 × 9).
