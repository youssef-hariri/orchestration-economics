# Protocol 14 — Study 4: Loop Control (Who Drives the OODA Cycle)

**Status: DRAFT — NOT REGISTERED. No generation, judging, or analysis call may be made under
this protocol until (a) author go-ahead, (b) OSF registration timestamped BEFORE first data
collection, (c) registration ID recorded here.**

**Lineage:** executes and completes the pre-registered-but-unexecuted arm A5 (critic-gated
WHILE loop, H4), expanded to a Controller-Tier design. The OODA loop (Boyd) is used as the
motivating decision-cycle framework: the Critic gate is the Observe–Orient checkpoint, the
Refiner re-pass is Decide–Act. OODA motivates the dose-response prediction; it is not itself
the mechanism claimed.

---

## 1. Research question

Does iterative feedback (a critic-gated loop) close the cheap-team → frontier-solo gap, and
does the *tier of the loop controller* (who evaluates and gates each cycle) matter?

Study 2 established the refinement prior: one refinement pass recovers 60–64% of the gap on
saturating families and buys coverage, not density. Study 4 tests the dose-response curve.

## 2. Design

**2 (controller tier) × 5 (family), executor pool fixed = family's pinned cheap sibling.**

| Arm | Builder/Refiner | Controller (critic + gate) | Construct |
|---|---|---|---|
| L-SELF | cheap sibling | cheap sibling | self-regulated OODA cycle (executes A5's construct) |
| L-FRONT | cheap sibling | family's frontier | frontier-directed cycle: capability transfer via evaluation |

- Loop: Builder → Critic (verdict: PASS / REFINE + feedback) → if REFINE, Refiner → Critic …
  up to **maxIterations = 3** (fixed, locked). The Critic's verdict schema is frozen verbatim
  across arms; only the controller model differs.
- **Every iteration's intermediate output is stored** (dose-response requires per-cycle
  quality; judging is applied to the output of EACH completed cycle, not only the final one).
- Controller and builder tokens all charged to arm cost (D30 precedent).

**Controls (frozen, no new runs):** C-T-N (no loop), F-S-N (benchmark), Study-2 single-pass
refinement results (the 1-cycle point on the dose-response curve, kimi/claude/qwen).

## 3. Stimuli and sample

- Problems: the 19 confirmatory problems (same exclusion rule as Study 1).
- Reps: 3. Runs: 2 arms × 5 families × 19 × 3 = **570 pipeline runs**
  (each run = 1–3 cycles depending on gate; expected LLM calls ≈ 570 × ~5).
- Judging: frozen panel × 3 verbatim variants, blinded, temp 0, `judge_v2.py` unchanged —
  applied per cycle output. Worst case 570 × 3 cycles × 9 = 15,390 judge calls.

## 4. Hypotheses (directions locked pre-registration)

- **H-L1 (plateau, directional):** marginal composite gain per cycle is positive at cycle 1→2
  and ≤ 0 at cycle 2→3 (Boyd: bounded static task ⇒ convergence once the environment stops
  changing; Study-2 refinement plateau). Segmented regression on cycle index.
- **H-L2 (controller transfer, directional):** L-FRONT > L-SELF on final-cycle composite.
  Ground: Study-2b outsider-refiner advantage (pooled d = −0.348).
- **H-L3 (superiority rejection, confirmatory-negative):** no loop arm exceeds F-S-N beyond
  SESOI d = 0.30 — superiority formally rejected if all CIs cross below it.
- **H-L4 (mechanism):** per-cycle gains concentrate in structural/Elaboration dimensions, not
  Novelty (replicates the Study-2 coverage-not-density code pattern quantitatively).

## 5. Gates (D31 logic)

- **G1:** loop terminates mechanically at maxIterations (no infinite-loop budget risk);
  completion ≥ 90% on a 4-problem pilot per arm × family.
- **G2:** stop on clear futility only — pilot L-FRONT final-cycle composite below frozen C-T-N
  by d < −0.30. Otherwise full run. All executed arms reported.

## 6. Analysis plan (locked)

- Dose-response: LMM `composite ~ cycle * arm` with family random effect (D52 fallback rule
  declared in advance); segmented regression with pre-locked breakpoint at cycle 2.
- H-L2: final-cycle L-FRONT vs L-SELF, Welch d + bootstrap CI (seed 42), Holm within family.
- H-L3: per-arm paired contrast vs frozen F-S-N; superiority gate G1/G2 logic as in Protocol 09
  (rules locked before computation — anti-cherry-picking).
- H-L4: dimension-level per-cycle decomposition, BH-FDR.
- Economics: cumulative tokens × frozen price vector; cost-per-cycle and cost-per-point-gained;
  Pareto position vs the frozen Study-1 frontier; T-EGR.

## 7. Execution discipline

Same as Protocol 13 §7 (ledger, raw storage, window, deviation rule). If Protocol 13 runs
first, its designed pipelines are NOT reused here — loops use the frozen C-T topology with the
loop config added, so Study 3 and Study 4 stay separable.

## 8. Budget envelope (estimate, verify at registration)

Worst case ≈ 3,400 cheap LLM calls + ~570 frontier controller calls + ≤ 15,390 judge calls.
Order of magnitude **≤ $60**. Pilot ≈ $6 inside the envelope.

## 9. Open decisions (before OSF registration)

1. maxIterations = 3 (recommended) vs 4 — dose-response resolution vs cost.
2. Judge every cycle (recommended; enables H-L1/H-L4) vs final cycle only (3× cheaper, kills
   the dose-response analysis).
3. Critic verdict schema: reuse Study-1 frozen critic prompt verbatim (recommended) vs a
   loop-specific prompt (breaks comparability with A5's frozen construct).
