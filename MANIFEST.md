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

---

## Entry 10 — Author decisions: problem set approved (D25), no human validation panel (D26)
- Date: 2026-07-30
- Phase: Phase 0 (pre-registration preparation)
- Decisions (by author):
  - **D25**: Business_Problem_16–30 approved as drafted → the 30-problem main set is content-final (freezes at prereg tag). Original-15 domain tags remain the only problem item pending.
  - **D26**: NO human raters — Phase 3 (blind human panel, 2 raters, human–AI correlation) removed. Substitute validity strategy: verbatim Papers 1–2 judge instrument, Fleiss' κ + ICC(2,k) on all solutions, leave-one-judge-out, judge-family disjointness, verbatim blinding instruction; stated explicitly as a limitation with human validation as future work. Grounding: *Judge's Verdict* (arXiv:2510.09738); Badshah 2025.
- Actions: DESIGN-DECISIONS.md (D25, D26), RESEARCH-PAPER-PLAN.md (§2 Stream F, §4.3, §4.6, §5 items 4/7, §6 Phase 3 + checklist), config/experiment_config.json (judging.human_validation, problems) all updated consistently.
- Cost incurred: $0.

---

## Entry 11 — Migration 019 applied; two provider API blockers diagnosed and resolved; D27 temp=1
- Date: 2026-07-31
- Phase: Phase 0 (setup, §6 step 4 — smoke test)
- Migration: coding team applied `scripts/run-migration-019.mjs` on production — run inserts work again.
- Blockers found via smoke tests (real errors captured from the run event stream; `run_status` only reports a generic failure):
  1. **OpenAI gpt-5.6 rejects `max_tokens`** (400: use `max_completion_tokens`). Platform bug — fixed in adapter `api/lib/providers/openai.ts` (retry once with `max_completion_tokens` on that exact 400), commit `3b4169f`, deployed. L3 security review: 0 findings.
  2. **Temperature 0.7 rejected by 2 of 5 families** (hard API policy, no workaround): Moonshot kimi-k3/k2.6 ("only 1 is allowed") and OpenAI gpt-5.6 ("Only the default (1) value is supported"). claude/gemini/qwen accepted 0.7. Verified empirically: gpt-5.6-luna at temp=1 completed (runId 21, 37 tokens).
- **D27 (author decision, 2026-07-31)**: generation temperature set to **1 uniformly across ALL 30 pipelines / 5 families** (author chose uniformity over per-family heterogeneity or dropping families; full rationale + alternatives in DESIGN-DECISIONS.md D27). Documented deviation from pre-registered 0.7; must be reported in the paper's Method section with the API errors as evidence of external forcing.
- Actions: `code/apply_d27_temp1.mjs` (idempotent) updated all 30 production pipelines (projects 13–42) → temp "1"; registry patched (write-through + `d27` block); config `generation.temperature`=1 (+note); DESIGN-DECISIONS.md (D27, D3 amendment note); RESEARCH-PAPER-PLAN.md §4.8(1).
- Cost incurred: ~a few hundred tokens (diagnostic smoke runs 8–21, mostly failed at 0 tokens; successes: runs 14/15/16/18/21, all ≤ 361 tokens).

---

## Entry 12 — Phase 0 smoke test PASSED 30/30; D28 max_tokens 8192; token/cost chain verified
- Date: 2026-07-31
- Phase: Phase 0 (setup, §6 step 4 — COMPLETE)
- Smoke test (`code/smoke_test.mjs`, 1 non-experimental problem per pipeline, sequential): **30/30 completed** (runs 22–51), all 5 families × 6 cells. Log: `runs/logs/smoke_test_2026-07-31.json`. Total ~88.9k tokens.
- Token/cost chain verified (§6 step 5): every run has the expected step count (1 solo / 3 team), every step has tokensUsed > 0 and latencyMs > 0, step sums equal run totals — `agentRuns.tokensUsed` ledger is sound for cost computation (plan §4.4, Table 2).
- Artifact found: the 2 kimi TEAM cells completed but with EMPTY final response (runs 42/43). Isolated experimentally: kimi's hidden reasoning counts against the completion budget (kimi-k2.6 solo at maxTokens=100 → empty, run 52; same prompt at 8192 → 8,532 chars, run 53).
- **D28 (author decision, 2026-07-31)**: `max_tokens` 2048 → **8192 uniformly across all 30 pipelines** (cap unobservable to models; uniform → no family confound; reasoning tokens are genuine measured cost; full rationale + alternatives in DESIGN-DECISIONS.md D28). Applied via `code/apply_d28_maxtokens.mjs`; registry patched (`d28` block); config + plan §4.4 updated. Documented deviation, reported alongside D27.
- D28 verification: kimi team cells re-run — oe-kimi-C-T-N run 54 (6,523 tokens, 1,327-char final) and oe-kimi-C-T-P run 55 (11,178 tokens, 3,845-char final), both non-empty. Recheck appended to the smoke log.
- Housekeeping: diagnostic scratch project 43 renamed to `zz-scratch-retired (was oe-smoke-tmp)` (MCP has no delete tool; safe to delete from UI).
- **Phase 0 §6 steps 3–5 are now COMPLETE**: 30 fixed pipelines live, smoke-tested, token ledger verified.
- Cost incurred: ~110k tokens total this session (smoke 88.9k + diagnostics + D28 recheck ~21k), spread across 5 providers' cheap+frontier models.

---

## Entry 13 — D29–D31: Polisher exclusion made explicit; A7 refined (persona-free + variance probe + conditional A7-P); pre-registered sequential gate protocol
- Date: 2026-07-31
- Phase: Phase 0 (pre-freeze design consolidation, prompted by author design review)
- **D29**: Polisher role formally excluded from team cells — Builder→Critic→Refiner is the minimal orchestration loop; Polisher affects presentation, not substance (LLM-judge style-bias risk); makes D1's "3-step" explicit.
- **D30**: A7 refinements — (1) A7 executes WITHOUT personas (isolates Design lever; exploratory 2×2 = C-T-N / C-T-P / A7 / A7-P); (2) bounded design-variance probe (5 problems × 3 temp-1 designs × 1 execution → design ICC); (3) A7-P conditional arm: designer also staffs roles from the frozen persona pool only; (4) single designer (Kimi V3) reaffirmed. All designer/probe/staffing tokens charged to arm cost.
- **D31**: sequential gate protocol frozen BEFORE any pilot token: gate table G0/G-A5/G-A6/G-A7/G-A7P/G-A8 with thresholds; SESOI d = 0.30 on Novelty; gates are futility/feasibility only (never evidence); confirmatory factorial runs in full regardless; H4/H5 pre-declared as conditional; every executed arm reported (no file-drawer).
- Files: DESIGN-DECISIONS.md (D29–D31), RESEARCH-PAPER-PLAN.md §4.1 (A7 amended, A7-P row, gate principle), config/experiment_config.json (`exploratory_gates` block).
- Cost incurred: 0 tokens (documentation only).

---

## Entry 14 — D32 pilot protocol frozen; pilot generation launched (G0 measurement)
- Date: 2026-07-31
- Phase: Phase 0 → pilot (§6 step 6)
- **D32 frozen before any pilot run**: matrix (30 pipelines × 4 problems × 1 rep = 120 runs, inside D21 window), deterministic problem draw (seed 20260731 → Business_Problem_4 [product_innovation], 8 [operations_supply_chain], 16 [strategy_market_entry], 19 [marketing_communications]; frozen in `config/pilot_problems.json`), problem rendering rule (background + blank line + problem, verbatim, no wrapper), G0 measurement procedures, and the special-arm family selection rule (100% completion → cheapest team run → lowest team latency).
- Pilot generation scheduled: detached process waits until 14:00 UTC (D21 execution window), then runs `code/pilot_run.mjs` (sequential, resumable, full final responses logged to `runs/logs/pilot_gen_2026-07-31.json`).
- Judging harness built (`code/judge.py`): 3 pinned Together judges × 3 verbatim D10 prompt variants = 9 scores/solution; blinded (problem+solution only, shuffled seed 20260731); resumable JSONL. Awaiting TOGETHER_API_KEY.
- G0 gate report builder (`code/pilot_g0_report.py`): empty-output rates per cell, Fleiss κ (median-across-variants per judge, 3 raters) + ICC(2,k) on Novelty, cost projection vs §4.4 envelope (upper-bound pricing: total tokens × output price), D32.5 family selection. Stats functions sanity-checked (perfect-agreement κ=1.0, identical-rater ICC=1.0).
- Cost incurred so far: 0 experiment tokens (setup only; generation starts 14:00 UTC).

---

## Entry 15 — D33: judge panel replaced (forced infrastructure deviation), frozen before first judging call
- Date: 2026-07-31
- Phase: Phase 0 → pilot (§6 step 6), before any judging token
- **Trigger**: pilot-day access checks — `mistralai/Mistral-Small-24B-Instruct-2501` and `zai-org/GLM-4.7` are dedicated-endpoint-only (400 "Unable to access non-serverless model") on the author's Together account; key itself valid (Llama-3.3-70B → 200). No mistralai model serverless at all.
- **D33 (author choice via structured options)**: uniform NON-REASONING panel — `deepseek-chat` (=DeepSeek-V4-Flash, DeepSeek API, $0.14/$0.28, non-thinking), `zai-org/GLM-5.2` (Together, thinking disabled via `chat_template_kwargs.enable_thinking=false`, $1.40/$4.40), `meta-llama/Llama-3.3-70B-Instruct-Turbo` (unchanged, $1.04/$1.04). All three probe-verified 2026-07-31 (0 reasoning tokens, correct "Dimension: score" format). Judge families {deepseek, zhipu, meta} stay disjoint from all 5 generator families; deepseek fallback-generator overlap caveat logged (fallback never invoked).
- Author explicitly rejected a mixed panel (1 reasoning + 2 non-reasoning) on capacity-fairness grounds; the all-reasoning alternative was rejected for ~4× cost, unauditable hidden reasoning, and an unvalidated family (Inkling).
- Superseded pins archived in `model_registry.json.judges_superseded_2026_07_31`.
- Files: config/model_registry.json, config/experiment_config.json (judging.judges), code/judge.py (per-judge endpoints/keys/extra_params, resolved-model logging), DESIGN-DECISIONS.md (D33), RESEARCH-PAPER-PLAN.md §4.2.
- Cost incurred: ~15 probe calls of ≤512 tokens (< $0.01), logged as infrastructure verification, not experiment data.

---

## Entry 16 — D34: concurrent-by-default policy; judge.py parallelized; c=100 ramp calibration frozen
- Date: 2026-07-31 (pilot generation in progress, ~33/120 at time of writing)
- Phase: Phase 0 → pilot
- **Author instruction**: time has value — latency-insensitive operations run concurrently by default; after the pilot, test max concurrency with ceiling c=100.
- **D34 frozen**: (1) judge.py parallelized NOW (24 workers = 8/judge lane, lock-serialized JSONL, resumable; ~1080 calls drop from ~1.5h to ~minutes) — scores are latency-insensitive so no measurement is touched; (2) concurrency ramp c=10/25/50/100 after G0, reusing pilot (pipeline, problem) pairs so the sequential pilot is the exact pairwise c=1 baseline; decision rule: highest c with 0% throttle-attributable failures AND ≤10% median latency inflation → main-run concurrency; fallback per-family c=5; (3) main-run writer isolation: one file per run, temp+atomic-rename, ledger by post-hoc merge; concurrency level recorded per run as execution-regime constant.
- The D32 pilot itself stays sequential as pre-registered (protocol integrity + it doubles as the ramp c=1 baseline).
- Files: DESIGN-DECISIONS.md (D34), code/judge.py (concurrent rewrite).
- Cost incurred: 0 experiment tokens (documentation + code only).

---

## Entry 17 — Pilot qualitative diagnostics → Amendment A1 drafted; main-run readiness completed (no experiment executed)
- Date: 2026-07-30
- Phase: post-pilot / pre-main-run (awaiting discount window, author instruction: no judging or generation until the window opens)
- **Author request**: qualitative analysis of pilot answers to explain pilot observations; then draft the amendment + re-registration and prepare everything for launch.
- **Diagnostics (results/QUALITATIVE-NOTES.md)**: (F1) run_status caps finalResponse at 16,000 chars — 130/371 pilot runs capped, judges scored truncated text; the interim-1 inverted interaction vanishes on non-truncated runs (d=−0.013, p=0.90) and lives entirely in truncated ones (d=−0.277, p=0.008); full texts recoverable from granular archive (111/130 longer). (F2) judge max_tokens=512 too small — 442 null dimension scores, 356 deepseek-chat, 334 Cultural Sensitivity never emitted. (F3) persona effect is dimension-dependent: Novelty +0.13, Cultural Sensitivity +0.08, Elaboration −0.49, Usefulness −0.53 (construct-rubric tension, not failure). (F4) length–quality correlation family-dependent (overall +0.51).
- **Amendment A1 drafted** (DeeWaanAI-Next/protocols/05-AMENDMENT-A1-PILOT-ARTIFACT-CORRECTIONS.md): A1.1 full-text judging; A1.2 judge max_tokens 2048 + completeness gate; A1.3 audit fields; A1.4 length robustness covariate; A1.5 optional pilot re-judge (author-gated). OSF delta: preregistration/amendment_A1_osf_delta.md. Decisions: DESIGN-DECISIONS D35–D38.
- **Readiness implemented (zero generation/judging credits)**: code/capture_fulltext.py (built runs/fulltext/pilot_fulltext.json 371 runs + pilot_repair_capped.json 130 runs); code/judge_v2.py (compile-checked, not executed); code/main_run.mjs (D34 writer isolation, seed-42 interleaving, full-text capture; dry-run validated: 1,900 runs = 19 problems × 40 pipelines × reps 3/2); code/create_ft_remaining.mjs → 6 F-T pipelines created on production (projects 49–54; gpt-5.6-sol, gemini-3.1-pro-preview, qwen3.7-max-2026-06-08); registry now 40 pipelines (full 8×5 factorial).
- **Interim-1 decision (CONTINUE) unchanged**; frozen design unchanged; pending author sign-off + OSF delta application before launch (LAUNCH-CHECKLIST.md).
- Cost incurred: 0 experiment tokens; 6 pipeline records created (infrastructure, free).

---

## Entry 18 — Amendment A1.5 executed: full pilot re-judge with judge_v2/A1 + analysis
- Date: 2026-08-04 (discount window open per author instruction 2026-07-30 message; author directive: re-judge → analyse → STOP before main run, await confirmation)
- Phase: post-pilot / pre-main-run
- **Scope decision (agent, documented)**: re-judged ALL 371 pilot runs (not only the 130 capped) — the max_tokens fix (A1.2) affects every run's null scores, and a single consistent instrument is academically cleaner than a v1/v2 mixed table; v1 judgment files untouched (hard rule 2).
- **Execution**: `code/judge_v2.py --store runs/fulltext/pilot_fulltext.json --out runs/logs/pilot_v2_judgments.jsonl` → 3,339 calls (371×3 judges×3 variants), ~20 min at 24 workers; 5 transient zhipu timeouts recovered via resume; 2 persistent incompletes (run 997, Llama var2/var3 — format non-compliance at temp 0 across 6 attempts), audited `incomplete: true` per A1.2. Final: 3,337 complete judgments, **0 null dimension scores** (v1: 442/16,695).
- **Analysis** (`code/analyze_pilot_v2.py` → `results/pilot_v2_analysis.json`, report `results/PILOT-V2-ANALYSIS.md`):
  - v1↔v2 run-level agreement r=0.92; shift +0.03 (+0.05 on capped runs) — correction, not re-measurement.
  - Balanced claude+kimi interaction (the estimable one): v1 −0.162 (p=0.016) → v2 −0.117 (p=0.031); on capped-with-recovered-fulltext runs (n=48) the reversal disappears (+0.059, p=0.43); residual concentrates in genuine model-ceiling runs (stimulus inherently capped) + a fragile non-capped signal. Length-adjusted b −0.117→−0.108.
  - Persona P−N signature replicated sharper under v2: Novelty +0.239, CS +0.068, Flexibility −0.053, Elaboration −0.448, Usefulness −0.576.
  - A1.4 confirmed on true lengths: length–quality r by family claude −0.269 … gemini +0.687.
  - Provider alias audit: deepseek-chat resolves to deepseek-v4-flash in BOTH v1 and v2 (instrument consistent).
- **Interim-1 CONTINUE stands and is strengthened**; main run (1,900 generations + 17,100 judgments) remains FROZEN awaiting explicit author confirmation — per author instruction, nothing launched beyond the judging re-run.
- Files: runs/logs/pilot_v2_judgments.jsonl, runs/logs/pilot_v2_judge_console.log, code/analyze_pilot_v2.py, results/pilot_v2_analysis.json, results/PILOT-V2-ANALYSIS.md.
- Cost incurred: $12.59 judging (zhipu $7.46 / meta $4.44 / deepseek $0.70); 0 generation tokens.

---

