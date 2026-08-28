# code/ — all executable code for the experiment

**Rule (MANIFEST Entry 6):** every script that is created and run at any phase of this
experiment is committed here (or in `analysis/`) BEFORE its outputs are trusted. No result
in this repository may exist without the committed code that produced it. Anyone with API
keys and `config/experiment_config.json` must be able to re-run the entire experiment.

## Planned scripts (committed as each phase begins)

| Script | Phase | Purpose |
|---|---|---|
| `make_ledger.py` | Phase 1 (preregistration) | Generate `runs/ledger.csv`: full randomized, arm-interleaved run list (seed 42). Run ONCE, committed with the preregistration tag, never regenerated. |
| `run_experiment.py` | Phases 1–2 | Ledger-driven executor via DeeWaanAI MCP: scan ledger → skip DONE → requeue FAILED_RETRYABLE → execute PENDING (≤4 concurrent, 3 retries, 5/30/120 s backoff). Idempotent — safe to re-launch after credit outage/disconnect. Writes `runs/responses/` + updates ledger. |
| `judge_solutions.py` | Phase 2 | Judging harness: 3 judges × 3 frozen prompt variants per solution, blinded and randomized order; writes `evaluation/judge_raw/` with `parsed_ok` gate. |
| `aggregate_scores.py` | Phase 2 | Parse judge_raw → `evaluation/scores_aggregated.csv` + `kappa_by_dimension.csv`. |
| `../analysis/stats.py` | Phase 4 | Full statistical pipeline (adapted from persona-model-fit `stats_with_anlysis.py`): mixed models, effect sizes + bootstrap CIs, FDR, BFs, robustness battery, T-EGR, figures. |
| `requirements.txt` | Phase 0 | Pinned Python dependencies (exact versions) for all scripts. |

## Reproducibility conventions (all scripts)
- Random seed **42** everywhere randomness exists (ledger shuffle, bootstrap, splits, Isolation Forest).
- All configuration read from `config/experiment_config.json` — no hard-coded models, prices, or temperatures.
- Scripts are idempotent: re-running never duplicates or overwrites completed work.
- Secrets via environment variables only (`.env` is git-ignored); never committed.
- Each script's header documents: usage command, inputs, outputs, phase.

## materialize_results.py (D54, 2026-08-28)
Emits the reviewer-facing CSV/JSON layer (`evaluation/scores_aggregated.csv`,
`evaluation/kappa_by_dimension.csv`, `evaluation/judge_raw/<study>/`, all of
`analysis/results/`) from frozen artifacts. stdlib-only, idempotent, zero API calls,
never recomputes a hypothesis test (confirmatory numbers flattened verbatim from
`results/*.json`; only descriptives computed, labeled `computed_by=materialize_results`).
**Standing rule:** every new analysis writes `results/<name>.json` AND is added here.
Run: `python3 code/materialize_results.py`
