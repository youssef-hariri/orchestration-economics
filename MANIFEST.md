# Experiment Manifest (append-only provenance log)

Every phase appends an entry here. Never edit past entries.

---

## Entry 0 — Repository scaffold created
- Date: 2026-07-30
- Phase: pre-Phase-0 (setup)
- Actions:
  - Repository structure created per RESEARCH-PAPER-PLAN.md §8.
  - `data/problems/business_problems_15.json` committed — verbatim from LLM-Creativity repo (DOI 10.5281/zenodo.17407392); 15 problems validated as parseable JSON.
  - `data/personas/cultural_personas.json` committed — verbatim persona texts from persona-model-fit repo (DOI 10.5281/zenodo.19533619); congruent role mapping annotated (Culture_5→builder, Culture_Expert→critic, Culture_11→refiner). Note: source file had a trailing-comma JSON defect; corrected here without altering persona text.
  - `evaluation/judge_prompts/judge_variations.jsonl` committed — verbatim 3 judge prompt variants from persona-model-fit.
  - `config/experiment_config.json` created in DRAFT state (model versions/prices TO_PIN).
- Pending decisions: Western frontier model (A1/A6); Eastern designer model (A7); judge model pinning; 10 fresh business cases; 2 human raters.
- Cost incurred: $0 (no LLM calls yet).

---

## Entry 1 — Design revision: multicultural frontier pool, Kimi V3 designer, fresh cases drafted
- Date: 2026-07-30
- Phase: pre-Phase-0 (design)
- Decisions (by author):
  - A1 baseline changed from single Western frontier to **multicultural frontier pool**: GPT + Claude + Gemini (Western) + Kimi V3 + Qwen 3.7 (Eastern), 2 reps each (150 obs pooled); enables exploratory East-vs-West frontier-origin analysis.
  - A6 cost-matched baseline selected by **pre-registered rule**: frontier with highest mean Novelty in A1.
  - A7 designer pinned to **Kimi V3** (Moonshot; exact version string TO_PIN at Phase 0).
  - Judge families re-selected for disjointness after Gemini moved to generator pool: **Mistral Small, GLM (Zhipu), Llama-3.3-70B** (generator families: OpenAI, Anthropic, Google, Moonshot, Alibaba, DeepSeek).
- Actions:
  - `data/problems/fresh_business_cases_10.json` committed — 10 author-reviewed post-cutoff 2026 cross-cultural business cases (contamination control), drafted 2026-07-30, validated as parseable JSON. PENDING author review/edit before preregistration freeze.
  - `config/experiment_config.json` updated (frontier_pool_multicultural, frontier_cost_matched_A6 selection rule, designer = Kimi V3, judges swapped).
  - RESEARCH-PAPER-PLAN.md §4.1/§4.2/§4.4/§4.7 updated; budget re-estimated at **≈ $18–30**.
- Pending decisions: pin exact model version strings + prices (Phase 0, after API keys added); author review of the 10 fresh cases; 2 human raters.
- Cost incurred: $0 (no LLM calls yet).

---

## Entry 2 — Design revision: 2×2×2 within-family factorial; frontier-team arms added
- Date: 2026-07-30
- Phase: pre-Phase-0 (design)
- Decisions (by author + assistant):
  - Design restructured as **2×2×2 factorial**: Tier (Frontier vs Cheap sibling) × Structure (Solo vs Team) × Persona (None vs Loaded), crossed within 5 model families; every frontier now has a **cheap sibling from its own family** (GPT-mini, Haiku, Flash, small-kimi, qwen-turbo) — tier is manipulated within family (author request: run pipelines with cheap variations of each frontier).
  - Teams made **model-homogeneous** (all 3 agents same model; personas vary) — removes model-mixing confound; old A2/A3/A4 become C-S-P/C-T-N/C-T-P run across 5 families.
  - **Frontier-team cells added** (author question answered YES): F-T-N (orchestration benchmark at frontier) and F-T-P (persona value at frontier), restricted to 2 families (best Western by F-S-N Novelty + Kimi V3, pre-registered rule) × 2 reps for cost control.
  - New **H6 (persona-scale substitution)**: persona gain larger at cheap than frontier tier (Tier × Persona interaction) — requires the frontier persona cells.
  - DeepSeek dropped from generation (no sibling pair needed); retained as fallback family. Judge families unchanged (Mistral, GLM/Zhipu, Llama/Meta — still disjoint).
  - Reps: cheap cells 3 × 5 families (225 obs/cell); frontier solo 2 × 5; frontier team 2 × 2; A5/A6/A7 = 5 reps, A8 = 3 reps on one pre-registered cheap family.