## Entry 19 — Main run LAUNCHED (interim-2); kimi family re-routed to Together mid-launch (deviation, documented)
- Date: 2026-08-04, first launch 18:49 UTC (D21 window open; author go-ahead with credits confirmed)
- Phase: main run generation (1,900 runs, c=100, seed-42 interleaving, D34 per-run files)
- **Author sign-offs recorded** (Amendment A1 §7): A1.1–A1.4 approved ("ok as long as it is based on academic data" — condition satisfied, evidence base cited), A1.5 executed, OSF delta author-confirmed (link pending).
- **Incident 1 — Moonshot credits exhausted (again).** First launch: ALL kimi runs failed instantly (tok=0). Root cause from run_status: "API credit exhausted: Moonshot Kimi: Account balance insufficient." Only F-T kimi had been on Together (disclosed pilot migration); C-S/C-T/F-S kimi still used native Moonshot (provider 12). Author had stated kimi uses Together.ai credits.
- **Deviation (routing-only, model identity preserved):** Together catalog verified 2026-08-04 to host BOTH pinned versions (moonshotai/Kimi-K2.6, moonshotai/Kimi-K3). `code/switch_kimi_all_to_together.mjs` migrated the 6 remaining kimi pipelines (projects 31–36) to provider 18, mirroring the disclosed pilot F-T migration; registry updated (routedVia: together.ai). Smoke test passed (run 1266, 20s, completed). No model, prompt, persona, or design element changed — hosting endpoint only. Paper obligation: disclose alongside the pilot F-T migration.
- **Incident 2 — resume-set bug found & fixed.** Failed runs were written to runs/raw/main and would have been skipped on resume. Fixed twice: (a) done-set counts only status=completed; (b) also requires non-empty text, after run 1268 (kimi/Together edge case) reported completed with tokens=10,492 but EMPTY archived content — such runs are now retried. Process restarted to apply (resume lost nothing).
- **Status at entry time:** running (pid 17432), ~50+ completed, 0 failures post-migration. TRUNC@SOURCE audit flag firing on long responses (~40% of early completions) — expected: full text IS captured via export_run (e.g. run 1323: len=33,032 recovered); flag exists for audit per A1.3.
- Cost incurred so far: generation in progress (tokens per run logged); judging not started.

### Entry 19 — update: first generation pass finished 00:xx UTC; PAUSED on triple credit exhaustion (author-anticipated)
- First pass outcome (ledger 1,900 records): completedNonEmpty 1,045 (+2 reattached later = 1,047); failed 747; timeout 104; TRUNC@SOURCE 153 (all recovered via export_run where applicable).
- Root causes (verified via run_status.error on samples): Anthropic "credit balance too low" (claude, 286 failed), OpenAI "rate limit exceeded or insufficient credits" (gpt, 344), Together "402 credit limit exceeded" (kimi, 117). Qwen completed 380/380. Gemini never failed on credit — 104 polls timed out at our 20-min cap while still running server-side; `code/reattach_timeout_runs.mjs` re-queries and reattaches: 2 recovered, ~90 still completing on the platform (re-run later), 12 failed.
- Remaining per family: claude 287, gpt 344, kimi 120, gemini ~12–102 (mostly server-side in flight), qwen 0 → ~760–850 new generations needed after recharge.
- Resume plan (author rule: "pause and resume later"): recharge Anthropic + OpenAI + Together → next D21 window (14:00 UTC) → `node code/main_run.mjs` (resume skips completed-non-empty, retries everything else) → re-run reattach script → verify 0 remaining → fulltext store → judge_v2.
- Caffeinate released (nothing running locally; gemini completions are server-side).

### Entry 20 — Pass 2 (kimi+claude resume) halted by platform DB outage (2026-08-05 ~02:45 UTC)
- Author instructions 2026-08-05: run recharged families only (kimi, claude); defer gpt (no credit); judging waits for discount window. Added `--families` filter to main_run.mjs (reusable partial-resume capability).
- Pass 2a (kimi+claude parallel, 2×c=100) → platform DB write failures ("Failed query: insert/update agent_runs") on BOTH families; claude pass killed, reverted to single-pass regime (c=100 total — the calibrated D34 level; 200 concurrent exceeds validated load).
- Pass 2b (kimi only) → 68 new completions; 52 marked failed — error evidence shows the LLM calls SUCCEEDED (e.g. run 3414-class: status=completed params in the failed UPDATE) and only DB persistence failed; these are candidate-recoverable via run_status/export_run once DB recovers.
- Zero-load probe (runId 3600) ALSO fails the same INSERT → outage is platform-side and ongoing: reads OK, all writes failing. Most likely MySQL read-only mode (disk full) or DB service crash on Railway. Author action required (Railway dashboard → MySQL: disk usage/logs/restart).
- Claude recharge still UNVERIFIED (no clean claude completion; all failures were DB errors, not credit errors — a good sign).
- Next: DB recovery → zero-load probe → claude pass → kimi sweep → gemini reattach → fulltext store → judging in discount window.

### Entry 21 — DeepSeek peak-valley pricing announcement (author-shared 2026-08-05)
- Announcement: DeepSeek API will adopt peak-valley pricing; peak hours 01:00–04:00 UTC and 06:00–10:00 UTC (09:00–12:00, 14:00–18:00 UTC+8) at 2× regular price, all billing items; effective date pending official notice. As of 2026-08-05 prices remain flat.
- Impact on plan: the author's earlier "wait for judging discount window" instruction is superseded — there is no off-peak discount, only a future peak surcharge. Judging will launch immediately once generation completes rather than waiting.
- Consistency: frozen execution window 14:00–00:00 UTC (D21) already fully avoids both future peak slots; D21 rationale holds unchanged.
- Cost accounting: if judging crosses peak hours after the effective date, DeepSeek judge costs (~1/3 of the panel) double for those calls — recorded in the paid-price sensitivity analysis (D21/D23); primary analysis unaffected (pinned standard prices).

### Entry 22 — OSF registration created (2026-08-06)
- Discovery: no OSF registration existed for this study (author believed one had been created programmatically; in fact the pre-registration existed only as repo documents, and the A1 "delta applied" confirmation had no OSF artifact — corrected here for the record).
- Action: author created OSF account (email-verified) + personal access token; registration built via OSF API v2 (`code/osf_register.py`).
- Registration: https://osf.io/mjb8x (Open-Ended Registration, submitted 2026-08-06 02:33 UTC, pending OSF moderation); project node https://osf.io/8pwej.
- Contents: 7 archived files — 00-COVER-AND-TIMING-DISCLOSURE.md + protocols 01–04 + Amendments A1/A2; narrative summary in the registration form.
- Honesty note: the cover document discloses that the OSF timestamp post-dates main-run generation start (2026-08-04) and A1 approval (2026-07-30); it records the true ordering of events (protocols frozen before pilot; A1 before first main-run call; A2 before interim-2 data lock). No hypothesis, design, cell, sample-plan, or stopping-rule element was altered by any amendment.
- Amendment A2 §6 updated with the registration link; the interim-2 analysis gate is now satisfied.

## Entry 23 — Interim-2 COMPLETE: data locked, A2 analysis executed, H1 boundary crossed (2026-08-06)

- Generation: all 1,900/1,900 runs completed non-empty (5 families × 380: claude/gemini/gpt/kimi/qwen). gpt family recovered via passes 8–10 (380 → 380; last 7 failed at step-3 transient provider errors, resolved on retry).
- Fulltext store rebuilt (`capture_fulltext.py --tag main`): 1,900 entries; 83 runs at the 16,012-char source cap (TRUNC@SOURCE flag preserved).
- Judging campaign v2/A1 complete: 17,091/17,100 cells (99.95%) with complete 5-dimension scores across 3 judges × 3 verbatim variants.
- Audited exclusions (9 cells, 0.05%): null-score INCOMPLETE records persisting across ≥4 retries on old-batch runs (runIds 3622, 3659, 3663, 3667, 3714, 3751, 3753, 3846, 4267) — systematic, not transient; affected runs retain ≥7/9 judgments. All transient zhipu read-timeouts resolved on retry (0 error-final cells).
- DATA LOCK (SHA-256): fulltext store `afeacbab26520381c883a2c3d245795ff49357c09dee745e0f1ae26a059a566e`; judgments `23c289a5797e53e43fb68e5c17ecd2994c3b718f9baf244dd031ba42ad51c4d1`. No further writes permitted.
- Analysis: `analyze_main.py` (A2.1–A2.7 + primary layer) executed on locked data → `results/interim2_analysis.json`; decision document `results/INTERIM2-DECISION.md`.
- Primary result: H1 tier × structure interaction d = −0.227 (pre-registered direction: team structure helps cheap_sibling more), Welch t = −2.447, p = 0.0145, bootstrap 95% CI [−0.410, −0.040]; |z| = 2.447 > OBF interim-2 boundary 1.977 → boundary crossed, H1 supported. JZS BF₁₀ ≈ 1 (inconclusive; reported per A2.4, not decision-gating).
- Robustness: LOFO sign-stable (5/5 folds, max |Δd| 0.084); LOPO all 19 folds negative; length confound none (A1.4 p = 0.63); inter-judge r 0.49–0.87.
- Notable secondary finding: H4 persona effect REVERSED (P−N d = −0.691, N scores higher) — flagged for final-report discussion; H5 not supported; tier×structure×persona 3-way F = 6.68, p = 0.0098.
- Per protocol 03 Rule 4: interim 2 is final; no further data collection. A2 §4 integrity clause honored (A2 outputs did not alter sequential stopping logic).
- Next: protocol 02 qualitative analysis, protocol 04 cost-effectiveness, final paper write-up.

## Entry 24 — Amendment A3 executed: exploratory advanced statistics on locked data (2026-08-06)

- Amendment A3 drafted and author-approved same day ("ok proceed with all of them"): protocols/07-AMENDMENT-A3-EXPLORATORY-ADVANCED-STATISTICS.md. Explicitly exploratory/post-lock; changes no hypothesis or stopping rule; A2 §4 integrity clause extended to A3.
- Implementation: code/analyze_exploratory.py → results/exploratory_analysis.json (read-only on locked files).
- A3.1 LMM (run-level, groups problem|family; primary vc_formula failed with KeyError, fallback documented in JSON): run-level tier×structure two-way coef ≈ 0 (p=0.97); three-way tier×structure×persona coef −0.151, p=0.00035 → interaction concentrated in persona-loaded conditions.
- A3.2 TOST (persona=N, SESOI ±0.20): d=−0.008, p_TOST=0.063 → equivalence NOT established; absence of the interaction without personas remains unproven (honestly reported).
- A3.3 Empirical-Bayes partial pooling (pymc unavailable; EB estimator disclosed as substitute): shrunk d kimi −0.365, claude −0.305, qwen −0.255, gemini −0.230, gpt −0.198.
- A3.4 Random-effects meta-analysis across 5 families: pooled d=−0.270 [−0.472, −0.069], p=0.008, τ²=0.015, I²=28.5% → interaction generalizes across families with low-moderate heterogeneity.
- A3.5 Persona dimension decomposition (BH-FDR): Novelty +0.154 (P helps); Usefulness −1.024 and Elaboration −0.966 drive the reversed persona main effect; Cultural Sensitivity n.s.
- INTERIM2-DECISION.md extended with §6 summarizing A3; §2/§5 decisions unchanged.
- Next: qualitative analysis per protocol 02.

## Entry 25 — Amendment A4 launched: inductive qualitative analysis, Wave 1 open coding (2026-08-07)

- Author-approved 2026-08-07 ("ok proceed with all of them"). Protocol: protocols/08-AMENDMENT-A4-INDUCTIVE-QUALITATIVE.md. EXPLORATORY; cannot alter interim-2 decision (A2 sec 4 clause extended to A3/A4).
- Design: explanatory sequential mixed-methods; grounded-theory-style open coding (Braun & Clarke 2006; Charmaz 2006); trustworthiness per Lincoln & Guba 1985. Protocol 02 deductive codebook demoted to secondary verification pass (A4.5).
- Provider check: deepseek/zhipu/meta all responding (no recharge needed).
- RQs: (1) why persona cheap teams beat some frontier singles; (2) what winning outputs do differently; (3) why the effect is family-contingent (kimi/claude vs gpt/gemini); (4) why personas raise Novelty but cut Usefulness/Elaboration.
- Wave 1 purposive sample (30 runs, deterministic): code/qual_a4_sample.py -> runs/qual/sample_wave1.json. W1a top-composite CTP 2/family; W1b top-composite FSN 2/family; W1c gpt+gemini CTP nearest family median (5+5). Composite kept for audit only; coders blinded (no cell/family/score in prompt).
- Coding harness: code/qual_a4_code.py — open coding prompt with NO pre-set themes, codes + verbatim quotes, reasoning_style/structure_notes/notable; coders deepseek-v4-flash + GLM-5.2 (temperature 0, max_tokens 4096), 60 calls concurrent, resumable JSONL runs/logs/qual_codes_wave1.jsonl.
- Next: axial synthesis with Llama-3.3-70B adjudicator -> results/QUALITATIVE-A4.md; saturation check; Wave 2 if needed (RQ4 contrast).

## Entry 26 — Amendment A4 completed: two-wave inductive qualitative analysis (2026-08-07)

- Wave 1 open coding: 30 runs x 2 blinded coders (deepseek-v4-flash, GLM-5.2, temp 0) = 60/60 complete -> runs/logs/qual_codes_wave1.jsonl. 944 unique codes (lexical Jaccard 0.021 — disclosed floor, semantic convergence handled at synthesis).
- Synthesis v1 (adjudicator Llama-3.3-70B): 944 codes -> 10 content themes — assessed as problem-domain content, not discriminative; discourse-level residual codes carried the signal.
- Synthesis v2: 4 process/style themes (Structured Reasoning, Exploratory Approach, Cultural Sensitivity, Collaborative Tone); adjudicator flagged insufficient pair material -> triggered Wave 2.
- Wave 2 (protocol A4 sec 3 saturation loop): 20 runs purposive — W2a matched frontier baselines (same problem+family as each W1a winner, 10), W2b RQ4 twin pairs CTP high Novelty-Usefulness gap vs same-problem CTN (5 pairs; 4 kimi, 1 qwen). 40/40 codings complete -> runs/logs/qual_codes_wave2.jsonl.
- Final pair-matched synthesis: RQ1/RQ2 high confidence (winners use exploratory/abductive reasoning, cultural contextualization, collaborative tone, metaphors, rhetorical questions); RQ3 medium (kimi/claude winners = global-local balance + decentralized governance framing; gpt/gemini non-responders = mechanistic charters/centralized truth/decision logging); RQ4 high (persona -> speculative/metaphorical language raises novelty, ambiguity cuts usefulness/elaboration; converges with pilot QUALITATIVE-NOTES).
- Saturation: adjudicator returned stop_sampling=false but its 3 "new" themes duplicate Wave-1 themes; analyst stopped at Wave 2 on redundancy grounds (documented in report sec 5). Wave 3 remains feasible at low cost.
- Report: results/QUALITATIVE-A4.md; machine output: results/qual_themes.json (all synthesis generations retained).
- Pre-submission hardening recommended: closed re-coding pass for Cohen's kappa; A4.5 deductive verification pass (protocol 02 six themes).
- Next: protocol 04 cost-effectiveness analysis; final paper write-up.

## Entry 27 — A4.6 closed re-coding pass: Cohen's kappa computed (2026-08-07)

- Author-approved same turn ("yes do it now"). Codebook: 12 analyst-frozen items grounded in Wave 1-2 observations (process-theme subdimensions + key discourse codes), embedded in code/qual_a4_closed.py.
- 50 transcripts x 2 blinded coders (deepseek-v4-flash, GLM-5.2, temp 0), 100 calls concurrent. 99/100 complete; run 3887/deepseek unparseable after 6 attempts (long claude winner transcript; audited out, 1/100 = 1%).
- Result: POOLED Cohen's kappa = 0.774 (percent agreement 89.8%) on 49 paired transcripts / 588 binary decisions — above the 0.70 threshold set by protocol 02.
- Per-item kappa >= 0.70 (7/12): reflective opening 1.000, cultural contextualization 1.000, inductive/exploratory 0.935, staged implementation 0.787, authority citation 0.767, deductive framework 0.766, risk quantification 0.741.
- Per-item kappa < 0.70 (5/12, disclosed): global-local balance 0.656, conditional logic 0.624, rhetorical questions 0.595, metaphor 0.492, collaborative framing 0.470 — subjective style codes; claims relying on them downgraded to moderate-reliability evidence (Krippendorff caution zone).
- Artifacts: runs/logs/qual_closed_wave12.jsonl, results/qual_kappa.json; QUALITATIVE-A4.md sec 1.2 added.
- Sample-size basis (author question): the 50-transcript corpus was pragmatic + saturation-driven, NOT power-analyzed; protocol 02's original target was 176. Literature support: Guest et al. 2020 (base themes saturate at ~9-17 interviews), Fugard & Potts 2015 (quantitative saturation tool). 50 x 12 = 600 decisions give a narrow kappa CI; extension to 176 remains low-cost if reviewers require.
- Next: protocol 04 cost-effectiveness analysis; final paper write-up.

## Entry 28 — Methodology decision D39: abductive iterative loop registered (2026-07-30)

