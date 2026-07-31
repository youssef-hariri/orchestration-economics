# Orchestration Economics — Experiment Repository

Companion repository for the paper:
> *The Economics of Orchestration: Can Culturally-Composed Teams of Small Language Models
> Outperform Frontier Models at Equal Cost? A Cost-Matched Experiment on Business Solution Generation*

Author: Youssef Hariri — Doctoral student, Business of AI, Rennes School of Business
Apparatus: DeeWaanAI multi-agent pipeline platform (all runs executed via its MCP interface).
Full research plan: `RESEARCH-PAPER-PLAN.md` (snapshot committed in this repo; working copy
lives in the workspace at `DeeWaanAI-Next/RESEARCH-PAPER-PLAN.md`) — §8 defines this repo.

## Traceability principle

**Nothing exists only in the platform database.** Every artifact — pipeline definitions,
per-step responses, token/latency logs, judge prompts and raw scores, analysis outputs —
is exported to files in this repository, committed, and (at publication) deposited on Zenodo.

## Repository layout

| Path | Contents | Populated in |
|---|---|---|
| `PROTOCOL.md` | Frozen pre-registration (hypotheses, arms, analysis plan) | Phase 1 (tagged `preregistration`) |
| `DATA-DICTIONARY.md` | Schema of every data file | now |
| `DESIGN-DECISIONS.md` | Decision register: every design/statistical decision + academic grounding (feeds the Methodology section) | every phase |
| `MANIFEST.md` | Provenance log: dates, pinned model versions, costs | every phase |
| `config/experiment_config.json` | Model tiers, pinned versions, prices, judges, designer | Phase 0 |
| `data/problems/business_problems_15.json` | The 15 validated business problems (from LLM-Creativity, DOI 10.5281/zenodo.17407392) | committed |
| `data/problems/business_problems_domain_15.json` | 15 author-drafted domain-stratified problems (Business_Problem_16–30) | committed |
| `data/problems/domain_map.json` | Pre-registered 6×5 domain grid over the 30 main problems | committed |
| `data/problems/fresh_business_cases_10.json` | 10 post-cutoff contamination-control cases (2026 scenarios) | committed |
| `data/personas/cultural_personas.json` | 3 cultural personas (from persona-model-fit, DOI 10.5281/zenodo.19533619) | committed |
| `code/` | ALL executable code (ledger generator, run executor, judging harness, aggregation) + pinned `requirements.txt` — no result exists without its committed code | Phases 0–2 |
| `pipelines/fixed/` | Exported pipeline JSON for arms A1–A6, A8 (`exportPipeline`) | Phase 0 |
| `pipelines/adaptive_A7/` | Per-problem designer outputs + resulting pipeline JSON | Phase 2 |
| `runs/responses/{arm}/{problem}/rep{n}.json` | Full per-step outputs of every run | Phases 1–2 |
| `runs/logs/` | Per-run token/latency/model logs (`runStatus`, `exportMyData`) | Phases 1–2 |
| `evaluation/judge_prompts/` | The 3 frozen judge prompt variants | Phase 0 |
| `evaluation/judge_raw/` | Every judge call: prompt + raw response + parsed score | Phase 2 |
| `evaluation/scores_aggregated.csv` | 9 scores per solution + Fleiss' κ | Phase 2 |
| `analysis/stats.py` | Statistical analysis (adapted from persona-model-fit) | Phase 4 |
| `analysis/results/` | Tables and figures (incl. T-EGR cost-novelty frontier) | Phase 4 |

## Experimental design (summary)

**2×2×2 within-family factorial**: Tier (Frontier vs Cheap sibling) × Structure (Solo vs
3-step Team) × Persona (None vs Persona-loaded), crossed within 5 model families
(GPT, Claude, Gemini = Western; Kimi, Qwen = Eastern). Teams are **model-homogeneous**
(all 3 agents same model; only persona/role prompts differ).

| Cell | Description | Families × reps |
|---|---|---|
| C-S-N | Cheap solo, no persona (true baseline) | 5 × 3 |
| C-S-P | Cheap solo + Culture_5 (bridge to *Doing More with Less*) | 5 × 3 |
| C-T-N | Cheap team, no personas (orchestration-only control) | 5 × 3 |
| **C-T-P** | **Cheap persona-diverse team** (Culture_5 Builder → Culture_Expert Critic → Culture_11 Refiner) — core | 5 × 3 |
| F-S-N | Frontier solo, no persona (multicultural frontier pool) | 5 × 2 |
| F-S-P | Frontier solo + Culture_5 | 5 × 2 |
| F-T-N | Frontier team, no personas (frontier orchestration benchmark) | 2 × 2 |
| F-T-P | Frontier team, persona-diverse (persona value at frontier) | 2 × 2 |

Special arms (one pre-registered cheap family, original 15 problems only): A5 = C-T-P +
Critic-gated WHILE loop (H4); A6 = frontier solo **cost-matched** to C-T-P (baseline =
best-Novelty F-S-N frontier, pre-registered rule); A7 = **adaptive** — **Kimi V3** (temp 0)
designs per problem, cheap models execute; A8 = C-T-P with shuffled persona→role mapping (H5).

**Pinned models (Phase 0, 2026-07-30, 16/16 live-verified):** gpt-5.6-sol / gpt-5.6-luna ·
claude-opus-5 / claude-haiku-4-5-20251001 · gemini-3.1-pro-preview / gemini-3.1-flash-lite ·
kimi-k3 / kimi-k2.6 · qwen3.7-max-2026-06-08 / qwen3.7-plus-2026-05-26; judges (Together.ai)
Mistral-Small-24B-2501, GLM-4.7, Llama-3.3-70B-Turbo; designer kimi-k3 (T=0); fallback
deepseek-v4-pro/flash. Full details: plan §4.2, `config/model_registry.json`,
frozen prices `config/price_vector.json` (D21–D24).

**30 main problems, domain-stratified (6 business domains × 5, `domain_map.json`)** + 10
post-cutoff robustness cases. **Consistency slice**: the special-arm family runs 5 reps
(instead of 3) in its four cheap cells so the Consistency DV (within-cell SD) has a
reliable estimate. Mixed-effects factorial analysis with problem and family as random effects;
primary DV = Novelty (3 judges × 3 prompt variants, families disjoint from generators);
economic DV = team-level Efficiency Gain Ratio (T-EGR); key hypotheses include H6
(persona-scale substitution: Tier × Persona interaction).

## Reproduction

All code that produced any artifact in this repo is committed in `code/` and `analysis/`
(seed 42, pinned `requirements.txt`, config-driven — see `code/README.md`). Full re-run:

1. Import pipeline JSONs from `pipelines/fixed/` into DeeWaanAI (or any OpenAI-compatible orchestrator).
2. Use `config/experiment_config.json` for exact model versions, temperatures, and maxTokens.
3. `python code/make_ledger.py` regenerates the identical run list (seed 42); `python code/run_experiment.py` executes it (idempotent, resumable).
4. `python code/judge_solutions.py` then `python code/aggregate_scores.py` reproduce `evaluation/`.
5. `python analysis/stats.py` reproduces all tables/figures from `evaluation/scores_aggregated.csv`.
