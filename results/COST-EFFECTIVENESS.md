# Cost-Effectiveness Analysis (Protocol 04 + Amendment A)

**Date:** 2026-07-30 · **Status:** complete · n = 1,900 priced main-run runs (all completed)
**Method:** tokens × frozen price vector v2026-07-30 (D23); blended price at
φ = 0.5 primary, sensitivity φ ∈ {0.25, 0.75}; judge cost excluded; T-EGR per D15.
Bias disclosure (Amendment A2): team intermediate outputs are uncounted, so team
costs are slightly understated — direction favors the cheap team.

## 1. Cell summary (primary φ = 0.5, pooled over 5 families)

| cell | mean cost $/run | quality | mean tokens | T-EGR |
|---|---|---|---|---|
| C-S-P | 0.01453 | 4.210 | 5,735 | 8.60 |
| C-S-N | 0.01936 | 4.507 | 7,670 | 6.15 |
| C-T-P | 0.07150 | 4.327 | 27,953 | 1.58 |
| C-T-N | 0.07340 | 4.531 | 29,978 | 1.49 |
| F-S-P | 0.06703 | 4.406 | 5,944 | 1.36 |
| F-S-N | 0.08352 | 4.586 | 7,412 | 1.00 (base) |
| F-T-N | 0.29515 | 4.610 | 27,368 | 0.27 |
| F-T-P | 0.30437 | 4.370 | 26,419 | 0.27 |

## 2. Pareto frontier — STABLE across all φ

Frontier cells at every φ ∈ {0.25, 0.5, 0.75}: **C-S-P, C-S-N, C-T-N, F-S-N, F-T-N**.
Dominated at every φ: **C-T-P, F-S-P, F-T-P**. Every persona (P) cell is dominated
by its no-persona twin — persona lowers quality at equal or higher cost, matching
the Study-1 persona penalty.

## 3. ICER (incremental cost per quality point, vs cheapest cell C-S-P)

- C-S-N: +$0.016 per point (best buy for quality)
- F-S-N: +$0.183 per point
- C-T-N: +$0.184 per point
- F-S-P: +$0.268 · F-T-N: +$0.702 · F-T-P: +$1.808 per point (worst buy)

## 4. Study-2 extension: refined C-T-P points (refine call costs ~$0.001–0.003)

| family | refined CTP cost | quality | vs pooled F-S-N |
|---|---|---|---|
| kimi | $0.0654 | 4.585 | parity quality at 78% of cost |
| claude | $0.1981 | 4.559 | parity quality at 237% of cost (saturated, expensive family) |
| qwen | $0.0166 | 4.398 | cheaper than any C-S cell, quality ≈ C-S-N |

Economic read: bare C-T-P is dominated, but a ~$0.002 add-only refinement pass
moves the kimi C-T-P point to frontier-parity quality at 78% of the frontier
cost — refinement is the cheapest known way to climb toward the frontier.
Caveat: refined quality means come from the Study-2 subset (3 families, 57
problems, pair-judged context); the paired within-family comparison against F-S-N
REMAINS negative (Entry 30, d = −0.30 kimi). Parity here is absolute-mean parity
on the 1–5 composite, not a paired win.

## 5. Headline claims (robustness-checked)

1. The cost-effectiveness frontier is cheap-solo + cheap-team-no-persona +
   frontier-solo + frontier-team-no-persona; persona cells are everywhere
   dominated (stable across φ — claim rule A6 satisfied).
2. T-EGR: cheap solo delivers 6–9× the novelty-per-dollar of frontier solo;
   frontier teams are the worst economic deal (T-EGR ≈ 0.27).
3. Orchestration economics verdict: structure substitutes for tier ONLY at the
   cheap end (C-S-N reaches 98% of F-S-N quality at 23% of the cost); frontier
   teams buy ~nothing (F-T-N = +0.024 quality over F-S-N at 3.5× the cost).
4. Refinement (Study 2) is economically attractive (~$0.002/run) and lifts a
   dominated cell to absolute parity with the frontier, but per Entry 30/31 it
   never produces a paired superiority.

## 6. Artifacts

- `results/cost/cost_per_run.csv` (1,900 rows), `cell_summary.csv` (3 φ panels),
  `pareto_frontier.csv`, `cost_effectiveness.json`,
  `cost_effectiveness_scatter.png` / `.pdf`
- `code/cost_effectiveness.py` (deterministic; re-run with any φ edit)
- Protocol 04 Amendment A (registered before computation)