- Author ideation turn converged on the program's research cycle: deductive confirmatory test (H1-H3, 1,900 runs) -> abductive explanation (A3 exploratory stats + A4 inductive qualitative) -> intervention design (end-of-pipeline refinement stage) -> new deductive test (refinement experiment as Study 2, own pre-registration).
- D39 freezes the refinement-stage design constraints: one universal refiner prompt (controlled variable), add-only rule (never delete original ideas/stance), failures handled by new arms not prompt edits; sample-size plan: pilot 50/family, then n ~ 8/d^2, target 100-150 paired problems x 3-5 families with Holm correction.
- Grounding logged in DESIGN-DECISIONS.md: Creswell & Plano Clark 2018 (explanatory sequential mixed methods), Dubois & Gadde 2002 (systematic combining), Peirce 1903 / Lipton 2004 (abduction), Hevner et al. 2004 (design science), Kerr 1998 (HARKing).
- Boundary rule: refinement experiment cannot count as part of H1-H3 (anti-HARKing); must be labeled Study 2 with its own OSF pre-registration before main run.
- Next: Protocol 09 (refinement experiment pre-registration) when author approves; then protocol 04 cost-effectiveness analysis and paper write-up.

## Entry 29 — Study 2 pilot executed: refiner mechanism confirmed, superiority gate not passed (2026-07-30)

