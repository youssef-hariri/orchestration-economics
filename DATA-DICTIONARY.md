# Data Dictionary

Schema of every data file in this repository. All timestamps ISO-8601 UTC.

## data/problems/business_problems_15.json
Object keyed by `Business_Problem_{n}`:
| Field | Type | Description |
|---|---|---|
| id | string | Problem ID (Business_Problem_1..15) |
| name | string | Snake-case short name |
| original_title | string | Human-readable title |
| background_context | string | Scenario context given to agents |
| business_problem | string | The task statement (prompt body) |

Provenance: LLM-Creativity repo (DOI 10.5281/zenodo.17407392), verbatim.

## data/problems/business_problems_domain_15.json
Object keyed by `Business_Problem_{16..30}` — same fields as above plus:
| Field | Type | Description |
|---|---|---|
| domain | string | One of the 6 pre-registered business domains |
| created | string | Draft date |
| provenance | string | Author-drafted domain-stratified extension set (MANIFEST Entry 4) |

## data/problems/domain_map.json
Pre-registered 6×5 domain stratification of the 30 main problems:
`domains` (array of 6 domain ids) + `map` (problem_id → domain). Original-15 tags
PENDING author confirmation before the preregistration freeze. Fresh_Case_1–10 are
excluded (out-of-sample robustness set).

## data/personas/cultural_personas.json
Array of persona objects:
| Field | Type | Description |
|---|---|---|
| id | string | Culture_5 / Culture_Expert / Culture_11 |
| assigned_role_congruent | string | Pre-registered congruent role (builder/critic/refiner) |
| source | string | Provenance |
| description | string | Verbatim persona system-prompt text |

## pipelines/fixed/{arm}.json and pipelines/adaptive_A7/{problem_id}.json
DeeWaanAI `exportPipeline` format: ordered steps with
`name, role, systemPrompt, provider, model, temperature, maxTokens, stepType, ifConfig, whileConfig`.
For A7, an additional sibling file `{problem_id}.designer_raw.txt` stores the designer model's
unedited output.

## runs/responses/{arm}/{problem_id}/rep{n}.json
One file per pipeline run:
| Field | Type | Description |
|---|---|---|
| run_id | int | DeeWaanAI swarmRuns id |
| arm | string | A1..A8 |
| problem_id | string | Business_Problem_n (1–30) or Fresh_Case_n |
| rep | int | 1..5 |
| started_at / finished_at | string | timestamps |
| steps[] | array | Per step: step_order, agent_name, role, persona_id, provider, model, temperature, system_prompt, input, output, tokens_prompt, tokens_completion, tokens_total, latency_ms, critic_verdict (if applicable), iteration |
| final_solution | string | Last step output (the judged artifact) |
| total_tokens | int | Sum across steps |
| total_latency_ms | int | Sum across steps |

## runs/ledger.csv (execution resilience — plan §4.9)
Full randomized interleaved run list, generated ONCE at preregistration (seed 42) and
never regenerated. One row per planned run; the executor is a pure function of this file
(scan → skip DONE → requeue FAILED_RETRYABLE → execute PENDING). Credit outage or
disconnect simply leaves rows PENDING; resume is idempotent.
| Field | Type | Description |
|---|---|---|
| run_key | string | `{cell_or_arm}__{family}__{problem_id}__rep{n}` (unique, doubles as response filename stem) |
| cell | string | C-S-N..F-T-P or A5..A8 |
| family | string | gpt / claude / gemini / kimi / qwen |
| problem_id | string | Business_Problem_n or Fresh_Case_n |
| rep | int | 1..5 |
| planned_order | int | Position in the seed-42 randomized interleaving |
| status | enum | PENDING / RUNNING / DONE / FAILED_RETRYABLE / FAILED_PERMANENT |
| attempts | int | Retry count (max 3, backoff 5/30/120 s) |
| swarm_run_id | int? | DeeWaanAI swarmRuns id once launched |
| tokens_total | int? | From logs after completion |
| cost_usd | float? | tokens × pinned price sheet |
| started_at / finished_at | string? | ISO-8601 UTC |
| last_error | string? | Last failure message (FAILED_* rows only) |

## runs/logs/
Raw `runStatus` / `exportMyData` exports (JSON), untouched, one per phase.

## evaluation/judge_prompts/judge_variations.jsonl
3 lines, one per variant (var1..var3): `id, source, description` (prompt template with
`{problem_text}` and `{solution_text}` placeholders). Dimensions scored (1–5):
Novelty (PRIMARY), Usefulness/Feasibility, Flexibility, Elaboration, Cultural Sensitivity.

## evaluation/judge_raw/{study}/{solution_id}__{judge}__{variant}.json
One file per judge call (materialized by `code/materialize_results.py` from the frozen
judgment JSONL logs; `{study}` = study1_main | wave).
| Field | Type | Description |
|---|---|---|
| solution_id | string | `{cell}__{family}__{problem_id}__rep{n}` (corrected 2026-08-28, D54: the pre-factorial scheme `{arm}__{problem}__{rep}` was not unique across families) |
| judge_provider / judge_model | string | pinned judge |
| variant | string | var1..var3 |
| raw_response | string | Unparsed judge output |
| scores | object | novelty, usefulness, flexibility, elaboration, cultural_sensitivity (1–5) |
| parsed_ok | bool | Parser success flag |

## evaluation/scores_aggregated.csv
One row per solution × judge × variant (long format), 17,091 rows:
`study, solution_id, run_id, cell, family, problem_id, rep, condition, judge_family, judge_model, variant, composite, novelty, usefulness, flexibility, elaboration, cultural_sensitivity`
Plus companion `kappa_by_dimension.csv`: `dimension, fleiss_kappa, n_solutions, computed_by`
(9-rater matrix per solution; descriptive, computed by materialize_results).

## analysis/results/ (materialized reviewer layer, D54)
`INDEX.csv` lists every file. Key tables: `descriptive_stats.csv` (cell × dimension),
`effect_sizes.csv` (Interim-2 H1–H5 + Amendment A3, flattened from frozen JSONs),
`heterogeneity_battery.csv` (D44/D45), `tegr_by_arm.csv`, `wave_scores_aggregated.csv`
(21,762 rows), `wave_gates.csv` (W1–W7 × both price vectors),
`refine_scores_aggregated.csv` + `study2_refine_results.csv` (Studies 2/2b),
`qual_codebook_kappa.csv` (13 codes + pooled κ, gate column), `qual_code_application.csv`
(per-text × coder code vectors), `qual_a4_themes.csv`, `qual_a4_kappa.csv`,
`qual_study2_analysis.csv`. All regenerated idempotently by `code/materialize_results.py`;
confirmatory numbers are flattened verbatim from frozen `results/*.json`, never recomputed.

## analysis/results/
- `descriptive_stats.csv` — mean/sd/n by arm × dimension
- `effect_sizes.csv` — planned contrasts, Cohen's d, 95% bootstrap CI (5,000 resamples), FDR-adjusted p
- `mixed_model_results.csv` — fixed/random effects estimates
- `tegr_by_arm.csv` — cost (from logs), novelty, T-EGR per arm
- `figures/` — incl. cost–novelty frontier plot

## MANIFEST.md
Append-only provenance log: phase, date, git commit, pinned model versions, runs executed,
actual cost from token logs.