- Actions:
  - `config/experiment_config.json` updated (design block, family sibling pairs, cell grid, reps).
  - RESEARCH-PAPER-PLAN.md §3 (H6), §4.1/§4.2/§4.4/§4.5/§4.6/§4.7 updated; budget re-estimated at **≈ $30–55** with pre-registered cost levers.
  - README.md design summary updated to factorial layout.
- Pending decisions: unchanged from Entry 1 + choice of the single cheap family for special arms A5–A8 (frozen at Phase 0 pilot).
- Cost incurred: $0 (no LLM calls yet).

---

## Entry 3 — Stochasticity/judging protocol, execution resilience, inherited stats stack
- Date: 2026-07-30
- Phase: pre-Phase-0 (design; grounded in full read of the 4 prior papers + `stats_with_anlysis.py`)
- Sources read in full: Papers DOI 10.5281/zenodo.17407392 (LLM-Creativity), 19533619 (Doing More with Less), 17425216 (ATIS), 17490945 (Team Composition Paradox); `code/stats_with_anlysis.py` (890 lines) from github.com/youssef-hariri/persona-model-fit. Local text archives in `.paper-research/`.
- Decisions (by author + assistant):
  - **Stochasticity protocol (author question answered):** sample randomness, don't suppress it — generation temp 0.7 (Paper 4's temp-0 suppression listed there as a limitation). **Every repetition is judged independently; responses are NEVER merged/ensembled before judging.** The ensemble exists only at the SCORE level (mean of 9 judge scores per solution) — same protocol as Papers 1 & 2. Two analysis units: solution-level ensemble score (descriptives) + judge-level mixed model (inference). Within-cell SD across reps becomes the **Consistency** secondary DV.
  - Reps stay at 3 (cheap) / 2 (frontier) × 5 families — power comes from 15 problems × families × reps under the mixed model, not 5 reps of one config.
  - **Judge prompts frozen at preregistration** — Paper 1 documents two prompt-"optimization" attempts that collapsed κ to ≈0; never redesign judge prompts mid-study.
  - **Pseudo-replication fix (methods contribution):** Paper 2 treated each of 9 judge rows as independent (n≈25,300); here inference uses mixed models with solution + judge random effects. Dual IRR reported (Fleiss κ + ICC(2,k), full sample).
  - **Inherited stats stack** (from `stats_with_anlysis.py`): Welch t, Cohen's d + 5,000-resample bootstrap CI (seed 42), FDR-BH, Type II ANOVA + partial η² + Shapiro/Levene, post-hoc power, IsolationForest (contamination 0.1) outlier sensitivity, 80/20 problem-split validation, LOO (judge & family), mean-vs-median sensitivity, EGR→T-EGR. Upgrade: Rouder BF approximation replaced by exact JZS BF (pingouin).
  - **Oracle-portfolio analysis added** (from Paper 4's +42.9% union result): per-problem best cell = attainable ceiling; A7-vs-oracle gap = routing value captured by the adaptive designer.
  - **Execution resilience (author requirement):** preregistered `runs/ledger.csv` (seed-42 randomized interleaving); statuses PENDING/RUNNING/DONE/FAILED_RETRYABLE/FAILED_PERMANENT; idempotent resume after credit outage/disconnect; 3 retries with 5/30/120 s backoff; ≤4 concurrent runs; `parsed_ok` gate so failed generations are re-run, never scored (fixes Paper 4's silent budget burn — its resume ledger had no retry and errors consumed budget).
  - **Pilot confirmed first** (author): 4 problems, ~$2, before any main-run spend; budget re-estimated from measured pilot tokens.
- Actions:
  - RESEARCH-PAPER-PLAN.md updated: §4.6 (+Consistency DV), §4.7 (inherited stack, pseudo-replication fix, oracle-portfolio, dual IRR), new §4.8 (stochasticity & judging protocol), new §4.9 (execution resilience).
  - `config/experiment_config.json` updated (judging block extended; new `analysis` and `execution_resilience` blocks); JSON validated.
  - DATA-DICTIONARY.md: `runs/ledger.csv` schema added.
- Pending decisions: unchanged from Entry 2 (model/version pinning + prices at Phase 0; author review of 10 fresh cases; 2 human raters; special-arm cheap family).
- Cost incurred: $0 (no LLM calls yet).

---

## Entry 4 — Domain-stratified 30-problem set; reps fixed at 3 + 5-rep consistency slice; first GitHub push
- Date: 2026-07-30
- Phase: pre-Phase-0 (design)
- Decisions (by author + assistant):
  - Author clarification: the problems are **culture-agnostic general business problems**; cultural personas are the treatment. Generalization therefore requires stimulus sampling across business domains (Westfall, Kenny & Judd 2014: ≥30 problem-level clusters).
  - **Main problem set expanded 15 → 30**: 6 pre-registered business domains × 5 problems (`domain_map.json`). Original 15 tagged by domain (tags PENDING author confirmation); 15 new author-drafted problems (Business_Problem_16–30) balance the grid. H2 upgraded from exploratory to **confirmatory** (Structure × Domain; divergent-leaning vs convergent-leaning planned contrast).
  - **Reps stay at 3** on all cheap cells (author requirement; statistically justified — rep count past 3 adds ~2–4% power at +67% cost). **Consistency slice**: the special-arm family runs **5 reps** in its four cheap cells (+240 runs) so the Consistency DV gets a reliable within-cell SD (SD sampling error ≈52% at n=3 vs ≈38% at n=5); Consistency confirmatory only there.
  - Special arms A5–A8 stay on the **original 15 problems** (mechanism arms need validated instruments, not domain breadth). Fresh-10 unchanged as out-of-sample robustness set.
  - Run matrix: factorial 2,640 + special 270 + slice 240 = 3,150 main runs (+90 fresh-10); ~3,240 solutions; ~29,200 judge calls; budget re-estimated **≈ $50–100** with 4 pre-registered cost levers (new lever: domain grid 6×5 → 6×4).
- Actions:
  - `data/problems/business_problems_domain_15.json` committed (15 new problems, JSON validated) — PENDING author review before preregistration freeze.
  - `data/problems/domain_map.json` committed (6×5 grid over 30 problems).
  - RESEARCH-PAPER-PLAN.md §3(H2)/§4.1/§4.3/§4.4/§4.6/§4.7/§4.8 updated; config cells/problems/analysis blocks updated; README + DATA-DICTIONARY updated; plan snapshot copied into this repo.
  - Repository initialized as standalone git repo and pushed to GitHub (author account) — see repo remote for URL.
- Pending decisions: author review of Business_Problem_16–30 and of original-15 domain tags; plus all items from Entry 2.
- Cost incurred: $0 (no LLM calls yet).

---

## Entry 5 — Design Decisions Register created (author requirement)
- Date: 2026-07-30
- Phase: pre-Phase-0 (documentation)
- Decision (by author): every design/statistical decision must be documented with its rationale grounded in academic literature and statistical methodology; these documents are source material for the paper's Methodology section.
- Actions:
  - `DESIGN-DECISIONS.md` committed — topic-organized register D1–D19 (factorial design, model-homogeneous teams, stochasticity sampling, independent judging, reps=3 + consistency slice, 30-problem domain stratification, mixed models/pseudo-replication fix, judge ensemble + frozen prompts, dual IRR, estimation-first stats, robustness battery, contamination control, cost-matching/T-EGR, preregistration, resilience ledger, persona congruence, oracle portfolio), each with Decision/Rationale/Academic grounding/Implementation pointers.
  - Maintenance rule added: all future decisions appended to BOTH `DESIGN-DECISIONS.md` (topical) and `MANIFEST.md` (chronological) with grounding at decision time.
  - README repository-layout table updated.
- Cost incurred: $0 (no LLM calls yet).

---

## Entry 6 — Code availability / computational reproducibility rule (author requirement)
- Date: 2026-07-30
- Phase: pre-Phase-0 (documentation)
- Decision (by author): all code we create and run must be saved so the experiment can be reproduced by anyone else.
- Actions:
  - `code/` directory created with `code/README.md` — inventory of every planned script (make_ledger.py, run_experiment.py, judge_solutions.py, aggregate_scores.py, analysis/stats.py, requirements.txt) and the reproducibility conventions (seed 42, config-driven, idempotent, env-var secrets, documented headers). Each script is committed BEFORE its outputs are trusted.
  - Decision recorded as D20 in `DESIGN-DECISIONS.md` with academic grounding (Peng 2011; Sandve et al. 2013; Stodden et al. 2016; TOP guidelines, Nosek et al. 2015).
  - README Reproduction section rewritten to a full code-driven re-run sequence; repository-layout table adds `code/`.
- Cost incurred: $0 (no LLM calls yet).

---

## Entry 7 — Phase 0 (partial): Eastern-family model pins, judges, discount windows
- Date: 2026-07-30
- Phase: Phase 0 (model pinning)
- Author inputs: API keys provided for Moonshot (Kimi), Alibaba (DashScope intl), DeepSeek, Together.ai via git-ignored `.env`; author directive to exploit provider off-peak discount windows.
- Actions:
  - All 4 keys validated live (HTTP 200 on /models). Endpoints fixed: Kimi = api.moonshot.ai (intl), Alibaba = dashscope-intl (Singapore), DeepSeek = api.deepseek.com, Together = api.together.xyz.
  - `config/model_registry.json` created: kimi-k3 / kimi-k2.6; qwen3.7-max-2026-06-08 / qwen3.7-plus-2026-05-26 (dated snapshots); judges Mistral-Small-24B-2501, GLM-4.7, Llama-3.3-70B-Turbo (all on Together, family-disjoint from generators); designer A7 = kimi-k3 T=0; fallback deepseek-v4-pro/flash. Prices pinned from official provider pricing pages same day.
  - Discount windows recorded: Qwen off-peak 22:00–08:00 UTC+8 (up to 80% off Max, 60% Plus, unverified on billing); DeepSeek 2x peak surge 09:00–12:00 & 14:00–18:00 UTC+8 (press-reported); Kimi & Together flat. Execution window fixed at 14:00–00:00 UTC (D21: pinned prices primary, paid prices sensitivity-only).
  - `code/pin_models.py` written and run: ALL PINNED MODELS VERIFIED (gpt/claude/gemini SKIP pending keys).
  - Decisions D21 (discount-window cost accounting) and D22 (model pins) appended to DESIGN-DECISIONS.md.
- Pending: OpenAI/Anthropic/Gemini keys → pin Western families; verify Qwen off-peak & DeepSeek surge on billing console during pilot; sync experiment_config.json TO_PIN fields at freeze.
- Cost incurred: $0 (free /models listings only).
---

## Entry 8 — Phase 0 complete: Western-family pins, token-invariant cost accounting, price vector
- Date: 2026-07-30
- Phase: Phase 0 (model pinning — COMPLETE)
- Author inputs: OpenAI, Anthropic, Gemini API keys added to git-ignored `.env`; author directive "as prices change all the time, we could instead measure the cost per token instead of per dollar".
- Actions:
  - All 3 Western keys validated live (HTTP 200 on /models). `.env` now holds 7 verified keys.
  - Western pins added to `config/model_registry.json` (status → COMPLETE): gpt-5.6-sol $5/$30 + gpt-5.6-luna $1/$6 (explicit Sol>Terra>Luna size ladder); claude-opus-5 $5/$25 + claude-haiku-4-5-20251001 $1/$5 (claude-fable-5 "Mythos-class" excluded as above-mainline; Sonnet 5 rejected — mid-tier with intro pricing expiring 2026-09-01); gemini-3.1-pro-preview $2/$12 + gemini-3.1-flash-lite $0.25/$1.50 (preview risk flagged, preregistered fallback gemini-2.5-pro).
  - D23 (token-invariant cost): ledger stores tokens as the observed quantity (API usage fields, required non-null before DONE); dollars are never stored, always recomputed as tokens x `config/price_vector.json` (created, v2026-07-30, 15 models, frozen for primary analysis; replicators swap the file to re-derive all economics). Robustness: alternative price vectors + price-free token-efficiency (Novelty per 1K output tokens, cross-family tokenizer caveat noted). Grounding: Diewert 1976 quantity–price decomposition; Sandve 2013 Rule 6; Steegen 2016 multiverse.
  - D24 (Western pins, mainline-flagship definition, price-ratio heterogeneity 3.4x–8x absorbed by family random effect) appended to DESIGN-DECISIONS.md.
  - `code/pin_models.py` extended for Anthropic (x-api-key + anthropic-version) and Gemini (x-goog-api-key, models/ prefix) conventions; run: 16/16 PASS — ALL PINNED MODELS VERIFIED.
  - `config/experiment_config.json` synced → version 0.2-phase0-pinned: families/judges/designer concretized, new cost_accounting block (price vector reference, required ledger token columns, execution window 14:00–00:00 UTC).
- Pending: verify Qwen off-peak & DeepSeek surge rates on billing console during pilot; author review of Business_Problem_16–30; coding-team Research Mode completion notice.
- Cost incurred: $0 (free /models listings only).


---

## Entry 9 — Phase 0: 30 fixed confirmatory pipelines created on production DeeWaanAI
- Date: 2026-07-30
- Phase: Phase 0 (setup, §6 step 3)
- Actions:
  - `code/create_pipelines.mjs` committed — deterministic generator; builds all 30 fixed confirmatory pipelines (5 families × {C-S-N, C-S-P, C-T-N, C-T-P, F-S-N, F-S-P}) from `config/experiment_config.json` + `data/personas/cultural_personas.json` and creates them via MCP `create_pipeline`. Idempotent (skips existing `oe-*` names).
  - All 30 created on production (project ids 13–42); full definitions + ids archived in `pipelines/fixed/fixed_pipelines_registry.json` (record of truth).
  - Bindings per pipeline: `defaultProviderId` (family provider), `defaultModel` + per-step `model` (pinned string), temp 0.7, maxTokens 2048. Role prompts = DeeWaanAI canonical Builder/Critic/Refiner verbatim; persona cells prepend verbatim persona text (congruent mapping); solo-N uses a fixed neutral task-only prompt (in generator, frozen at prereg).
  - Deferred by design (reasons in generator header): F-T-N/F-T-P (family pair fixed after F-S-N Novelty), A5/A8 (special-arm family frozen at pilot), A6 (budget from C-T-P median), A7 (designed at run time).
- Blocker found during smoke test: production DB missing migration 019 (`swarm_batches` + `swarm_runs.batch_id`) — deployed code writes `batch_id` on every run insert, so ALL production pipeline runs fail until 019 is applied. Idempotent runner `scripts/run-migration-019.mjs` written (platform repo) and verified locally (applied + re-run skip). Smoke test (§6 step 4) pending migration.
- Cost incurred: $0 (the one smoke-test run failed at DB insert, before any LLM call).
