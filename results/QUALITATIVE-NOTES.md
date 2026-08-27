# Pilot Qualitative Diagnostics — Exploratory Notes (Pre-Main-Run)

**Date:** 2026-07-30 · **Status:** EXPLORATORY — does not modify the frozen pre-registered analysis plan.
Any change adopted for the main run requires a documented protocol amendment + re-registration.
**Data:** 371 pilot runs (Phase A 329 + Phase B 42), 3,339 judgments. No new experiments run; all findings derive from archived pilot data only.

---

## Finding 1 (MAJOR): The inverted tier×structure interaction is attributable to a response-truncation artifact

**The cap.** The platform's `run_status` MCP tool truncates `finalResponse` to 16,000 chars
(`api/mcp/tools/getRunStatus.ts` → `MAX_RESPONSE_CHARS = 16000`, `truncate()` in `api/mcp/tools/_shared.ts`,
marker `…[truncated]`). The pilot runner read answers through this tool, and **the judges scored the
truncated text** (`code/judge_phaseA.py` injects `sol["finalResponse"]` into the rubric).

**Prevalence.** 130 / 371 runs (35.0%) sat exactly at the 16,012-char cap. Truncation is *confounded with the design*:

| cell | truncated rate |
|---|---|
| cheap team (C-T) | 0.75 |
| cheap solo (C-S) | 0.41 |
| frontier team (F-T) | 0.26 |
| frontier solo (F-S) | 0.12 |

Teams aggregate 3 agents' content → longer answers → disproportionately clipped. Judges then score mid-sentence, mid-table endings.

**Consequence.** The interaction contrast d = (F−T − F−S) − (C−T − C−S) on claude+kimi:

- all runs: **−0.161 (p = 0.018)** — the "inverted" effect from interim-1
- non-truncated runs only: **−0.013 (p = 0.90)** — *vanishes*
- truncated runs only: **−0.277 (p = 0.008)** — the inversion lives entirely in clipped answers

**Recovery path.** Full-length answers are preserved in the granular archive
(`runs/granular/*.json` → `export.agentResponses[0].content`): for 111 of the 130 capped runs the archive
content exceeds the cap. Re-judging those 130 runs from full text is feasible at modest judging cost and
would yield an artifact-corrected pilot estimate — *proposed, not executed* (awaiting user decision + discount window).

---

## Finding 2 (MAJOR): deepseek-chat judgments are truncated, systematically dropping Cultural Sensitivity

**442 / 16,695** individual dimension scores are null (2.65%). Composition:

- **356 / 442 (80.5%) are deepseek-chat**, and 334 of those are *Cultural Sensitivity* with the dimension
  **never mentioned** in the justification text.
- Root cause visible in `raw`: deepseek-chat justifications end mid-sentence inside the Elaboration
  section (e.g., "...This solution is exhaustively detailed." / raw_len ≈ 2,400–2,700 chars) —
  the judge's max output tokens is too small; the 5th dimension is never emitted.

**Implication:** Cultural Sensitivity scores currently rest effectively on 2 of 3 judges, and deepseek-chat
contributed to the other 4 dimensions with a systematic style (verbose justifications). Not fatal for the
pilot's composite DV, but must be fixed before the main run (raise judge max_tokens and/or reorder dimensions).

---

## Finding 3: Persona effect is construct-valid but rubric-conflicted (dimension decomposition)

Qualitative reading of paired outputs (e.g., BP10, claude) shows Culture_5 is **faithfully embodied** —
indirect, suggestive, understated style ("perhaps the more interesting question is...", hints over prescriptions) —
and this style mechanically shortens outputs: P-cell outputs average 9,732 vs 11,720 chars for N-cells (−17%);
extreme case BP10: 12,296 → 4,336 chars.

Per-dimension persona effect (P − N):

| dimension | diff |
|---|---|
| Novelty | **+0.126** |
| Cultural Sensitivity | **+0.079** |
| Flexibility | −0.125 |
| Elaboration | **−0.486** |
| Usefulness | **−0.526** |

Interpretation: the persona *works as designed* (more novel, more culturally attuned) but the indirect
communication style reduces prescriptiveness and coverage — the dimensions the rubric weights heavily.
The negative persona main effect is therefore a **persona-style × rubric-construct tension**, not a
persona failure. This is itself a publishable observation for the paper (persona effects are
dimension-dependent; aggregating to a single composite conceals it).

---

## Finding 4: Length–quality correlation is family-dependent (length-bias risk)

Pearson r between output length (as stored, i.e., post-cap) and composite quality:

- all runs: **+0.507** (p < 1e-25)
- claude −0.059 (ns), gpt −0.347, kimi +0.440, gemini +0.660, qwen +0.619

Length-adjusted interaction (OLS, run-level): claude interaction remains −0.164 (p = 0.024) after
log(length) control — but note length here is contaminated by the cap, so this adjustment is unreliable
until full-text re-judging is done. Register length as a robustness covariate for the main run.

---

## Recommendations for the main run (require protocol amendment + re-registration before adoption)

1. **Score full answers.** Retrieve `agentResponses.content` via the archive/export path (or raise/
   bypass the run_status cap) instead of the truncated `finalResponse`; log a truncation flag per run.
2. **Fix the judge emission.** Raise judge max_tokens (and/or move Cultural Sensitivity earlier in the rubric);
   add a post-judgment integrity check (all 5 dimensions present) with automatic retry.
3. **Register length diagnostics.** Output length per run + length-adjusted sensitivity analyses as
   pre-registered robustness checks.
4. **Optional pilot repair.** Re-judge the 130 capped pilot runs from granular-archive full text
   (judging-only cost) to produce an artifact-corrected pilot table for the paper appendix.

## Guardrails honored

- No new experiment runs; no new credits consumed beyond analysis.
- Pre-registered plan, family selection, and interim-1 decision (CONTINUE) stand unchanged until a formal amendment is filed.
