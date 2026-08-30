> **STATUS 2026-08-30: SUPERSEDED BY STUDY 3 (D59, author ruling). Not executed. See DESIGN-DECISIONS.md D59 and MANIFEST Entry 79. Retained unmodified below for the audit trail.**

# Protocol 15 — Study 5: The Router (Predictive Contingency Model)

**Status: DRAFT — NOT REGISTERED. Phase 1 uses ONLY frozen, already-collected data and needs
no OSF generation registration; it is registered anyway (analysis pre-registration) if
proceeding. Phase 2 involves new generation and requires its own OSF registration BEFORE the
first call.**

**Lineage:** operationalizes the oracle-portfolio analysis (D19) into a predictive test, and
converts the paper's contingency model (§5 decision table) into a falsifiable artifact.
Dual purpose: academic capstone + DeeWaanAI auto-recommendation feature validation.

---

## 1. Research question

Can a cheap model, given ONLY the problem text, predict which orchestration cell (C-S-N /
C-T-N / F-S-N / …) will be cost-quality optimal for that problem — and how much of the
oracle ceiling does that capture?

## 2. Phase 1 — Retrospective (zero new generation)

- **Data:** frozen Study-1 (1,900 runs) + wave (2,050+ judged runs) records only.
- **Oracle:** per problem, the cell maximizing composite quality subject to a cost ceiling
  swept over the observed cost range (a frontier, not a single label — avoids arbitrary
  cost-cutoff choice). Ground: D19 oracle-portfolio construct.
- **Router:** a pinned cheap model (per registry) receives problem text (+ optionally the
  domain tag) and outputs a cell choice + rationale. Temperature 0. N problems × R prompt
  variants (≥2, frozen at registration) to measure routing stability.
- **Metrics (locked):** routing accuracy vs oracle; regret = oracle quality − router-pick
  quality (in composite points and in $); value captured = (router regret) / (worst-cell
  regret) normalized; per-domain breakdown.
- **Hypotheses:**
  - **H-R1 (directional):** router regret < random-cell-selection regret (bootstrap CI
    excludes 0, seed 42).
  - **H-R2 (descriptive, no direction committed):** router errors concentrate in domains where
    the wave showed cell rankings unstable (cf. W3 failure — honest prior: the marketing
    flip predicts weak routing signal there).
- **Cost:** router calls ≈ 30 problems × few variants × 2 datasets ≈ **< $2**.

## 3. Phase 2 — Prospective validation (gated; separate registration)

Only if H-R1 passes. On the 10 reserved Fresh_Case problems (never touched by any prior
analysis — D14 contamination control), the router picks a cell per problem; those pipelines
are executed and judged (frozen panel); realized regret vs oracle computed on the new data.
- Runs: ≤ 10 problems × 1 routed cell × 3 reps + the oracle requires the other cells too
  (10 × ~3 cells × 3 reps ≈ 90–150 runs + judging ≈ 1,350 calls). Envelope **≤ $25**.
- **G-R gate:** proceed to Phase 2 only if Phase-1 H-R1 passes with regret reduction ≥ 30%
  vs random (threshold locked here).

## 4. Product coupling (disclosed dual purpose)

The router prompt, schema, and regret metrics are designed to be directly deployable as
DeeWaanAI's recommendation layer. This dual purpose is disclosed in the paper (the platform
is the declared apparatus; routing is its planned service feature). Academic claims rest
only on pre-registered metrics, not on product outcomes.

## 5. Analysis plan (locked)

- Phase 1: bootstrap CIs on regret/accuracy (seed 42, 5,000 resamples); permutation null for
  H-R1; per-domain and per-dataset (Study-1 vs wave) breakdowns; BH-FDR across domains.
- Phase 2: realized regret vs Phase-1 expectation; equivalence test (TOST, SESOI d = 0.20,
  A3.2 precedent) for "prospective matches retrospective".

## 6. Discipline

- Phase 1 reads frozen artifacts only; no write path to Study-1/wave records.
- Fresh_Case_1–10 remain untouched until Phase 2's own registration exists.
- Router prompts frozen at registration; never re-optimized (D10 lesson).

## 7. Open decisions (before registration)

1. Router model: one pinned cheap model (recommended: deepseek-chat, disjoint from all
   generator families in both datasets) vs a small router panel.
2. Oracle definition: cost-ceiling sweep (recommended) vs single T-EGR-maximizing cell.
3. Whether Phase 1 registers standalone or jointly with the Phase-2 gate.