- Author approved "proceed with this new refiner experiment". Protocol 09 pre-registered first (D39/D40 territory: hypotheses H2.1-H2.3, frozen universal add-only refiner prompt, seed 20260730, gates G1/G2, locked analysis).
- Efficiency: no regeneration — reused locked Study-1 fulltexts/judgments; only the 60 refinement calls (deepseek-chat, temp 0) and 540 judgments (frozen D10 panel) were new. All concurrent per standing order.
- G1 feasibility PASS: 60/60 refinement completions (100%), 540/540 judgments, 0 failures. Length ratio refined/original = 1.69 (logged; D37 sensitivity available).
- H2.1 primary (refined vs FSN, Holm): kimi d=+0.080 CI[-0.105,0.147] n.s.; claude d=-0.903; qwen d=-0.642. G2 gate FAILS -> full run NOT triggered (rule applied mechanically, no post-hoc threshold change).
- Baseline audit: same-sample original CTP vs FSN ran negative (kimi -0.078, claude -0.154, qwen -0.424 composite; d=-0.26/-1.07/-2.19) — random n=20 realized baseline unfavorable; refinement closed each gap by exactly its own gain (kimi flipped positive).
- H2.2 novelty protection PASS all families (+0.039/+0.042/+0.156). H2.3 repair: kimi Usefulness +0.233 (FDR 0.002), composite +0.102 (d=1.53); qwen Usefulness +0.539 / Elaboration +0.506 / composite +0.284 (d=1.48); claude saturated (already 30-35k chars), n.s.
- Artifacts: results/refine_study2_pilot.json, results/REFINE-STUDY2-PILOT.md, runs/refine/*, runs/logs/refine_pilot.jsonl + refine_judgments_pilot.jsonl, code/refine_study2_{sample,run,analyze}.py.
- Next (author decision, must be pre-registered): extend pilot to stabilize baseline; or condition claims; or close paper with Study 1 + pilot as mechanism demonstration.

## Entry 30 — Study 2 extension to full pool: superiority rejected at full n, mechanism confirmed (2026-07-30)

- Author chose "extend to 50-100/family, most scientific". Protocol 09 sec 8 amendment registered BEFORE execution: locked pool fact measured first (universe = exactly 57 C-T-P-with-F-S-N-mate per family), extension = remaining 37/family, seed 20260731, disjoint from pilot 20, pooled analysis, pilot data reused untouched, zero threshold changes.
- Execution: 111 new refinements (deepseek-chat, temp 0) 111/111; 999 new judgments on frozen D10 panel; re-run recovered 7 zhipu timeouts; 4 INCOMPLETE disclosed (R3622x3, R3873x1 — 37-38k-char refined texts pushed judge rationales past frozen max_tokens=2048; affected runs keep 6-8 valid judgments; frozen harness not patched).
- Pooled H2.1 (n=57/family): kimi d=-0.295 CI[-0.137,-0.008]; claude d=-1.301 CI[-0.248,-0.164]; qwen d=-0.809 CI[-0.223,-0.113] — all significantly WORSE than F-S-N.
- Baseline audit at full n CORRECTS the pilot hypothesis: original CTP vs FSN is systematically negative (kimi -0.184 d=-0.71; claude -0.222 d=-1.42; qwen -0.471 d=-2.17, all CIs exclude 0). The CTP-vs-FSN deficit is a population effect, consistent with Study 1's Usefulness penalty.
- Gap recovery by refinement: kimi 60%, claude 8% (saturated), qwen 64% of the baseline gap.
- H2.2 novelty protection PASS pooled (kimi +0.043, claude +0.021, qwen +0.177). H2.3 repair pooled: kimi Usefulness +0.275/Elaboration +0.111 (FDR 0.000); qwen +0.520/+0.464 (FDR 0.000); claude n.s.
- G2 FAILS again, mechanically; pool is EXHAUSTED — no further extension possible. Superiority claim REJECTED for this intervention; mechanism claim CONFIRMED. Report shape: Study 2 = registered mechanism demonstration with a negative superiority result (claim discipline, anti-HARKing maintained end to end).
- Artifacts: results/refine_study2_pooled.json, REFINE-STUDY2-PILOT.md sec 6, runs/refine/sample_extension.json + refined_store_extension.json, runs/logs/refine_extension.jsonl + refine_judgments_extension.jsonl, code/refine_study2_sample_ext.py; harness scripts parameterized (--samples/--judgments/--refine-logs/--phase/--out).
- Next (author decision): close Study 2 for the paper; remaining pipeline = protocol 04 cost-effectiveness analysis, final paper write-up; OSF moderation still pending for the main registration.

## Entry 31 — Cross-family secondary analysis: no wins, two ties with weakest frontier (2026-07-30)

- Author asked (intermediate question): are all comparisons same-family? could some cheap+design+persona family beat ANOTHER family's frontier? Approved running it.
- Protocol 09 sec 9 amendment registered BEFORE computation: full 6-direction matrix, deterministic minimal-runId F-S-N mate, descriptive-only status (family quality confounded with design — no causal claim), Holm in part A, no gates attached. Zero new API calls — pure recomputation over locked Study-1 + Study-2 judgments.
- (A) original CTP vs cross-family FSN (n=57/direction): all six directions NEGATIVE (kimi->claude d=-1.46 ... qwen->claude d=-2.84). The CTP answer loses to every frontier, not just its own.
- (B) refined CTP vs cross-family FSN: two effective TIES with the weakest frontier — refined kimi->qwen +0.019 (d=+0.10, CI includes 0) and refined claude->qwen -0.007 (CI includes 0); all other directions negative. Frontier ordering implied: claude > kimi > qwen.
- Conclusion: author hypothesis rejected in strong form; refinement lifts each family to parity with the weakest frontier only. Reinforces Entry 30: mechanism works, superiority not demonstrated under ANY pairing scheme.
- Artifacts: results/cross_family.json, code/cross_family.py, REFINE-STUDY2-PILOT.md sec 7.
- Next unchanged: author decision on closing Study 2; then protocol 04 cost-effectiveness + paper write-up.

## Entry 32 — Study 2 qualitative analysis: orchestration buys coverage, the frontier wins on density (2026-07-30)

- Author approved qualitative follow-up to grasp the full picture behind the quantitative results. Protocol 10 pre-registered BEFORE execution: 3 RQs (frontier residual edge; style convergence vs length inflation; claude saturation), 30 triples (10/family, seed 20260801), A4.6-style machinery (inductive wave -> frozen codebook -> blinded closed coding by 2 coders -> kappa gate 0.70), analysis plan locked before Wave 2.
- P0 free check: length ratio vs composite change strongly POSITIVE (pooled Pearson r=+0.675, Spearman rho=+0.707; kimi +0.56, qwen +0.47, claude n.s.). Length is a prime driver of refinement gains; dilution hypothesis rejected.
- Wave 1: 36/36 inductive feature lists (6 wave-1 triples x 3 texts x 2 coders). Analyst froze a 13-code codebook (results/qual2_codebook.json) before Wave 2.
- Wave 2: 180/180 closed coding calls. Pooled kappa=0.824 (93.1% agreement) gate PASSED; 6 of 13 codes below 0.70 (base-rate artifact, agreement 82-98%), conclusions on them downgraded to medium reliability per protocol.
- RQ1: only one kappa-reliable residual frontier edge >= 0.30: concise_maxims (qwen frontier 1.00 vs refined 0.55). redundancy_bloat (medium reliability): frontier 0.00 all families vs refined 0.65-0.95. Refined answers match or EXCEED the frontier on all structural codes.
- RQ2: all 6 codes that changed orig->refined (kimi, qwen) are structural scaffolding codes; no insight code moved. Convergence metric net: kimi toward 4/away 6, qwen 5/4, claude 0/2.
- RQ3: claude original answers already at codebook ceiling (>=0.90 on 11/13 codes); ZERO codes changed -> saturation mechanistically confirmed.
- Mechanism summary: refinement adds structure and length (coverage) but cannot manufacture density (compressed maxims, zero boilerplate); the frontier's remaining edge is exactly that density. Explains the Entry 30/31 ceiling (parity, never superiority).
- Artifacts: protocols/10-PROTOCOL-STUDY2-QUAL.md, results/QUALITATIVE-STUDY2.md, results/qual2_analysis.json + qual2_kappa.json + qual2_codebook.json, runs/logs/qual2_wave1.jsonl + qual2_closed.jsonl, runs/qual2/triples.json, code/qual_study2_prep.py + qual_study2_wave1.py + qual_study2_closed.py + qual_study2_analyze.py.
- Next unchanged: author decision on closing Study 2; then protocol 04 cost-effectiveness + paper write-up.

## Entry 33 — Protocol 04 cost-effectiveness frontier: persona cells dominated, refinement is the cheapest climb (2026-07-30)

- Author approved executing Protocol 04. Amendment A registered BEFORE computation: ledger data reality (tokensUsed totals only, no input/output split -> blended price at locked phi=0.5 primary, sensitivity phi in {0.25,0.75}, plus price-free token ordering); family->model mapping from frozen model_registry; judge cost excluded; Study-2 extension (refined C-T-P cost = original run + refine call with real prompt/completion splits, deepseek-chat pricing); robustness claim rule (frontier membership must be stable across all phi).
- n = 1,900 completed runs priced via frozen price_vector v2026-07-30 (D23). Cell costs (phi=0.5): C-S-P $0.0145/4.210, C-S-N $0.0194/4.507, C-T-P $0.0715/4.327, C-T-N $0.0734/4.531, F-S-P $0.0670/4.406, F-S-N $0.0835/4.586, F-T-N $0.2952/4.610, F-T-P $0.3044/4.370.
- Pareto frontier IDENTICAL at all phi: {C-S-P, C-S-N, C-T-N, F-S-N, F-T-N}; dominated at all phi: {C-T-P, F-S-P, F-T-P}. All persona cells dominated by their no-persona twins (economic echo of the Study-1 persona penalty).
- T-EGR (D15, within-family vs F-S-N): C-S-P 8.60, C-S-N 6.15, C-T-P 1.58, C-T-N 1.49, F-S-P 1.36, F-T-N 0.27, F-T-P 0.27. ICER vs cheapest: C-S-N +$0.016/point (best buy), F-T-P +$1.81/point (worst).
- Study-2 extension: refine calls cost $0.001-0.003 each; refined kimi C-T-P = $0.0654 at quality 4.585 (absolute parity with pooled F-S-N 4.586 at 78% of cost); refined qwen C-T-P = $0.0166 at 4.398. Paired within-family comparisons remain negative (Entry 30) - absolute-mean parity only, disclosed.
- Verdict: structure substitutes for tier only at the cheap end (C-S-N = 98% of F-S-N quality at 23% of cost); frontier teams buy almost nothing (F-T-N +0.024 quality at 3.5x cost); refinement is the cheapest known move toward the frontier but never a paired win.
- Artifacts: results/COST-EFFECTIVENESS.md, results/cost/ (cost_per_run.csv 1900 rows, cell_summary.csv, pareto_frontier.csv, cost_effectiveness.json, scatter png+pdf), code/cost_effectiveness.py, Protocol 04 Amendment A.
- Next: author decision on paper write-up (all analyses now complete: Study 1 main + amendments, Study 2 quantitative/qualitative/cross-family, economics).

## Entry 34 — Paper structure design v1 with DOI-verified literature register (2026-08-07)

- Author approved the paper-writing phase, step 1: structure design (sections, subsections, paragraph points). Standing rule from author: literature review restricted to real references with verified DOIs.
- Artifact: PAPER-STRUCTURE.md (v1). Sections: 1 Introduction (orchestration bet, gap, contributions), 2 Related Work (5 theme clusters), 3 Pre-registered Design and Apparatus (factorial, stimuli, generation, blinded panel, token-invariant costing, statistical plan), 4 Study 1 (main effects, persona penalty, practicality penalty, robustness battery), 5 Study 2 (quantitative refinement, qualitative coverage-vs-density, economic integration), 6 Discussion (contingency model, density mechanism, methodological lessons, limitations, conclusion), 7 Figures/tables plan, 8 Supplementary.
- DOI verification pass (2026-08-07, publisher/indexer pages): 14 references verified with resolvable DOIs (R1-R15 minus two re-verify flags); 3 strings flagged for pre-submit re-check (Cohen 1988 book, Albers & Lakens 2018, Diewert 1976); 9 candidate references parked in PENDING-VERIFY and excluded from the draft until their DOIs are confirmed (LLM-Blender, Du debate, generative agents, CoT, foundation models, surveys, GPT-4 report). arXiv 10.48550/* DOIs used where no publisher DOI exists (Wang, Liang, Verga, Zheng, Tomlinson).
- Artifact-to-section mapping table included for write-up.
- Next: author review of PAPER-STRUCTURE.md; then drafting section-by-section with DOIs locked.

## Entry 35 — Paper structure v2: aligned to the author's published academic style (2026-08-07)

- Author instruction: follow the structure of an academic work (methodology section, then results), using the author's own papers as the template.
- Sources read: .paper-research/paperB.txt (Doing More with Less, DOI 10.5281/zenodo.19533619) and paperA.txt (LLM-Creativity, DOI 10.5281/zenodo.17407392). Extracted style signature: numbered sections 1 Introduction → 2 Literature Review → 3 Methodology → 4 Results → 5 Discussion → 6 Limitations → 7 Future Directions → 8 Conclusion; funnel introduction with numbered contributions + roadmap paragraph; List of Abbreviations; Literature Review as themed streams + integration paragraph; Methodology split 3.1 Design / 3.2 Models / 3.3 Personas / 3.4 Generation / 3.5 Evaluation Framework (judge selection, rubric, IRR) / 3.6 Statistical Analysis (effect sizes, inferential, economic, robustness) / 3.7 Validity / 3.8 Availability; each Results subsection ends with a Key Takeaway; Summary-of-Key-Findings table.
- PAPER-STRUCTURE.md rewritten to v2 in this style; own-paper DOIs added to the verified register (19533619, 17407392, 17490945); DOI verification rules from Entry 34 unchanged.
- Lineage anchors: T-EGR as heir of Paper 2's EGR; stimuli inherited from Paper 1 (17407392); contingency arc completed from Paper 4 (17490945).
- Next: author review of v2; then section-by-section drafting with DOIs locked.

## Entry 36 — Literature review drafted (Section 2), verified-DOI scope enforced (2026-08-07)

- Artifact: paper/02-LITERATURE-REVIEW.md (draft v1, ~1,400 words). Written strictly from the verified register: R1 Noy & Zhang 2023 (Science), R2 Brynjolfsson et al. 2023 (NBER), R3 Dell'Acqua et al. 2023 (SSRN), R4 Wang et al. 2023, R5 Liang et al. 2023, R6 Verga et al. 2024, R7 Zheng et al. 2023, R8 Nosek et al. 2018, R9 Steegen et al. 2016, R10 Sandve et al. 2013, R11 Albers & Lakens 2018, R12 Lakens 2013, R13 Cohen 1960, R14 Tomlinson et al. 2024, R15 Diewert 1976, plus the author's own Zenodo papers (17407392, 17490945, 19533619). Zero PENDING-VERIFY citations included.
- Structure follows PAPER-STRUCTURE.md v2 §2: 2.1 productivity effects (single-agent capability, jagged frontier → orchestration question), 2.2 multi-agent/ensemble (self-consistency, debate; cost-matching gap), 2.3 LLM-as-a-judge (biases → panel design), 2.4 open-science + economic measurement (preregistration, multiverse, reproducibility, pilot discipline, effect-size reporting, kappa, price-quantity decomposition, inference footprints), 2.5 integration: own-paper lineage (EGR → T-EGR) → precise gap → three pre-registered hypotheses (substitution, persona, refinement).
- Key claims kept verifiable: Noy & Zhang 444 professionals / 0.8 SD time / 0.4 SD quality / low-performer gains; Brynjolfsson 5,179 agents / +14% / +34% novices; Dell'Acqua 758 consultants / +12.2% tasks / +25.1% speed / +40% quality inside boundary, −19 pp outside; Wang majority-vote over sampled reasoning paths; Liang multi-round debate improves factuality/reasoning and divergent thinking; Verga PoLL better human correlation at lower cost, mitigates self-preference; Zheng position/verbosity/self-enhancement biases; Hariri 2026b 40–88% cost savings, contingency model.
- Self-check flags retained in the reference list: R11/R15 DOI strings and R14 journal DOI still marked for pre-submit re-verification.
- Next: author review of Section 2 draft; remaining sections drafted in order (3 Methodology next).

## Entry 37 — Full paper draft assembled: citation audit corrections integrated, literature review v3 inserted (2026-08-07)

- Sources: CITATION-AUDIT-REPORT.md (reviewer audit, 2026-08-07), 02-LITERATURE-REVIEW.md (v3 enhanced by reviewer).
- Citation audit applied: (1) Albers & Lakens DOI corrected 10.1016/j.jesp.2017.09.004 (was 06.013); (2) Liang et al. corrected to EMNLP 2024 (was EMNLP 2023), DOI 10.18653/v1/2024.emnlp-main.992; (3) Dell'Acqua author Lifshitz-Assaf corrected; (4) Tomlinson journal DOI 10.1038/s41598-024-54271-x (was arXiv pending); (5) Diewert title capitalization verified OK.
- New references added (R16-R19): Wei et al. 2022 CoT (NeurIPS), Yao et al. 2023 Tree of Thoughts (NeurIPS), Shinn et al. 2023 Reflexion (NeurIPS), Snell et al. 2024 test-time compute.
- Full paper assembled: paper/FULL-PAPER-DRAFT.md (996 lines). Sections: Title + Abstract (~250 words) + List of Abbreviations (24 entries) + 1 Introduction (funnel, 5 contributions, roadmap) + 2 Literature Review (v3 integrated verbatim, 4 themed streams + integration) + 3 Methodology (8 subsections) + 4 Results (8 subsections with Key Takeaways) + 5 Discussion (4 subsections) + 6 Limitations + 7 Future Directions + 8 Conclusion + References (21 entries, all DOI-verified).
- All audit corrections synced to both 02-LITERATURE-REVIEW.md and FULL-PAPER-DRAFT.md. Self-citations (Hariri 2025a/b, 2026b) kept in References per author preference; audit recommendation to consider moving to Related Work noted for author decision.
- Next: author review of full draft; figure/table generation; LaTeX conversion for target journal format.

## Entry 38 — Paper draft v2: audit, figures, AI disclosure (2026-08-08)

- Sources: FULL-PAPER-DRAFT.md (v1, 1007 lines), FIGURE-SELECTION-GUIDE.md (18 figures), Additional_figures_needed.md (audit).
- v2 file: paper/FULL-PAPER-DRAFT-v2.md (1065 lines). Changes from v1:
  1. Version bump and date to 2026-08-08.
  2. Figure 3 (cost-effectiveness scatter) inserted in §4.6 — was referenced in text but missing.
  3. Table 1 label added to cell summary table (§4.6).
  4. Table 2 label added to Summary of Key Findings (§4.8).
  5. Figure 10 (persona dimensions) inserted after §4.2 Key Takeaway.
  6. Figure 7 (cross-family matrix) inserted after §4.4 gap recovery.
  7. Figures 8 (LOO) and 9 (meta-analysis forest) inserted in §4.7.
  8. Inline text reference to Figure 7 added in §4.4 (cross-family paragraph).
  9. Inline text references to Figures 8 and 9 added in §4.7.
  10. Section 7: "Three experiments" corrected to "Four experiments" (lists 4 items).
  11. §3.9 AI-Assisted Research Disclosure added: documents use of Kimi (kimi-k3) and Qwen (qwen3.7-max) for ideation, code generation, audit, and execution under human supervision.
  12. Roadmap paragraph updated to reference §3.9.
- Additional_figures_needed.md created: 4 new figures requested (φ-sensitivity scatter, contingency flowchart, sequential boundary plot, persona radar), plus Fig 3 copy instruction and numbering crosswalk.
- Next: figure generation agent produces Figs 19–22; author review of v2; LaTeX conversion.

## Entry 39 — Business draft v4: heading audit, executive summary, managerial table (2026-08-10)

- Source: FULL-PAPER-DRAFT-BUSINESS-v3.md (1097 lines).
- v4 file: paper/FULL-PAPER-DRAFT-BUSINESS-v4.md (1164 lines). Changes from v3:
  1. **Duplicate abstract removed** — lines 10–12 had an empty `## Abstract` block followed by `---` then the real abstract; collapsed to single abstract.
  2. **Heading hierarchy normalized** — §3.1–3.3, §3.5–3.8 promoted from `###` to `##`; §3.2.x, §3.5.x, §3.6.x demoted from `####` to `###`; §4.1–4.8 promoted from `###` to `##`; §5.1–5.4 promoted from `###` to `##`. Consistent hierarchy: `#` chapters, `##` sections, `###` subsections.
  3. **Executive Summary for Practitioners added** after Abstract — 30-line blockquote with decision context, bottom line, three budget rules, and coverage-vs-density caveat.
  4. **Table 3 (Managerial Quick-Reference)** added in §5.1 — maps task profile → recommended cell → quality/cost/T-EGR → override condition.
  5. **§6 Limitations expanded** — fifth limitation on API-list vs. enterprise-negotiated pricing and pipeline latency not priced.
  6. **§8 Conclusion expanded** — two new paragraphs: build-versus-buy framework for AI capability; field-level contribution statement.
  7. Version bump to v4 (2026-08-10).
- Original v3 file preserved unchanged per versioning policy.
- Next: author review of v4; target-journal selection; LaTeX conversion.

## Entry 40 — LaTeX conversion of business draft v4 (2026-08-10)

- Source: FULL-PAPER-DRAFT-BUSINESS-v4.md (1165 lines).
- Output: paper/FULL-PAPER-DRAFT-BUSINESS-v4.tex (1420 lines).
- Conversion details:
  1. Document class: article, 12pt, A4.
  2. Packages: amsmath, graphicx, booktabs, longtable, tabularx, hyperref, natbib, cleveref, mdframed, siunitx, csquotes, caption, subcaption, enumitem, xcolor, float.
  3. Executive Summary rendered as mdframed box with gray background.
  4. List of Abbreviations as longtable with booktabs rules.
  5. All 22 figures as \includegraphics with \label/\caption.
  6. All 3 tables as LaTeX tabular/tabularx with booktabs rules.
  7. References as hand-formatted thebibliography with hyperlinked DOIs.
  8. Cross-references via cleveref (\cref) for sections, figures, tables.
  9. Custom commands: \phiBlend, \BF, \TEGR, \dval, \figref, \secref.
  10. All section labels added for cross-referencing.
- Original v4 .md file preserved unchanged.
- Next: pdflatex compilation test; target-journal template adaptation if needed.

## Entry 41 — Business draft v5: data-integrity correction, problem count fixed (2026-08-11)

- **Trigger:** Author review identified that v4 stated "38 business problems" but the actual experiment used 30 problems total (11 pilot + 19 confirmatory).
- **Deep data audit performed** (all verified against `code/analyze_main.py`, `runs/fulltext/main_fulltext.json`, `runs/logs/main_judgments.jsonl`, `results/interim2_analysis.json`):
  - Problem count: 19 confirmatory (30 total, 11 pilot excluded per D31 / Albers & Lakens 2018). Paper said 38 — **WRONG, FIXED → 19**.
  - Run count: 1,900 confirmed (19 × 40 pipelines × 2.5 avg reps). ✓
  - Data duplication: 0 duplicate runIds in `main_fulltext.json`; 5,313 overwritten judgment records (normal retries, last-write-wins). ✓
  - Pilot leakage: 0 pilot problems in main analysis. ✓
  - Score distribution: 1–5 Likert, mean 4.433, std 0.763, no anomalies. ✓
  - Effect sizes: d = −0.227 (H1), +0.294 (tier), −0.691 (persona) — all match `interim2_analysis.json`. ✓
  - Per-cell N: C-* 285 each (19×5×3), F-* 190 each (19×5×2). ✓
  - Leave-one-problem-out: 19 folds — confirms 19 problems in analysis. ✓
- **Files created:** `paper/FULL-PAPER-DRAFT-BUSINESS-v5.md`, `paper/FULL-PAPER-DRAFT-BUSINESS-v5.tex`.
- **Corrections applied (3 locations each file):**
  1. Abstract: "38 business-strategy problems" → "19 business-strategy problems"
  2. Executive Summary: "38 business problems" → "19 business problems"
  3. §1 Introduction: "38 domain-stratified business problems" → "19 confirmatory business problems (drawn from a 30-problem domain-stratified universe; 11 problems reserved for feasibility gating per the pre-registered protocol; Albers & Lakens, 2018)"
- **Version Errata Log added** at end of both v5 files (table of all versions + detailed v5 correction notes).
- **What was NOT changed:** All statistical results, effect sizes, tables, figures, and conclusions remain identical — the analysis was correctly computed on 19 problems throughout. The "38" was a writing error in v3 (propagated to v4), not a data error.
- Original v4 files preserved unchanged per versioning policy.
- **PAPER-STRUCTURE.md** still contains "38" in 4 locations (lines 27, 75, 130, 149) — flagged for next update.

**Update (2026-08-11, same session):** PAPER-STRUCTURE.md fixed — all 4 "38" problem-count references corrected to "19" (lines 27, 75, 130, 149). Line 149 now states "30 domain-stratified business problems; 11 pilot, 19 confirmatory." Also fixed "10 reps" → "reps 3/2" (line 75) to match actual replication structure. Only DOI/page-number "38" instances remain (Science 380, NBER 31161, etc.) — these are correct.

## Entry 42 — Business draft v6: stimulus-sampling limitation added (2026-08-11)

- **Trigger:** Author asked whether 19 problems is statistically sufficient. Academic assessment: 19 is below the 30–40 stimulus range recommended by Westfall, Kenny & Judd (2014) for maximal generalizability power, though internally valid (LOO 19-fold stability confirmed). This should be disclosed as a limitation.
- **Files created:** `paper/FULL-PAPER-DRAFT-BUSINESS-v6.md`, `paper/FULL-PAPER-DRAFT-BUSINESS-v6.tex`.
- **Change:** §6 Limitations — sixth limitation added on stimulus sampling breadth:
  - 19 problems below 30–40 ideal (Westfall, Kenny & Judd, 2014)
  - Mitigating evidence: LOO 19-fold sign stable (max |Δd| = 0.02), dense within-problem replication (100 runs/problem × 5 families)
  - External validity bounded; future work should replicate with larger, more diverse corpora
- **Version Errata Log** extended in both v6 files (v6 row added).
- Original v5 files preserved unchanged per versioning policy.

---

## Entry 43 — v7 Comprehensive Pre-Publication Revision (2026-08-16)

**Trigger:** Author pre-publication review identified 15 improvements needed before publishing online.

**Files created:**
- `paper/FULL-PAPER-DRAFT-BUSINESS-v7.md` (from v6)
- `paper/FULL-PAPER-DRAFT-BUSINESS-v7.tex` (from v6)

**Changes applied (15 fixes):**

| # | Fix | Section(s) |
|---|---|---|
| 1 | Problem count: "19" → "30" (total) in abstract/intro; "19" retained in results for confirmatory analysis | Abstract, §1, §3.1 |
| 2 | Keywords enhanced for discoverability (12 keywords) | Abstract |
| 3 | Executive summary moved from after abstract to Appendix A (Practitioner Summary) | Structure |
| 4 | "cheap"/"cheap-tier" → "lower-tier" throughout; C = lower-tier explained in abbreviations table | All sections |
| 5 | Section 2.5: added external persona references (Shanahan et al. 2023; Salewski et al. 2023) | §2.5 |
| 6 | DeepSeek pricing: corrected to "stable during experiment" (no peak-surge window in effect) | §3.4, §7 |
| 7 | Protocol 03, A2.4, Study 2 explained before first use | §3.6.2 |
| 8 | RQ1/RQ2/RQ3 explained before first use | §3.6.5 |
| 9 | Section 3.7 disclosed threats rephrased for clarity | §3.7 |
| 10 | "every script was inspected" → "all scripts audited by AI under author supervision" | §3.9 |
| 11 | Convergence metric (kimi toward 4 / away 6) rephrased in plain language | §4.5 |
| 12 | A2 battery explained before first use | §4.7 |
| 13 | Limitations: "Four" → "Six" (correct count) | §6 |
| 14 | Section 7: removed DeepSeek peak-surge window claim | §7 |
| 15 | Section 8: contribution claim made more modest | §8 |

**What was NOT changed:** All statistical results, effect sizes, tables, figures, and conclusions remain identical.

- **Version Errata Log** extended in both v7 files (v7 row + corrections table added).
- Original v6 files preserved unchanged per versioning policy.

---

## Entry 44 — Local ↔ OSF preregistration sync (2026-08-20)

**Trigger:** v8 pre-publication verification — confirming the robustness battery file (Amendment A2, referenced as "A2.4" in §3.6.2) is publicly registered on OSF.

**Verification (OSF API, authenticated via OSF_TOKEN):**
- Registration mjb8x osfstorage contains all 7 files (00-COVER through 06-AMENDMENT-A2).
- Confirms paper claims ("pre-registered", "A2.4", "protocol 03") are backed by public registration.

**Sync action:** downloaded files 01–06 from OSF into `preregistration/osf_submission/` (00-COVER was already present and byte-identical to OSF). Local folder now mirrors the OSF registration exactly (7 files).

---

## Entry 45 — Publication checklist: OSF visibility (2026-08-20)

**Status check (OSF API):** registration mjb8x is currently **not public** (embargoed/draft) and has no DOI yet.

**Author decision:** make the registration public when the paper is published.

**Publication-day checklist:**
1. Lift embargo / set registration mjb8x to public, so `osf.io/mjb8x` resolves for readers (paper header and §3.9 reference it).
2. Confirm the DOI is minted after publication, and cite it if the venue wants a DOI for the pre-registration.
3. Verify the robustness-battery pointer in the final draft: "Amendment A2, OSF registration osf.io/mjb8x" (file `06-AMENDMENT-A2-EXTENDED-INTERIM2-ANALYSIS.md`, items A2.1–A2.7).

---

## Entry 46 — Paper v9: pre-publication audit fixes (2026-08-20)

**Trigger:** deep audit of v8 surfaced 3 critical attribution/numbering issues + 14 broken-grammar items + several data-accuracy items. Author decisions: **A1 → Option A**, **A2 → Option A**; errata log intentionally absent from the published paper (author confirmation); executive summary moved to end of paper (author request).

**New files (v8 unchanged per versioning policy):**
- `paper/FULL-PAPER-DRAFT-BUSINESS-v9_with_figures/FULL-PAPER-DRAFT-BUSINESS-v9.tex` (LaTeX only; no MD companion by author decision)
- `paper/FULL-PAPER-DRAFT-BUSINESS-v9_with_figures/` 14 figures copied from v8 folder.

**Critical fixes (A1 — solo/team attribution, Option A):**
- New title: "Orchestrate or Upgrade? When a Lower-Tier Model Delivers 98% Quality at 23% Cost" (numbers now attributed to a single lower-tier model, i.e. C-S-N).
- Abstract, §4.1/§4.6 Strategic Implication boxes, §5.1 decision framework, Table 4 managerial rows, §8 conclusion, Appendix A exec summary: 98%/23%/T-EGR 6.15 attributed to the lower-tier solo call (C-S-N); the three-step team variant (C-T-N) reported separately as 98.8% quality at 88% cost (T-EGR 1.49). Avoid rows split: F-T-N (100.5%/353%) and F-T-P (95.3%/365%).

**Critical fixes (A2 — hypothesis renumbering, Option A):**
- Study 1 hypotheses aligned exactly with OSF Protocol 01: H1 = tier×structure interaction (primary), H2 = tier main effect, H3 = structure main effect, H4 = persona, H5 = structure×persona. Labels added in §4.1, Table 3 (now covers H1–H5), and §2.5 rewritten with explicit Protocol 01 mapping.
- Study 2 labeled Protocol 09 (G1/G2 gates, criteria H2.1–H2.3); §2.5 discloses that Protocol 09 was frozen in the decision log (D39–D40) before any refinement run and that the OSF registration covers Study 1 and its amendments.

**Critical fixes (A3 — exploratory labeling):**
- A3 analyses (empirical-Bayes, random-effects meta-analysis, persona dimension decomposition) labeled exploratory/post-data-lock in §3.6, §4.1 (A3.5), §4.7 (A3.4), with disclosure that they are registered in the decision log, not part of the OSF package.

**Data-accuracy fixes:**
- DeepSeek wording restored to v7-correct form (pricing stable; no peak-surge window in effect) in §3.3 and §7.
- Study 2 pool: "all 171 matched CTP–FSN pairs (57 per family), pilot 20/family + pre-registered extension 37/family" (was "171 pairs per family").
- Refinement dimension gains: d = 0.57 to 1.35 (was 0.8–1.4).
- §3.6 Robustness Checks rewritten as the actual A2.1–A2.7 battery (Type-II ANOVA A2.3: F = 6.90, p = 0.0087, partial η² = 0.0036; the non-existent "mean-vs-median" item removed); §4.7 reports the same.
- Unsupported "<0.04" LOO claim removed (replaced by "interaction keeps its sign").
- Westfall, Kenny, & Judd (2014) bibitem added (Kenny = D. A., verified via web search; JEP: General 143(5), 2020–2045, doi:10.1037/xge0000014).

**Grammar/mechanical fixes:** cheaperer×2, cheaperest×3, cheaperly, intro run-on sentences rewritten (19 confirmatory / 11 feasibility gating with Albers & Lakens 2018), stray quotes, truncated sentences, missing verbs, "Abers"→"Albers", footnote URL scheme, ICER "lowest-cost cell", §2.4 G1/G2 category error, §3.7 "rather than silently excluded", §3.9 AI disclosure.

**Structure:** Executive Summary moved to Appendix A after the conclusion; pointer sentence added after the abstract.

**Re-audit (full re-read of v9 + residual greps + brace/env/figure/citation checks):** found and fixed 5 minor polish items in place (title shortened to ≤15 words; abstract colon → sentence break with "Economically,"; abstract "60–64%" → "up to 64%" since claude gap recovery was 8%; Table 3 gained H3/H5 rows and "G2 FAIL"→"G2 rejected"; §3.6.2 contrast wording). All checks pass: 0 residual matches, braces balanced, 34/34 environments, all 14 figures present, all 23 bibitems cited. **No v10 needed.**

**Not changed:** all statistical results, effect sizes, cell tables, figures, and conclusions; v8 files preserved. Figure audit/regeneration remains the next step, pending author go-ahead.
---

## Entry 47 — Open item: v9 title pending author decision (2026-08-20)

**Issue:** author flagged that the current v9 title — "Orchestrate or Upgrade? When a Lower-Tier Model Delivers 98% Quality at 23% Cost" — misaligns: the question asks when to orchestrate vs. upgrade, but the subtitle answers with the solo-model finding.

**Status:** author will think and advise. Title in `FULL-PAPER-DRAFT-BUSINESS-v9.tex` unchanged for now. Four candidate directions discussed (direct-answer, mechanism-answer, "Mostly Neither", descriptive reframe). Resolve before publication.

---

## Entry 48 — Protocol 11 pre-registered: Study 2b refinement extension to gpt + gemini (2026-08-21)

**Trigger:** author question — reviewers will ask why gpt/gemini families were never refined (Study 2 covered kimi/claude/qwen only). Author decision: draft the protocol and code now; execution pending author go-ahead + OSF registration.

**Artifacts:**
- `DeeWaanAI-Next/protocols/11-PROTOCOL-STUDY2B-REFINER-GPT-GEMINI.md` — Protocol 11: Study 2b, hypotheses H3.1–H3.3, G1/G2 gates, locked analysis plan, budget envelope ≤ $15, exact runbook. Registry entry **D41** added to DESIGN-DECISIONS.md.
- `code/refine_study2b_sample.py` — pilot sampler (20 pairs/family, seed 20260821), stdlib-only. **Executed and verified:** 40 pairs drawn → `runs/refine_b/sample_pilot.json` (zero cost, deterministic from locked Study-1 data).
- `code/refine_study2b_sample_ext.py` — extension sampler (37 pairs/family, seed 20260822), stdlib-only. Verified (37+37 disjoint, union 57/family); output file removed afterwards per gate discipline (regenerated only after G1+G2 pass).
- Run/judge/analyze reuse locked Protocol 09 scripts unchanged (`refine_study2_run.py`, `judge_v2.py`, `refine_study2_analyze.py`) — same frozen refiner prompt `protocol09-v1`, same judge panel, same aggregation.

**Locked pool fact (measured before any execution):** 57 C-T-P↔F-S-N paired runs per family with full text, for gpt and gemini, verified against `runs/fulltext/main_fulltext.json`.

**Family-selection disclosure for the paper (pre-data rationale):** gpt/gemini were deferred from Protocol 09 for budget staging, not excluded by design; Study 2b is the pre-registered completion of the family universe.

**Not yet done (execution prerequisites):** OSF registration of Protocol 11; python env with numpy/scipy/pandas; DEEPSEEK_API_KEY + Together keys; author go-ahead to spend (≤ $15).

## Entry 49 — Study 2b refiner changed to within-family models (D42, 2026-08-21)

**Trigger:** author directive — the research question is the TEAM effect, so each family must be refined by its OWN model; only the refinement prompt may be fixed. Supersedes Entry 48's deepseek-chat refiner plan for Study 2b.

**Changes:**
- Registry entry **D42** added (DESIGN-DECISIONS.md); Protocol 11 §1 (refiner-identity disclosure) and §4 (refiner models, temperatures, budget ≤ $18, runbook) updated.
- `code/refine_study2b_run.py` — NEW runner: per-family refiners locked from `config/model_registry.json` (gpt → `gpt-5.6-luna`, temp 1 API-enforced; gemini → `gemini-3.1-flash-lite`, temp 0), resumable JSONL, judge_v2-compatible store with `refiner_model` recorded per answer. Compile-checked.
- Frozen prompt verified **byte-identical** to Study 2's `refine_study2_run.py` (programmatic check); tagged `protocol11-v1`.

**Consequence:** Study 2b ≠ Study 2 refiner design → results never pooled; difference disclosed in paper. Required keys now: OPENAI_API_KEY + GEMINI_API_KEY (refiners) and DEEPSEEK/Together (frozen judge panel, unchanged). Pilot sample (`runs/refine_b/sample_pilot.json`) unaffected.

**Execution prerequisites (unchanged except keys):** OSF registration of Protocol 11; numpy/scipy/pandas env; author go-ahead to spend (≤ $18).

## Entry 50 — Study 2b expanded to 2×5 factorial: refiner identity × family (D43, 2026-08-21)

**Trigger:** author directive for highest academic standard — (1) continue the universal deepseek refiner for gpt+gemini (refinement as a process), and (2) add within-family refiners for ALL 5 families (team attribution). Supersedes Entry 48/49 scope. Author instruction: do NOT run any code yet.

**Protocol 11 re-drafted** (`DeeWaanAI-Next/protocols/11-PROTOCOL-STUDY2B-REFINER-GPT-GEMINI.md`):
- Arm U: deepseek-chat refiner for gpt+gemini (completes the 5-family universal condition; reuses frozen `refine_study2_run.py` unchanged).
- Arm W: each family's own cheap sibling — luna / flash-lite / kimi-k2.6 / claude-haiku-4-5-20251001 (Anthropic Messages API) / qwen3.7-plus-2026-05-26; temperatures API-enforced per D27 precedent.
- Locked abductive rationale text for reviewers (§1); H3.1-U/H3.1-W/H3.2/H3.3/H3.4 (new refiner-identity contrast, two-sided, no pre-committed direction); G1/G2 gates per arm; Holm + BH-FDR; sampling reuse-first (gpt/gemini arms share sample_pilot.json; W-arm kimi/claude/qwen reuse Study-2 sample files → fully paired H3.4).
- Scheduling locked (§8): DeepSeek calls only UTC 04:00–06:00 or 10:00–01:00 (peak UTC 01–04/06–10 at 2×, off-peak half — NOW IN EFFECT per author); qwen refine calls only UTC 14:00–00:00 (off-peak ~60% discount). Windows overlap at UTC 14:00–00:00.
- Budget envelope ≤ $60 (7 new arms; judging ≈ 3,591 calls dominates).

**Code (written, syntax-checked ONLY — nothing executed per author order):**
- `code/refine_study2b_run.py` — extended to all 5 families; added Anthropic Messages-API path (`x-api-key`, `anthropic-version: 2023-06-01`); thinking traces excluded; keys via `judge_v2.load_key` (env/.env).
- `code/refine_study2b_analyze.py` — NEW, frozen pre-data analysis script: `--mode arm` (H3.1–H3.3 + G1/G2) and `--mode identity` (H3.4 paired W−U); reuses `refine_study2_analyze.py` helpers verbatim (identical aggregation/bootstrap/Holm machinery).
- Judging: frozen `judge_v2.py` unchanged (verified --store/--out CLI matches runbook).

**Registry:** D43 appended to DESIGN-DECISIONS.md (supersedes D42 scope; D41/D42 trail preserved). Pricing-window memories updated (DeepSeek off-peak now in effect; old UTC+8 schedule retired).

**Execution prerequisites:** OSF registration of re-drafted Protocol 11 (before first call); keys OPENAI + GEMINI + KIMI + ANTHROPIC + ALIBABA (refiners) + DEEPSEEK + Together (panel); numpy/scipy/pandas env; scheduling-window compliance; author go-ahead for ≤ $60.

## Entry 51 — Study 2b EXECUTION LOG: pilots complete, G2 fails in every testable family (2026-08-22)

Author go-ahead received ("ok proceed with all what is needed"). Execution followed the Protocol 11 §9 runbook verbatim. All DeepSeek calls (arm-U refiner + deepseek judge) ran inside the off-peak windows; qwen refinement ran inside UTC 14:00–00:00.

**0. OSF registration (hard prerequisite, completed BEFORE any Study-2b call):** registration **83c9u** (https://osf.io/83c9u), Open-Ended Registration branched from node 8pwej; state in `preregistration/osf_submission/.osf_state_study2b.json`. Technical findings (documented in `code/osf_register_study2b.py`): uploader file objects make POST /registrations/ reject the draft ("files attached but not part of a component being registered") — files freeze automatically via the storage archive (same as Study-1 mjb8x); subjects must be PATCHed onto the DRAFT. Registration summary states the timestamp precedes all Study-2b data collection — TRUE.

**1. Arm U pilot (deepseek-chat refiner, gpt+gemini, 40 pairs):** refinement 40/40 → `runs/logs/refine_b_U_pilot.jsonl` + `runs/refine_b/refined_store_U_pilot.json`; judging 360/360 → `runs/logs/refine_b_U_judgments_pilot.jsonl`; analysis → `results/refine_study2b_U_pilot.json`. **G1 pass (1.0). G2 FAIL both families** (gemini d=-0.371; gpt d=-0.092; CIs do not exclude 0 in the positive direction). H3.2 novelty protection pass both.

**2. Arm W block 1 (own cheap siblings, gpt+gemini, SAME 40 pairs):** refinement 40/40 after ONE documented redo: gpt-5.6-luna rejected `temperature` entirely (omit), rejected `max_tokens` (use `max_completion_tokens`), then 2/20 pairs returned empty content because the reasoning model spent the full 8192-token budget on internal traces (finish_reason=length, reasoning_tokens=8192) — fixed with `reasoning_effort=low` and ALL 20 gpt pairs redone for within-arm parameter consistency; original log preserved as `runs/logs/refine_b_W_pilot_attempt1.bak.jsonl`. Judging 360/360; analysis → `results/refine_study2b_W_pilot.json`. **G1 pass. G2 FAIL both families** (gemini d=-1.954, CI [-0.436,-0.286] — refined WORSE than frontier solo; gpt d=0.009 — null). Secondary: gemini refined BEATS its own original C-T-P (composite +0.262, Elaboration +0.633) yet still loses to F-S-N; gpt refinement ≈ no change vs original.

**3. Arm W block 2 (kimi+claude+qwen, Study-2 pilot pairs, 60 pairs):** claude-haiku-4-5 20/20 and qwen3.7-plus 20/20 (qwen inside its discount window); **kimi 0/20 — BLOCKED: Moonshot account org-6706…cc43 suspended for insufficient balance (exceeded_current_quota_error), confirmed twice by direct probe; NOT a technical fault; author action required (recharge or formally drop kimi)**. Judging 360/360 (1 meta INCOMPLETE record excluded by frozen aggregation, same treatment as Study 2); analysis → `results/refine_study2b_W3_pilot.json`. **G1 FAIL (completion 0.667, caused solely by the kimi block; claude+qwen subset 40/40). G2 FAIL claude (d=-1.185) and qwen (d=-0.860)**, both CIs excluding 0 on the negative side. H3.3: qwen repair visible (Usefulness +0.317, Elaboration +0.461) yet composite still below F-S-N.

**4. H3.4 refiner-identity contrasts (pilot stage):** `results/refine_study2b_identity_pilot.json` (gpt/gemini, U vs W same pairs): gemini W−U d=-1.78, p_holm≈0.0 (own sibling markedly WORSE than universal deepseek); gpt W−U d=0.085, n.s. `results/refine_study2b_identity_W3_pilot.json` (claude/qwen W3 vs Study-2 universal judgments, fully paired): claude W−U d=-0.471 (p_holm=0.0485), qwen W−U d=-0.593 (p_holm=0.0314) — universal refiner edges within-family in both.

**5. Gate decision (pre-registered, Protocol 11 §6):** every testable family fails G2 in every new arm → **NO extension is executed**; all pilot results stand as pilot-stage nulls/negative findings, as the protocol commits. kimi's two cells remain unrun pending the author's recharge/drop decision.

**6. Code fixes disclosed (post-freeze, bug class only — no hypothesis, sample, gate, or decision rule touched):** (a) `refine_study2b_run.py`: 429-retry loop exhaustion implicitly returned None → now raises RuntimeError; (b) `refine_study2b_analyze.py::two_sided_paired`: `2*p_one_sided` truncated negative effects to p=1.0 → corrected to `2*min(p,1-p)` (identical to the formula already used in the same file's dim_block); both identity outputs re-generated with the fix.

**Outputs:** refined stores + judgment logs + 5 result JSONs as named above; spent ≪ the $60 envelope (extensions never triggered; judging = 1,080 calls total).
## Entry 52 — kimi unblocked via Together.ai (PROTOCOL DEVIATION, disclosed) + FINAL pilot gates (2026-08-22)

Supersedes the kimi-blocked status in Entry 51 §3. Author directive: "use together.ai".

**Deviation (pre-analysis, disclosed per main-run Kimi migration precedent):** the locked kimi W-arm refiner `kimi-k2.6` (Moonshot direct) was unavailable — direct account suspended for insufficient balance, and Together's `moonshotai/Kimi-K2.6` listing is NON-serverless (requires a paid dedicated endpoint; probe 400 `model_not_available`). The refiner was switched to **`moonshotai/Kimi-K3` on Together serverless** (same family — the W-arm construct is family identity; different version; `reasoning_effort=none` verified to disable reasoning so the editing behavior matches the other non-reasoning cheap refiners; temperature 1 retained as locked). No hypothesis, sample, judge, gate, or decision rule changed. Limitation for the paper: kimi's W cell used K3, not K2.6.

**Execution:** kimi 20/20 refined (`refine_b_W3_pilot.jsonl`, store now 60/60; outputs notably long — arm length ratio 1.474); kimi 180 judge calls completed inside the DeepSeek window (540 total in `refine_b_W3_judgments_pilot.jsonl`; 1 meta INCOMPLETE record on R3717/var2 excluded by frozen aggregation, same treatment as Study 2).

**FINAL pilot results (all 5 families now measured):**
- G1: arm U 1.0 pass; arm W block 1 1.0 pass; arm W block 2 now **1.0 pass**.
- H3.1 (refined vs F-S-N): gpt d=+0.009, kimi d=+0.087 (nulls, CIs include 0); gemini d=-0.371 (U) / -1.954 (W), claude d=-1.185, qwen d=-0.860 (significantly NEGATIVE).
- H3.2 novelty protection: pass all families in both arms.
- H3.4 (W−U): gemini d=-1.78 (p_holm≈0); gpt d=+0.085 n.s.; kimi d=+0.030 n.s.; qwen d=-0.593 (p_holm=0.047, survives 3-family Holm); claude d=-0.471 (p_holm=0.097 after re-correction over 3 families); pooled d=-0.348, p=0.009 — the universal (cross-family) refiner beats the within-family editor on pooled evidence.
- **G2 FINAL: fail in every family of every new arm → no extension executed (pre-registered commitment). Study 2b closes at pilot stage as a set of null/negative findings.**

**Scientific reading:** refinement-as-process does NOT generalize beyond the Study-2 families; where an effect of refiner identity exists, it favors the cross-family outsider (deepseek), not the in-family editor. The Study-2 positive result is best interpreted as partly refiner-specific. Cost: ≪ $60 envelope (Together K3 refinement ≈ $1; judging 1,260 calls total across the study).

## Entry 53 — 2026-08-22 — Exploratory heterogeneity & robustness battery (D44), frozen-data re-analysis
**Status:** COMPLETE · **Author directive:** "run them all as you recommended" · **Cost:** $0 (no API calls; re-analysis of frozen Study-1 artifacts) · **Decision register:** DESIGN-DECISIONS D44 (with per-analysis academic grounding)

**Context:** session deep-dive showed the team effect is domain-contingent (marketing +0.004 vs finance −0.106 vs F-S-N) and the family capability gap correlates with the team effect at r = −0.978 (n=5 families). Seven exploratory angles were registered (D44) and executed on the locked ledger + judgments.

**Artifacts:** `code/exploratory_heterogeneity.py` (deterministic) → `results/exploratory_heterogeneity.json` → report `results/EXPLORATORY-HETEROGENEITY.md`.

**Results digest (all EXPLORATORY):**
1. **A1 reliability:** Brown–Forsythe: no family-level variance reduction by teams (all p ≥ 0.33). Downside P(comp<4.0): 2.81% → 1.75% → 1.05% across C-S-N/C-T-N/F-S-N (monotone, mild). EXCEPTION: marketing team SD significantly lower than solo (p = 0.020) — mean and reliability wins converge there.
2. **A2 difficulty moderation:** NULL (r = +0.153, p = 0.532; difficulty band narrow 4.21–4.73).
3. **A3 length ANCOVA (LMM):** team-vs-cheap-solo effect +0.026 raw → −0.018 after log-token control (n.s., length-explained; flip not to be over-read); frontier effect +0.081 → +0.078 (survives, capability); length coefficient +0.031 (p = 0.014) confirms judge length-bias channel. Caveat logged: quality is judged on visible full text, so length control partly controls the mechanism under study (report asymmetry, not "mediation").
4. **A4 latency:** C-S-N 47.2 s / C-T-N 131.7 s / F-S-N 94.8 s — frontier solo is FASTER than the team; quality-per-$-minute 295.8 vs 28.1 vs 34.7; all cells tri-objective Pareto-optimal. Orchestration's case is cost-only.
5. **A5 dimensions × domains:** no Holm survivor (3–4 problems/domain); descriptively all largest team losses are on Novelty in analytical domains.
6. **A6 rank stability:** Kendall's W = 0.922 (teams) vs 0.665 (frontier) across 6 domains — family team ranking is domain-invariant.
7. **A7 ICC(3,k=9) by domain:** 0.908/0.908/0.903/0.873/0.827/0.734 (marketing/strategy/ops/finance/product/hr) — HR is the least reliable measurement channel.

**Pre-registration discipline:** all seven analyses labeled exploratory/post-hoc (D44 binding clause; Nosek et al. 2018); zero contact with Fresh_Case_1–10 (reserved confirmatory replication); confirmatory record H1–H6 untouched.

## Entry 54 — 2026-08-22 — Persona-extended heterogeneity battery (D45), frozen-data re-analysis
**Status:** COMPLETE · **Author directive:** "run the tests" · **Cost:** $0 (no API calls) · **Decision register:** DESIGN-DECISIONS D45

**Context:** D44 battery extended with the Persona axis. Coverage verified first (author question): all 8 cells × 5 families fully collected (C-S-P/C-T-P/F-S-P = 285/285/190 per family 57/57/38) — solo+persona and team+persona were indeed tested for all families.

**Artifacts:** `code/persona_heterogeneity.py` → `results/persona_heterogeneity.json` → Part II of `results/EXPLORATORY-HETEROGENEITY.md`.

**Results digest (all EXPLORATORY):**
1. **P1 Cultural Sensitivity:** persona effect NULL everywhere (pooled d −0.10 to −0.05, p_holm ≥ 0.30; all 12 domain cells n.s.) — personas do not move the dimension they were designed for.
2. **P2 novelty/usefulness by domain:** solo personas: novelty +0.36 to +0.57 and usefulness −0.96 to −1.10 in ALL 6 domains (uniform trade-off); team personas: novelty NEGATIVE in all domains (−0.08 to −0.35) while usefulness cost shrinks to −0.20 to −0.51.
3. **P3 length ANCOVA (LMM, cheap tier, structure×persona):** persona main effect on Novelty +0.465 (p<0.001) SURVIVES length control (genuine effect, unlike the team edge in Entry 53 A3); composite persona cost −0.250 survives; team×persona interactions: Novelty −0.693***, Usefulness +0.711*** — teams squash the persona novelty gain.
4. **P4 ICC:** persona answers slightly MORE reliable (ICC(3,9) 0.933 vs 0.918; ICC(3,1) 0.608 vs 0.555) — not a measurement artifact.
5. **P5 variance:** personas roughly double outcome SD (solo 0.232→0.397, team 0.211→0.348, all p≈0, all domains).

**Pre-registration discipline:** same as Entry 53 — exploratory label binding; H1–H6 record untouched; Fresh_Case_1–10 reserved.

---

## Entry 55 — 2026-08-22 — D46 recorded: MiniMax price accounting (list prices primary, promo vector as sensitivity)

**Context:** confirmatory-wave family verification. Both new API keys tested live: MISTRAL_API_KEY (api.mistral.ai, 56 models, `mistral-large-latest` and `mistral-small-latest` completions clean) and MINIMAX_API_KEY (api.minimax.io, completions clean for M3 / M2.7 / Text-01).

**Verified prices (official sources, 2026-08-22):** Mistral Medium 3.5 (`mistral-medium-3-5-26-04`, chosen frontier — Mistral's designated successor to all deprecated large/medium models) $1.50/$7.50; Mistral Small 4 (`mistral-small-2603`, cheap) $0.15/$0.60 → output multiple 12.5×. MiniMax-M3 list $0.60/$2.40 (billed at permanent-50%-off = $0.30/$1.20); MiniMax-M2.7 $0.30/$1.20.

**Decision (author-approved):** minimax primary accounting uses LIST prices (multiple 2×); the as-billed discounted prices (multiple 1×) are reported as a sensitivity vector. Grounded in Simmons, Nelson & Simonsohn (2011), Nosek et al. (2018), Saltelli et al. (2008); consistent with prior treatment of Qwen/DeepSeek discount windows. Full rationale in DESIGN-DECISIONS.md D46.

**Integration flags:** MiniMax M-series emit `<think>` reasoning traces → reasoning setting must be pinned explicitly (Kimi-K3 precedent); M2.5/M2.1/M2 marked Legacy on MiniMax's pricing page → cheap sibling locked to M2.7.

**No generation/judging calls made** beyond 1-token smoke tests; no effect on the locked Study-1 record.

---

## Entry 56 — 2026-08-22 — Paper draft v10: D44/D45 exploratory battery integrated

**Change:** new draft `paper/FULL-PAPER-DRAFT-BUSINESS-v10_with_figures/FULL-PAPER-DRAFT-BUSINESS-v10.tex` (copied from audited v9).

**Edits:**
1. New Results subsection "Exploratory Heterogeneity: Domain Contingency, a Capability-Gap Mechanism, and the Persona Decomposition" (sec:exploratory-heterogeneity) with explicit exploratory/post-hoc status declaration (Nosek et al. 2018), covering A1–A7 and P1–P5 with exact numbers from `results/exploratory_heterogeneity.json` / `results/persona_heterogeneity.json`, the A3 measurement caveat (length partially IS the intervention — asymmetry reading, not mediation), and the n=5 caveat on the capability-gap correlation.
2. Summary-of-findings table: one exploratory row pointing to the new subsection.
3. Future Directions: new first item — pre-registered out-of-sample replication wave (30 fresh problems, second 6×5 domain grid, core cells C-S-N/C-T-N/F-S-N, family universe 5→10) as the gate that decides which exploratory findings become headline claims; remaining items renumbered.
4. Eight new references with DOIs: Hansen & Salamon 1990; Dietterich 2000; Brown & Forsythe 1974; Borenstein et al. 2009; Dubois et al. 2024; Holm 1979; Kendall & Babington Smith 1939; Shrout & Fleiss 1979.

**Verification:** two pdflatex passes, exit 0, 30 pages, zero undefined references, zero LaTeX errors.

**Discipline:** confirmatory record (H1–H6) untouched; all new content labeled exploratory; Fresh_Case replication wave still requires OSF pre-registration BEFORE any fresh generation (pending step 2).
---

## Entry 57 — 2026-08-23 — Confirmatory replication wave pre-registered (D47–D50, Protocol 12, OSF jg49x)

**What was locked (all BEFORE the first wave generation call):**
1. **D47** — wave scope/design: 30 fresh problems × 10 families × 3 core cells (C-S-N/C-T-N/F-S-N), cheap ×3 / frontier ×2 reps = 2,400 generation runs; frozen judge panel ×3 verbatim variants = 21,600 judge calls; binding upgrade gate for the Study-1 exploratory findings; author credit-exhaustion policy (skip exhausted family, continue others). Grounded in OSC 2015 (doi:10.1126/science.aac4716), Camerer et al. 2018 (doi:10.1038/s41562-018-0399-z), Simons 2014, Nosek et al. 2018.
2. **D48** — family universe 5→10 with verified model/price/provider pins (thinkingmachines/Inkling, gpt-oss, gemma on Together; mistral direct; minimax direct; kimi Moonshot-direct after K2.6 Together retirement 2026-08-19); MiniMax reasoning pinned at vendor defaults + traces stripped before judging.
3. **D49** — 20 newly authored fresh cases complete the second 6×5 domain grid (Fresh_Case_11–32 minus 24/28; `fresh_business_cases_20_wave.json` + `fresh_domain_map_wave.json`). Grounded in Maxwell 2004 (doi:10.1207/s15327906mbr3901_7), Borenstein et al. 2009.
4. **D50** — persona/refinement cells excluded from the wave (own frozen records exist; budget ≈ $250–350); disclosure obligation recorded.
5. **Protocol 12** (`DeeWaanAI-Next/protocols/12-PROTOCOL-WAVE-CONFIRMATORY-REPLICATION.md`) with W1–W7 gate tests and execution discipline.
6. **OSF registration jg49x** submitted 2026-08-23T14:42:17 UTC (before any wave generation); stimulus files stored with OSF timestamps under child component osf.io/ezuwt with sha256 hashes in the registration summary (OSF API does not permit form file attachments — same documented limitation as mjb8x). State: `preregistration/osf_submission/.osf_state_wave.json`.
7. **Analysis lock:** `code/analyze_wave.py` (W1–W7, Study-1 reference values computed from frozen Study-1 artifacts pre-wave) and `code/judge_wave.py` (thin wrapper over frozen judge_v2.py + defensive reasoning-strip) written before judging, per Protocol §5.6.

**Platform prep:** MiniMax provider slug added to DeeWaanAI (commit 55706c2, deployed to Railway) so `add_provider` accepts it.

---

## Entry 58 — 2026-08-23 — Wave platform setup + mini-pilot (t5/t6)

**Providers added:** mistral (id 19, api.mistral.ai) and minimax (id 20, api.minimax.io) via MCP add_provider; together=18 confirmed; ids archived in `pipelines/fixed/wave_provider_ids.json`.

**Pipelines (30, `pipelines/fixed/wave_pipelines_registry.json`):** 12 Study-1 frozen pipelines reused (gpt/claude/gemini/qwen × C-S-N/C-T-N/F-S-N — identical instrument); 18 created new (kimi ×3 on Moonshot provider 12 — ROUTING-ONLY deviation with Study-1 precedent, since the frozen kimi pipelines sit on Together where K2.6 was retired 2026-08-19; plus thinkingmachines/gpt-oss/gemma/mistral/minimax ×3). Study-1 frozen registry untouched.

**Mini-pilot:** 6 new families × {Fresh_Case_1, Fresh_Case_2} × all reps = 96 runs, inside the UTC 14:00–00:00 window, concurrency 40 (new-provider caps mistral/minimax = 4, placeholder ramp values in `config/wave_concurrency.json`).

**Results:** gemma 16/16 and gpt-oss 16/16 clean; kimi (Moonshot direct), minimax, thinkingmachines completing cleanly; mistral cheap/team cells clean but ALL 4 frontier (F-S-N) attempts failed at step 1 → root cause found: pinned model id invalid (Entry 59 / D51). One transient mistral frontier failure pre-dates the id discovery. Kimi route validated live (Moonshot-direct completions non-empty).

---

## Entry 59 — 2026-08-23 — D51: mistral frontier model id corrected pre-data (mistral-medium-3-5-26-04 → mistral-medium-2604)

**Discovery:** api.mistral.ai rejects `mistral-medium-3-5-26-04` (400 invalid_model); the correct dated snapshot of Mistral Medium 3.5 is `mistral-medium-2604` (alias `mistral-medium-3.5` resolves to the same model; both verified callable). Price re-verified unchanged ($1.5/$7.5).

**Legitimacy:** zero valid observations existed under the invalid id (the 4 failed attempts produced no output; failures are never scored); the fix changes only the vendor identifier string; made before the first successful mistral frontier generation; disclosed in DESIGN-DECISIONS D51, Protocol 12 §3, model_registry.json, both price vectors, the wave registry, and platform pipeline 69 (update_pipeline). Grounding: Nosek et al. 2018; Simons 2014.

---

## Entry 60 — 2026-08-23 — Mini-pilot close-out, ramp decision, full wave launch (t6 → t7)

**Mini-pilot final (96 runs, 6 new families × {Fresh_Case_1, Fresh_Case_2} × all reps):** 90/96 completed with non-empty full text on first pass; **zero 429s, zero credit-exhaustion events** across ~50 min at global concurrency 40 (new-provider caps mistral/minimax = 4). gemma 16/16, gpt-oss 16/16, minimax 16/16, thinkingmachines 16/16, kimi 14/16, mistral 12/16 (4 frontier failures under the invalid id — Entry 59).

**Mistral fix verified post-D51:** all 4 F-S-N re-runs completed on `mistral-medium-2604` (runIds 4805/4808/4809/4810) — end-to-end frontier generation now clean on provider 19.

**Kimi routing disclosure:** F-S-N Fresh_Case_2 hit repeated platform-side `fetch failed` at step 1 (tok=0) on the Moonshot-direct route — runIds 4737, 4788 (mini-pilot) and 4806, 4807 (fix-rerun); platform auto-retry observed on 4807. Fresh_Case_1 frontier completed normally both times (e.g., runId 4763), and all kimi cheap/team runs completed — so the route works; this specific task exhibits intermittent first-attempt fetch failures. Both tasks remain in the full-wave queue (resume re-attempts non-completed records); any residual failures will be disclosed in the wave report with the affected cell counts. This is a transport-level event (no tokens consumed, no output produced, nothing scored).

**Ramp decision (`config/wave_concurrency.json` updated):** highest-clean-level criterion (§5.3) — mistral/minimax clean at 4 → doubled to 8 (conservative step; any full-wave 429 is captured per-run in `realError` and the cap revisited); thinkingmachines/gpt-oss/gemma clean at 30 → kept; kimi clean at effective 40 → kept at 60; Study-1 families inherit D34 levels (gpt/claude/gemini 100, qwen 60).

**Full wave launched 2026-08-23 ≈15:57 UTC** (inside the discount window; window gate UTC 14:00–00:00 enforced in-runner): `node code/wave_run.mjs --concurrency 100` (pid 29286, log `runs/logs/wave_full.log`). Scope 2,400 runs; the 90 completed mini-pilot records are resume-skipped, the 6 failed/timed-out records re-attempted. Per author policy (2026-08-23): a credit-exhausted family is skipped and the others continue (`runs/logs/wave_credit_exhaustion.jsonl` sidecar).

---

## Entry 61 — 2026-08-23 — Gemini provider throttling during full wave; family isolated per author policy

**Event:** full wave round 1 (launched ≈15:57 UTC, c=100, all 10 families) produced systematic gemini failures: 54+ runner-side 20-min timeouts with tok=0 across ALL three cells; platform step_error stream shows repeated `Provider throttled, retry after Nms` (e.g., runId 5169) followed by silent retry loops (runIds 5759/5760). Other 9 families ran clean (zero 429s; gpt 94/claude 83/etc. completing normally in the same interval).

**Diagnosis and response:** cap lowered 100 → 10 (D34 fallback logic; `config/wave_concurrency.json` SAME-DAY CORRECTION note) and the wave restarted on resume (round 2, pid 67363) — gemini STILL failed at cap 10 with identical tok=0 signature → the failure is not runner-side concurrency but a provider-side condition (quota exhaustion or outage on the Google key; Study-1's c=100 calibration predates the 10-family aggregate load regime).

**Isolation (author credit-exhaustion policy applied by analogy):** round 3 (pid 76904) runs the other 9 families (2,160 tasks) unimpeded; a separate gemini probe lane at c=1 (pid 77358, Fresh_Case_3 only, log `runs/logs/wave_gemini_probe.log`) tests whether the provider can complete ANY run. Outcome branches: (a) probe completes → gemini re-admitted at a validated low cap in a dedicated lane; (b) probe fails → gemini DEFERRED to the next discount window (quota reset), disclosed in the wave report with affected-cell counts; either way the 9-family record proceeds and gemini's gate contributions are reported as missing-at-random-by-provider, not imputed.

**Integrity notes:** all failed/timed-out attempts consumed zero tokens and produced no scored output; resume re-attempts only non-completed records; orphaned platform runs from rounds 1–2 that later complete server-side are never captured (same treatment as Study-1 timeout repairs). No analysis-relevant data was collected under the throttled regime.

---

## Entry 62 — 2026-08-23 — Wave generation close for this window: 2,060/2,400 (8 families complete; kimi credit-exhausted at 140/240; gemini 0/240 deferred)

**Completed this window (UTC 14:00–20:05):** claude, gpt, gpt-oss, gemma, mistral, minimax, qwen, thinkingmachines — all 240/240 (30 problems × 3 cells × reps), zero 429s on these families after the ramp. Total completed 2,060 runs; ledger `runs/logs/wave_run_ledger.json` (2,218 records incl. failed attempts).

**Kimi (140/240: C-S-N 58/90, C-T-N 52/90, F-S-N 30/60):** Moonshot account balance exhausted mid-wave ("API credit exhausted: Moonshot Kimi: Account balance insufficient", run_status error of runId 5896; sidecar `runs/logs/wave_credit_exhaustion.jsonl`). Recovery option considered and REJECTED for this window: the Study-1 precedent (2026-08-04, all-cell migration to Together) does not transfer because K2.6 was retired on Together 2026-08-19 — only F-S-N (K3) could move, creating a within-family cheap/frontier routing asymmetry absent from any prior record; per author policy the remainder is deferred to a later lane after credits are restored. The 140 completed kimi runs remain valid (all Moonshot-direct, homogeneous routing).

**Gemini (0/240):** provider-side failure regime all day (throttle → silent retry loops → tok=0 even at c=1, Entry 61); deferred to the next discount window pending quota reset/outage clearance; probe-first re-admission required.

**Runner fixes committed en route:** credit detection fallback to run_status.error; exhausted-family skip (§5.4); worker-queue race (atomic claim). Judging proceeds on the 2,060 completed runs; gemini/kimi remainders will be judged in follow-up lanes after completion (judge_v2.py resumable).

---

## Entry 63 — 2026-08-23 — Judging launch (2,054 runs); regex near-miss caught pre-judging; empty-response re-runs

**Near-miss caught before any judge call:** `judge_wave.py`'s reasoning-strip regex `THINK_RE` had been saved with an EMPTY pattern (the tag-shaped literal was stripped when the file was authored through tooling). An empty regex matches at every position, so the first `--store-only` build reported all 2,049 docs "stripped" (counts 209–1,975 per doc). Because the replacement string was also empty, the stored text itself was unchanged — verified — but the disclosure counters were wrong. Fix: pattern re-assembled from string parts (`"<"+"think"+">"`) so no tag-shaped literal appears in source; store rebuilt → exactly the 240 MiniMax docs carry residual `<think>` traces (matches D48's vendor-default expectation; every stripped doc counted in `docs_with_reasoning_stripped`). No judge call was made under the faulty regex; this is a pre-data instrumentation fix, disclosed per Nosek et al. 2018.

**Empty-response re-runs:** 11 frontier runs (claude F-S-N ×5, kimi F-S-N ×6) had completed status with ~10–13k tokens consumed but empty finalResponse in BOTH run_status and export_run (platform-side content loss; cf. Study-1 DB-write incident). Resume logic requires non-empty content (Study-1 lesson), so a claude/kimi lane re-ran them: all 5 claude recovered non-empty (runIds 7152–7156); the 6 kimi remain empty-pending (Moonshot credit exhaustion — deferred with the kimi remainder). Auto credit-detection fired correctly this time (sidecar entry 20:04:48 UTC) and skipped kimi's remaining queue.

**Judging launched 2026-08-23 ≈20:12 UTC** (off-peak for DeepSeek; window discipline §5.5): `judge_wave.py` → frozen `judge_v2.py` (3 judges × 3 verbatim variants, temp 0, blinded, seed 20260731), store = 2,054 runs → 18,486 planned judge calls; output `runs/logs/wave_judgments.jsonl`, console `runs/logs/wave_judging_console.log`. Judgeable population this wave: claude/gpt/gpt-oss/gemma/mistral/minimax/qwen/thinkingmachines 240 each, kimi 134 (of which 6 empty excluded → 134 in store), gemini 0. Correction to Entry 62 headline: 2,060 completed-status records, of which 2,054 judgeable after the claude re-runs and 6 kimi empty-pending.

---

## Entry 64 — 2026-08-24 — Confirmatory analysis executed (wrapper fallback disclosed); gates: W1/W2/W6 PASS, W3/W4/W5 FAIL

**Judging close (prior step, carried over):** 18,450/18,450 unique judge keys completed over 4 resumable passes (pass1 DNS churn 5,586 transient errors; pass2-4 backfill; zhipu/meta/deepseek 402s were transient, not exhaustion). 2,050 judged runs enter analysis (kimi 134 incl. 6 empty excluded at store build; minimax 236; all others 240; gemini 0 deferred). 27 orphan judgments belong to quarantined pre-re-run minimax runIds and join to nothing.

**Numerical event — pre-registered LMM singular:** frozen `analyze_wave.py::lmm` (dual vc: problem + family:problem) raised `LinAlgError: Singular matrix` at the first fit (W1). Diagnosis before gate outcomes: each single-vc spec converges with BIT-IDENTICAL fixed effects (W1 C-T-N coef 0.016734682689594604 both ways) — the imbalanced panel (kimi credit-exhausted; gemini deferred) makes the dual-vc structure numerically non-identifiable. Resolution: disclosed runtime wrapper `code/run_wave_analysis.py` (D52) — frozen script untouched (sha256 94729d02… embedded in output), rule declared pre-execution: try frozen spec → on LinAlgError fit both single-vc specs, hard-require convergence + identical fixed effects (rtol 1e-6), sticky single-vc thereafter so the W3a LRT pair shares RE structure. 4/4 LMM calls fell back; full per-call disclosure in `lmm_numerical_fallback_disclosure` of both results JSONs.

**Gate outcomes (primary price vector; n=2,050 judged runs, 9 families, α=0.05):**
- W1 team effect: coef +0.0167, p=0.00647 → **PASS** (replicates Study-1 core).
- W2 upgrade threshold: F-S-N over C-T-N coef +0.0912, p<0.0001 → **PASS**.
- W3a cell×domain interaction: LRT χ²=−45.506 (negative — REML vc-structure caveat, D52), p=1.0 → **FAIL**. W3b signs 5/6 (marketing flipped negative: Δ=−0.083 vs Study-1 +0.0037; strongest negative = finance as predicted, strongest positive = none) → **FAIL**. W3 gate **FAIL**.
- W4 capability-gap mechanism (9 complete families): Pearson r=−0.2445, p=0.526; Spearman ρ=−0.033, p=0.932 (Study-1 ref r=−0.978; power at n=9 for ρ=0.80 is 0.768) → **FAIL**; stays exploratory.
- W5 marketing variance advantage: Brown-Forsythe p=0.990, sd_team 0.290 > sd_solo 0.274 → **FAIL**; pooled p=0.752 (no gate).
- W6 economics: C-S-N $0.0154 / 4.471, C-T-N $0.0657 / 4.487, F-S-N $0.0618 / 4.573; quality/$·min F-S-N 47.3 > C-T-N 18.7; Pareto {C-S-N, F-S-N}; T-EGR C-S-N 3.918, C-T-N 0.922 → **PASS**.
- W7 ICC(3,1) by domain: 0.480–0.629 (ICC(3,k) 0.892–0.939) — judge reliability audit, no gate.
- Upgrade-gate summary: all three Study-1 exploratory findings (domain contingency, capability-gap mechanism, marketing variance advantage) FAIL the gate and REMAIN EXPLORATORY; core replications W1/W2/W6 hold.

**Sensitivity (--promo, D46 minimax promo vector):** identical gate pattern; W6 cost shifts C-S-N $0.01485 / C-T-N $0.06275 / F-S-N $0.06042, T-EGR 3.978/0.945 — conclusions robust to the minimax pricing scenario.

**Disclosures carried into WAVE-REPLICATION-REPORT.md:** gemini 0/240 (provider outage, deferred), kimi 134/240 judged (credit exhaustion; 6 empty F-S-N pending), minimax 236/240 (quarantine re-runs), THINK_RE near-miss (Entry 63), LMM numerical fallback (D52), W3a REML-LRT caveat. Report written this date; frozen artifacts unchanged.

## Entry 65 — 2026-08-26/28 — Wave COMPLETE (2,400/2,400, 10 families); judging complete (0 pending); re-analysis: gate pattern unchanged

**Deferred lanes executed (D53):**
- **gemini 240/240** — the "outage" was the free-tier daily cap (150 req/day/model, 429 `generate_requests_per_model_per_day`); resolved by the author's Google billing upgrade. Probe-first re-admission per Entry 61 (Fresh_Case_3 c=1, 8/8 clean, runIds 7166–7173), then remainder lane at c=10 (`runs/logs/wave_gemini_lane.log`): 232/232, zero throttled.
- **kimi 240/240** — Moonshot recharge landed (org 670685b8…cc43 verified by probe); cheap cells (C-S-N/C-T-N, `kimi-k2.6`) completed Moonshot-direct. **Author directive 2026-08-26:** kimi F-S-N routed via **Together serverless `moonshotai/Kimi-K3`** (new pipeline id 73, `oe-wave-kimi-F-S-N-tgr`) — supersedes the Entry-62 deferral of exactly this routing asymmetry; same pinned model version, temp 1, maxTokens 8192; 30 F-S-N runs from 08-23 remain Moonshot-direct. Disclosed as D53; per-run route membership auditable via `projectId` in the ledger.
- Kimi empties (tok≈9–10k, len=0, platform-side content loss on BOTH routes) recovered over five resume passes; last pending run (F-S-N Fresh_Case_26 r1) recovered 2026-08-28 runId 7631. Final state: **every one of the 2,400 planned wave runs completed with non-empty content; zero pending; zero imputed.**

**Judging (2026-08-28):** store rebuilt (2,422 runs; 240 MiniMax reasoning-strip docs per D48; 30 not-completed + 8 empty stale records auto-excluded). Backfill pass: deepseek third completed first; Together 402 credit exhaustion mid-pass (K3 generation had consumed the balance) — author recharged; resume passes completed **0 pending** (21,762 unique judge keys; +27 orphan judgments from quarantined minimax runIds, join to nothing). One local SSL/cert incident under user-site Python (no scores recorded; relaunched under managed runtime). DeepSeek calls inside off-peak rules (weekend off-peak-all-day per the 2026-08-23 pricing change, Beijing time).

**Re-analysis (disclosed wrapper; frozen `analyze_wave.py` byte-identical):** n = 2,418 judged runs, 10 families complete. **Gate pattern UNCHANGED:** W1 PASS (+0.0168, p=0.00217) · W2 PASS (+0.0745, p<0.0001) · W3 FAIL (χ²=−47.5, p=1.0; signs 5/6; marketing still negative) · W4 FAIL (n=10; r=−0.2141, p=0.553; power for ρ=0.80 now 0.828) · W5 FAIL (marketing p=0.795, direction still reversed; pooled p=0.618) · W6 PASS (Pareto {C-S-N, F-S-N}; T-EGR 4.044/0.956; promo 4.11/0.98 — gates unchanged) · W7 ICC(3,1) 0.471–0.622. The three Study-1 exploratory findings REMAIN exploratory per the binding upgrade rule (D47). 4/4 LMM calls fell back under D52 on the now-balanced panel — the singularity is structural to the design, disclosed in the results JSONs.

**Artifacts:** `results/wave_analysis.json`, `results/wave_analysis_minimax_promo.json` (regenerated); WAVE-REPLICATION-REPORT.md §Update 2026-08-28; lane logs `wave_gemini_probe2.log` / `wave_gemini_lane.log` / `wave_kimi_lane2–5.log` / `wave_judging_console2–5.log`.

## Entry 66 — 2026-08-28 — Reviewer-facing results layer materialized (D54); standing rule: every stat test ships as a file

**Author directive:** statistical test results must live in files readable without re-running code; reusable for figures/secondary analyses; same treatment for qualitative coding.

**Built:** `code/materialize_results.py` (stdlib-only, idempotent, ZERO API calls, never recomputes a hypothesis test — joins frozen judgment logs to frozen ledgers, flattens existing result JSONs; only descriptive quantities computed, labeled `computed_by=materialize_results`).

**Outputs (all verified):**
- `evaluation/scores_aggregated.csv` — 17,091 rows = 1,900 solutions × ≤9 judgments (7 solutions at 8 and 1 at 7 = the audited Interim-2 incompletes); families 3,420/3,420/3,420/3,420/3,411.
- `evaluation/kappa_by_dimension.csv` — Fleiss' κ over the 9-rater matrix: novelty 0.235, usefulness 0.334, flexibility 0.281, elaboration 0.377, cultural sensitivity 0.466 (n = 1,900; descriptive label).
- `evaluation/judge_raw/` — 17,091 Study-1 + 21,762 wave per-call files (prompt variant, judge, raw response, parsed scores).
- `analysis/results/` — `INDEX.csv` + 13 CSVs: descriptive_stats, effect_sizes (Interim-2 H1–H5 + A3), heterogeneity_battery (D44/D45), tegr_by_arm, wave_scores_aggregated (21,762), wave_gates (W1–W7 × 2 price vectors), refine_scores_aggregated (2,794; Studies 2/2b), study2_refine_results, qual_codebook_kappa (13 codes + pooled κ = 0.824 with 0.70 gate column), qual_code_application (378 text × coder vectors), qual A4/Study-2 flattened tables.

**Bug caught at materialization (fixed same day):** documented `solution_id` scheme was not unique under the within-family factorial (collapsed 1,900 → 380); now `{cell}__{family}__{problem}__{rep}`. Labeling layer only — judgment logs were always keyed by unique runId.

**Standing rule (D54):** every future analysis writes its result JSON to `results/` AND is added to `materialize_results.py`; an analysis that exists only in stdout/chat does not exist.

## Entry 67 — 2026-08-28 — Paper draft v11: confirmatory wave integrated; exploratory demotions + A5–A8 disclosure

**New draft:** `paper/FULL-PAPER-DRAFT-BUSINESS-v11_with_figures/` (from audited v10). Two pdflatex passes, exit 0, 32 pages, zero undefined references, zero LaTeX errors.

**Edits:**
1. New Results subsection "Out-of-Sample Confirmatory Replication: The Wave" (sec:wave): Protocol 12 / OSF jg49x design, Table (W1–W7 complete-panel gate outcomes, n = 2,418, 10 families), D52/D53 disclosures, binding upgrade-gate reading (W1/W2/W6 PASS; W3/W4/W5 FAIL — exploratory findings remain exploratory), promo-vector sensitivity note.
2. Exploratory heterogeneity subsection (sec:exploratory-heterogeneity): status declaration updated — forward reference replaced by the gate outcomes; strategic-implication quote relabeled "exploratory — gate FAILED" (kept as hypothesis generator only).
3. Abstract: replication-wave block added (core claims replicate; exploratory findings fail their gates).
4. Contributions: sixth contribution added (pre-registered confirmatory replication wave as a demonstration of gate discipline).
5. Methodology §3.1: two-study framing extended with Protocol 12; **registered-but-unexecuted arms A5/A6/A8 disclosed** (gates never evaluated, arms never executed; A5→Protocol 14, A7→Protocol 13).
6. Summary-of-findings table: wave-replicated row (W1/W2/W6) added; exploratory row split — wave-gated (FAIL) vs persona battery (not wave-tested, D50).
7. Future Directions rewritten: wave item (done) replaced by Protocols 13/14/15 (design authorship, loop control, routing); subtractive refiner / human panel / second domain retained (six items).
8. Limitations: seventh limitation added (wave execution environment: gemini billing fix, kimi Together routing deviation, D52 REML caveat).
9. Code and Data Availability: D54 materialized CSV layer documented.
10. Two new references: Open Science Collaboration 2015 (10.1126/science.aac4716); Camerer et al. 2018 (10.1038/s41562-018-0399-z). Author date stamp 2026-08-28.

**Still open (author decision, Entry 47):** the title. The wave results strengthen the case for a title reflecting the replicated negative-substitution finding; candidates unchanged pending the author's pick.

## Entry 68 — 2026-08-28 — v11 audit against frozen data: five corrections, all numbers verified

Full pass of v11 claims vs frozen artifacts (`results/wave_analysis.json`, `interim2_analysis.json`, `results/cost/cost_effectiveness.json`, `qual2_kappa.json`). Verified accurate: wave gates W1–W7 (all point estimates, p-values, power, ICC range, T-EGR incl. promo sensitivity), abstract figures (d = −0.227/−0.691, 98%/23%, T-EGR 6.15/1.49, κ = 0.824, wave +0.017/+0.075), 64% gap recovery, summary table.

**Corrections made (stale or interim-value carryovers):**
1. "Five contributions follow" → Six (a sixth was added in v11).
2. Marketing wave delta quoted from the 9-family interim (−0.083) → complete-panel value **−0.075**.
3. Decision-register references updated: D1–D39 → **D1–D54** (three occurrences, incl. AI-disclosure "all 39 design decisions").
4. "ten protocols" → **twelve protocols** (two occurrences).
5. Conclusion now cites "this 1,900-run experiment **and its 2,400-run pre-registered replication wave**".

Recompiled: 32 pages, zero errors, zero undefined references.

## Entry 69 — 2026-08-28 — Protocol 13 (Study 3) runner built: `code/study3_design_run.py`; §9 open decisions resolved (D55)

**Code:** `code/study3_design_run.py` — resilient, resumable Study 3 generation runner per author directive (network/credit failure → resume where it stopped). Append-only ledger `runs/logs/study3_ledger.jsonl`; resume skips tasks completed with `final_len > 0`; per-family credit exhaustion logged to `runs/logs/study3_credit_exhaustion.jsonl` and family skipped; solutions in `runs/study3/solutions/`, raw designer JSON in `runs/study3/designs/`; `--build-store` rebuilds the judge_v2-compatible store (`runs/study3/study3_store.json`) idempotently. Local `load_key` copy so the runner never requires judge keys at generation time.

**Dry-run verified:** full plan = **570 tasks** (2 arms × 5 families × 19 confirmatory problems × 3 reps = 57/arm·family); pilot = **40 tasks** (D32 frozen draw Business_Problem_4/8/16/19, 1 rep). Zero API calls made to date.

**Protocol §9 decisions resolved (D55):** invalid design → exclude-and-disclose after ONE repair retry (no fixed-pipeline fallback); fresh design per rep; provider-enforced default sampling params (D27; gpt omits temperature, uses max_completion_tokens + reasoning_effort=low).

**Gate before any generation:** OSF pre-registration of Protocol 13 (adapt `code/osf_register_study2b.py`), then pilot (`--pilot`, ≈ $5), gates G1 (≥90% valid designs + ≥90% completion) and G2 (stop only if D-FRONT < C-T-N by d < −0.30), then the full run. DeepSeek judging only off-peak (weekend = off-peak all day Beijing time); qwen generation gated to UTC 14:00–00:00 inside the runner. Budget envelope ≤ $40.

## Entry 70 — 2026-08-28 — Study 3 pilot COMPLETE: 40/40, gates G1+G2 PASS; runner hardened; full run authorized by gate results

**Execution:** OSF registration `9ukjz` timestamped BEFORE first successful generation (pre-registration failures made zero API calls: import bug → pilot-list KeyError → `DESIGN_PROMPT.format` brace KeyError; all pre-API). Pilot = 40 tasks (4 problems × 5 families × 2 arms × 1 rep; seeded draw 20260828, 4 domains — the registered summary cited stale D32 IDs; corrected to the deterministic re-draw disclosed here and in D55: Business_Problem_6/8/9/12).

**Gates (results/study3_pilot_gates.json, D54):**
- **G1 PASS** — 100% schema-valid designs (0 repair retries, 0 design_failed), 100% completion, all 5 families. Step-count distribution: 3-step ×8, 4-step ×32.
- **G2 PASS** — Novelty vs frozen C-T-N baseline (n=60, mean 3.92): D-FRONT mean 4.067 (d = **+0.392**), D-SELF 3.972 (d = +0.137). Stop-rule was d < −0.30; both arms ABOVE the human-designed baseline. Judging: frozen panel ×3 variants, 360/360, DeepSeek weekend off-peak.

**Runner hardening (author resilience directive):** missing `import os`; stale env `KIMI_API_KEY` shadows fresh .env key → run with `env -u KIMI_API_KEY`; Anthropic system-role hoisting to top-level `system` param; unescaped braces in DESIGN_PROMPT; **step-level checkpointing** (`runs/study3/checkpoints/`) so 5–15-min multi-step tasks survive chunk kills and resume mid-task (design call not re-paid). Two early findings for the paper: frontier designers produce longer pipelines; first pilot signal says model-authored pipelines meet/beat the human baseline.

## Entry 71 — 2026-08-29 — Study 3 instrument v2 (D56): platform-verbatim designer prompt; OSF amendment bwc93; 73 v1 runs archived superseded

**Audit finding (author):** v1 designer diverged from the platform auto-designer (4-step cap vs <8, bespoke prompt vs platform-internal prompt, missing if/while gates, temp default vs 0.3; platform role vocabulary verified non-enforcing in code). **Action:** re-instrumented to platform-verbatim prompt with one disclosed modification (no approval/HITL steps); gate-faithful executor (if/while keyword routing, bounded loops); v1 ledger/solutions/designs/judgments archived as `*_v1_superseded*`; v2 ledger/store paths; OSF amendment registration **bwc93** submitted BEFORE any v2 generation; v11 §3.9 gained an AI-oversight case study paragraph documenting the episode (compiles clean, 32 pp). Next: v2 pilot (40) → G1/G2 → full 570.

## Entry 72 — 2026-08-29 — Pilot v2 complete: 37/40 valid solutions, G2 PASS, G1 amendment filed (639eq); kimi attrition escalated

**Pilot v2 (protocol13-v2, platform-verbatim designer):** gpt 8/8, gemini 8/8, claude 8/8, qwen 8/8 (window-gated, ran at 14:00 UTC), kimi 5/8. Attrition (disclosed): BP6 design_failed (empty designer output ×2), BP8 Moonshot moderation block ×3, BP9 empty polisher output → retry design_failed. **G2 PASS:** D-FRONT Novelty 4.076 (d = +0.42 vs frozen C-T-N 3.92), D-SELF 3.975 (d = +0.14); judging 333/333 (frozen panel, DeepSeek weekend off-peak). **G1 amendment 639eq** filed pre-full-run (D57): moderation blocks/design failures = disclosed attrition. kimi strictly misses even the amended 80% threshold (5/7) — author decision pending; runner proceeds with kimi included. **Fixes shipped during pilot:** anthropic omit_temperature (opus-5 deprecates temperature), kimi k3 fixed-temperature (only 1 allowed), empty-assistant repair guard, empty final-agent output → retriable failure, terminal statuses in planner (design_failed + ≥3 failures stop retrying). Family Novelty means (pilot, small n): kimi 4.62, gemini 4.14, qwen 4.11, claude 3.81, gpt 3.68.

## Entry 73 — 2026-08-30 — STUDY 3 COMPLETE: 544/570 + 26 disclosed attrition; judged 4,896; pre-registered analysis run

**Execution:** full run finished 2026-08-29 23:25 UTC (self-driving driver, 64 workers). Participant flow: gpt 114/114, gemini 114/114, qwen 114/114, claude 113/114 (1 design_failed), kimi 89/114 (21 design_failed — k2.6/k3 empty-or-truncated designer JSON on the platform prompt; 4 failed incl. BP8 moderation block ×3). Moonshot balance suspended the kimi lane twice; resolved by top-ups + D58 reroute of k3 designer to Together.ai. Judging: frozen 3-judge panel ×3 variants, 4,896 judgments, DeepSeek weekend off-peak.

**Pre-registered results (`results/study3_results.json`, `analysis/results/study3_*.csv`, D54):**
- **Contrast A (D-FRONT vs D-SELF, Novelty, paired, Holm):** significant ONLY for claude (Δ=+0.136, t=2.997, p_holm=0.0136, d=0.78). gemini (p=1), gpt (p_holm=0.31), kimi (p=1), qwen (ns) — no general authorship effect.
- **Contrast B (vs frozen human-designed C-T-N):** BOTH arms beat the human baseline in ALL 5 families (D-SELF d=0.15–0.67; D-FRONT d=0.24–1.33). Model-authored pipelines ≥ human default everywhere.
- **Cost/structure:** D-SELF 34.8M tokens vs D-FRONT 24.3M (cheap designers loop more); ~5.3 designed steps, ~6 executed (gate loops); 98.9%/100% of designs include if/while gates.
- **Pooled:** D-FRONT vs D-SELF nearly identical across all 5 dimensions (Novelty 4.03 vs 3.99).
- **Headline:** design authorship is NOT the bottleneck — cheap models designing for themselves match frontier-designed pipelines; both beat the frozen human design. kimi's designer-stage fragility (22% attrition) is the one big cheap-tier disadvantage found.

## Entry 74 — 2026-08-30 — Study 3 contrast vs frontier-solo (F-S-N): orchestration helps weak families, not strong ones

Author-requested comparison (pre-registered F-S-N comparator). Designed cheap-executed pipelines vs frozen frontier-solo (Novelty): POOLED D-SELF d = −0.22, D-FRONT d = −0.05 — parity overall. Heterogeneity is the story: kimi +0.85/+0.74, qwen +0.55/+0.61, gemini +0.46/+0.51 (cheap pipelines BEAT frontier solo), gpt parity (−0.07/+0.13), claude −3.14/−2.84 (opus-5 solo far above any haiku-executed pipeline). Interpretation: pipeline design closes the gap where the frontier-solo ceiling is low; where the frontier model is strongest (claude), solo remains untouchable by cheap orchestration. Saved: results/study3_vs_frontier_solo.json.

## Entry 75 — 2026-08-30 — Full Study 3 vs F-S-N battery: both arms, all 5 dimensions, Holm (50 tests)

`analysis/results/study3_vs_fsn_full.csv`. Key pattern: D-FRONT (frontier-designed, cheap-executed) does NOT rescue the families where cheap pipelines lose to frontier solo — claude D-FRONT still sig. below opus-solo on Novelty (d=−2.84) and Flexibility (−0.78); gemini D-FRONT sig. below flash-pro-solo on Usefulness (−1.41), Elaboration (−1.57), Flexibility (−0.68). kimi D-FRONT beats k3-solo on Novelty (+0.74, p_holm=.013) as does D-SELF (+0.85, p_holm=.006); qwen D-FRONT Novelty +0.61 (p_holm=.049). Conclusion: design authorship cannot compensate for executor capability where the frontier solo ceiling is high; orchestration gains are family-specific and concentrated where the solo frontier is weakest.

## Entry 76 — 2026-08-30 — Study 3 economics table (cost per solution vs quality delta); token-field bug found & corrected

Author-requested decision table: cost/solution (USD, frozen price vector v2026-08-23-wave) and ΔNovelty vs F-S-N per family for F-S-N / D-SELF / D-FRONT. **Correction (D54 audit trail):** first pass under-costed D-SELF/D-FRONT for OpenAI-format providers — the ledger stores provider-native usage fields (`prompt_tokens`/`completion_tokens`), which the inline script misread as Anthropic-style (`input_tokens`/`output_tokens`); Together-hosted k3 is logged as `moonshotai/Kimi-K3`, now aliased to the frozen `kimi-k3` price entry. Fixed and persisted as a versioned script `code/study3_economics.py`; outputs `results/study3_economics.json` + `analysis/results/study3_economics.csv`. F-S-N cost uses the 15/85 input/output split approximation (main ledger stores totals only) and is labeled as such.

Corrected table (cost per completed solution; d = Novelty vs F-S-N):
- **gemini:** F-S-N $0.043 · D-SELF $0.010 (0.24×, d=+0.46) · D-FRONT $0.025 (0.59×, d=+0.51) — cheaper AND better
- **qwen:** F-S-N $0.020 · D-SELF $0.040 (1.99×, d=+0.55) · D-FRONT $0.046 (2.30×, d=+0.61) — better at 2× cost
- **kimi:** F-S-N $0.107 · D-SELF $0.377 (3.53×, d=+0.85) · D-FRONT $0.274 (2.56×, d=+0.74) — better at ~3× cost
- **gpt:** F-S-N $0.180 · D-SELF $0.729 (4.04×, d=−0.07) · D-FRONT $0.512 (2.84×, d=+0.13) — parity at higher cost
- **claude:** F-S-N $0.266 · D-SELF $0.438 (1.65×, d=−3.15) · D-FRONT $0.668 (2.51×, d=−2.84) — more expensive AND much worse → sell solo

Decision rule: T-EGR winner is family-specific — orchestrate gemini (strictly dominant), qwen/kimi (pay ~2–3× for +0.5–0.9 SD novelty), never claude (solo); gpt indifferent → solo on cost.

## Entry 77 — 2026-08-30 — Paper v12: Study 3 section drafted + data-quality audit (judgment dedupe)

**Audit before drafting (author directive):** found 19 duplicate judgment lines in `runs/study3/study3_judgments_v2.jsonl` (judging-retry duplicates on 4 claude solutions; (meta,var2) re-judged up to 7×). Verified the analysis loader keys on (runId, judge, variant) with last-wins overwrite, so all reported statistics were already computed on the deduplicated 4,896 = 544×9 unique judgments; only the `judgments` headline count in `results/study3_results.json` was inflated (4,915) — fixed in `code/study3_analysis.py`, re-run, all contrast/CSV outputs bit-identical.

**v12 (`paper/FULL-PAPER-DRAFT-BUSINESS-v12_with_figures/`, compiles clean, 35 pp):** new Results subsection "Study 3: Who Should Design the Pipeline?" (\cref{sec:study3}) — design + OSF chain (9ukjz→bwc93→639eq), Contrast A authorship table (tab:study3-authorship), Contrast B (beats human design 5/5), vs-F-S-N family contrast + economics decision table (tab:study3-econ), decision rule, key takeaway; abstract gains the Study 3 paragraph; Research Design updated (three studies; A7 disclosure now points to executed Study 3); Summary of Key Findings +2 rows; Discussion decision-framework gains the family-conditional override; Limitations gains an eighth item (kimi designer attrition, single auto-designer instrument, no-HITL scope); Future Directions renumbered (Protocol 13 marked complete; five remaining experiments).

## Entry 78 — 2026-08-30 — Study 3 descriptive family × domain breakdown (no inference, author directive)

Author asked whether family×domain inferential stats add value; advised no (cells of 3–4 problems × 3 reps are underpowered; family already shown to be the moderator, not domain) and produced a **descriptive-only** breakdown instead: `code/study3_by_domain_descriptive.py` → `results/study3_by_family_domain.json` + `analysis/results/study3_by_family_domain.csv` (means and Cohen d vs F-S-N on Novelty, 30 family×domain cells, 3–4 problems each, **no p-values by design**) + heatmap `paper/FULL-PAPER-DRAFT-BUSINESS-v12_with_figures/fig23_study3_family_domain.png`. Descriptive pattern: column (family) stripes dominate — claude loses everywhere (d −2.7…−10.6), qwen wins everywhere (+0.4…+1.8), kimi wins except finance/ops, gemini wins except finance/HR, gpt ~0 everywhere; finance is the weakest domain for 4/5 families. Confirms visually that family, not domain, moderates orchestration gains.

## Entry 79 — 2026-08-30 — Protocols 14/15 superseded (D59); Protocol 16 drafted + REGISTERED (zkm8v); runner built

**D59 (author ruling):** Protocol 14 (loop control) superseded — Study 3 showed loops are universal yet outcomes remain family-determined; residual dose-response question demoted to future work. Protocol 15 (router) superseded — per-family routing snapshot from 49 problems is obsolete-on-arrival as models change; reframed as a product method (cheap-tier benchmarking-as-routing), not an experiment. Banners added to both protocol files.

**Protocol 16 (D60, OSF `zkm8v` — timestamped BEFORE any generation; the OSF API returned a transient 502 on submit but the registration succeeded, id recovered from the draft link):** Study 3 confirmatory replication — D-SELF only (pre-declared drop of D-FRONT per Study 3 Contrast A), 30 wave problems × 3 reps × 5 core families = 450 planned, comparator = frozen wave F-S-N (zero new frontier-solo generation), binding gates R1–R5. Runner `code/study3conf_run.py` (wraps Protocol-13 v2 instrument; own ledger/tag). qwen deferred to its discount window (author directive); first wave = 4 families × 90 = 360 runs, pilot of 16 (seeded draw: Fresh_Case_10/16/22/12, 4 distinct domains) precedes the full run.

## Entry 80 — 2026-08-30 — Protocol 16 pilot COMPLETE 16/16 (G1 pass); artifact-hygiene fix

Pilot (seeded draw Fresh_Case_10/16/22/12, 4 domains × 4 families): 16/16 completed, 0 design_failed — G1 feasibility passes per D57 rule (kimi 4/4 here, small n). **Audit fix during pilot:** the Protocol-13 runner had solutions/designs/checkpoints paths hardcoded to `runs/study3/`; Protocol-16 pilot artifacts initially mixed into Study-3 dirs. Parameterized (`SOLUTIONS_DIR`/`CKPT_DIR`/`DESIGNS_DIR`/`PROTOCOL_ID`), migrated the 16 pilot artifacts to `runs/study3conf/`, rebuilt `study3conf_store.json` (16 runs), verified Study-3 store intact (544 runs). Ledger `runs/logs/study3conf_ledger.jsonl`. Next: full run, 360 tasks (4 families × 90; qwen deferred to window per D60).

## Entry 81 — 2026-08-31 — Protocol 16 analysis script FROZEN + hash-locked BEFORE judging

`code/study3conf_analysis.py`, SHA-256 `478b3a6bc9d93d97153a90ca72b7297c627e887b9b4b14f6df4078f84095c45e`. Implements gates R1–R5 exactly as registered (OSF zkm8v): problem-level Welch tests of D-SELF vs frozen wave F-S-N on Novelty, normal-approx one-sided p (same convention as Study 3), R4 gpt TOST via 90% CI on d within ±0.30, headline = R1∧R2∧R3∧R5. **Audit before lock (author directive):** (1) fixed empty-family crash + zero-variance division guards; (2) verified judgment dedupe (last-wins per run×judge×variant) identical to Study 3; (3) verified comparator completeness — wave F-S-N judged coverage gpt/claude/gemini/qwen 60/60, kimi 82/90 runs but all 30 problems have ≥1 judged rep (problem-level comparator complete, R1 unaffected); (4) smoke-tested loaders on frozen wave data only — no contact with Protocol-16 outcome data. Outputs on run: results/study3conf_results.json + analysis/results/study3conf_gates.csv (D54).

**Generation state at lock time:** gemini 90/90, claude 89/90, gpt 88/90, qwen 89/90, kimi 82/90 + 5 disclosed attrition; 3 kimi tasks still running. Judging has NOT started; no Protocol-16 outcome analysis has been performed.
