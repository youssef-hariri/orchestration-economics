# Design Decisions Register — academic & statistical grounding

Companion to `MANIFEST.md` (chronological provenance log). This register organizes every
design decision **by topic** with its rationale and academic grounding, written to be
reusable in the paper's Methodology section. Cross-references: RESEARCH-PAPER-PLAN.md
(§ numbers), `config/experiment_config.json`.

Format per decision: **Decision → Rationale → Academic grounding → Implemented in**.

---

## D1. 2×2×2 within-family factorial design (§4.1)
- **Decision:** Tier (Frontier vs Cheap sibling) × Structure (Solo vs 3-step Team) × Persona (None vs Loaded), fully crossed within 5 model families; family as a blocking factor.
- **Rationale:** A factorial design estimates all three main effects and their interactions from the same runs (efficiency), and blocking by family converts the frontier-vs-cheap comparison into matched pairs — every frontier is compared against a cheap model from its *own* family, removing vendor/architecture confounds.
- **Grounding:** Factorial efficiency and blocking: Fisher (1935) *The Design of Experiments*; Montgomery (2017) *Design and Analysis of Experiments*. Matched-pair logic for confound control: Shadish, Cook & Campbell (2002).
- **Implemented in:** plan §4.1; config `design`, `tiers.families`, `tiers.cells`.

## D2. Model-homogeneous teams
- **Decision:** All 3 agents in a team run use the SAME model; only persona/role prompts differ.
- **Rationale:** If teams mixed models, any team-vs-solo difference would confound orchestration with model diversity. Homogeneity attributes the Structure effect to orchestration alone; the Persona effect to personas alone (H3).
- **Grounding:** Single-variable manipulation / ceteris paribus experimental logic (Shadish, Cook & Campbell 2002); mirrors the isolation strategy of Paper 2 (*Doing More with Less*, DOI 10.5281/zenodo.19533619), which varied persona while holding model constant.
- **Implemented in:** plan §4.1 design principles; config `design.team_rule`.

## D3. Stochasticity is sampled, not suppressed (§4.8)
- **Decision:** Generation temperature 0.7 with repeated runs per cell; never temp 0 for generation.
- **Rationale:** LLM output is a draw from a conditional distribution; temp-0 collapses the distribution to a single (still not perfectly deterministic) point and hides output variance that managers actually face. Repetitions turn stochasticity into measurable within-cell variance.
- **Grounding:** Paper 4 (*Team Composition Paradox*, DOI 10.5281/zenodo.17490945) used temp 0 and lists it as a limitation; Papers 1–2 sampled at temp 1 / 0.7. Treating stimuli-level randomness as data rather than noise follows the random-effects tradition (Clark 1973; Baayen, Davidson & Bates 2008).
- **Implemented in:** plan §4.8(1); config `generation.temperature`.
- **Amended by D27 (2026-07-31):** temperature revised from 0.7 to 1 (provider-forced; see D27). The core principle — sampled stochasticity with repeated runs, never temp 0 — is unchanged.

## D4. Judge every repetition independently; ensemble only at score level (§4.8)
- **Decision:** Each repetition is a separate solution scored by all 9 judge calls; responses are NEVER merged before judging; the solution score = mean of its 9 judge scores.
- **Rationale:** Merging responses before judging would destroy the variance needed for both mean-effect inference and the Consistency DV, and would create an artifact (a "merged text") that no condition actually produced. Score-level aggregation preserves comparability with Papers 1–2.
- **Grounding:** Identical protocol to Paper 1 (*LLM-Creativity*, DOI 10.5281/zenodo.17407392: "Each of the 6,375 generated business solutions was assessed by all five LLMs") and Paper 2 (9 ratings per response). Aggregating ratings, not stimuli, is standard in judgment research (Shrout & Fleiss 1979).
- **Implemented in:** plan §4.8(2–3); config `judging.judge_each_repetition_independently`, `judging.ensemble_level`.

## D5. Reps = 3; generalization power from stimuli, not repetitions (§4.4)
- **Decision:** 3 repetitions per cheap cell (2 per frontier cell), with power sourced from 30 problems × 5 families.
- **Rationale:** Under crossed random-effects designs, power to generalize across stimuli is driven primarily by the *number of stimuli*, not replicates per stimulus; rep count beyond 2–3 yields sharply diminishing power returns (~2–4% for 3→5 reps) at +67% generation cost, because within-cell noise is already averaged over 9 judge scores.
- **Grounding:** Westfall, Kenny & Judd (2014, JEP:General) power analysis for designs with sampled stimuli; Judd, Westfall & Kenny (2012, JPSP) treating stimuli as random factors.
- **Implemented in:** plan §4.4; config `generation.reps_*`.

## D6. 30 main problems, domain-stratified 6×5 (§4.3)
- **Decision:** Expand from 15 to 30 problems, stratified as 6 business domains × 5 problems (strategy, marketing, operations, HR, finance, product innovation), pre-registered in `domain_map.json`.
- **Rationale:** Problems are the sampling universe over which findings generalize ("business problems"), so they must be treated as sampled stimuli with adequate cluster count (≥30) and domain coverage; 5 problems per domain makes the H2 domain moderator confirmatory rather than exploratory.
- **Grounding:** The language-as-fixed-effect fallacy (Clark 1973); stimulus sampling requirements (Westfall et al. 2014); stratified sampling for moderator estimation (Shadish, Cook & Campbell 2002). Precedent: Paper 1 used 15 problems — this doubles the stimulus sample while retaining the validated instruments.
- **Implemented in:** plan §4.3; `data/problems/business_problems_domain_15.json`, `data/problems/domain_map.json`.

## D7. 5-rep Consistency slice on one family (§4.1, §4.6)
- **Decision:** The single pre-registered special-arm family runs 5 reps (instead of 3) in its four cheap cells; the Consistency DV (within-cell SD of Novelty) is confirmatory only there.
- **Rationale:** An SD estimated from n=3 draws has sampling error ≈52% of its value (χ-distribution of the sample SD); n=5 reduces it to ≈38%. Boosting reps only where output *reliability* is the estimand is the cost-efficient allocation; mean effects everywhere else need only 3 reps (D5).
- **Grounding:** Sampling distribution of the standard deviation (χ²/χ theory; e.g., Ahn & Fessler 2003 technical note); optimal design principle of allocating observations to the estimand that needs them (Montgomery 2017).
- **Implemented in:** plan §4.1 note, §4.6; config `tiers.consistency_slice`.

## D8. Mixed-effects models; pseudo-replication fix (§4.7)
- **Decision:** Primary inference = mixed model with Tier × Structure × Persona fixed effects and crossed random effects (problem, family, solution, judge). Effect sizes reported on solution-level ensemble scores.
- **Rationale:** Judge×variant rows are repeated measurements of the same solution, not independent observations. Paper 2 treated them as independent (n≈25,300), inflating significance — correcting this is an explicit methodological contribution of this study.
- **Grounding:** Pseudo-replication (Hurlbert 1984, Ecological Monographs); crossed random effects for subjects-and-stimuli designs (Baayen, Davidson & Bates 2008, JML); maximal-but-identifiable random-effects structure (Barr et al. 2013, JML).
- **Implemented in:** plan §4.7; config `analysis.units`.

## D9. Judge ensemble: 3 cheap judges × 3 prompt variants, families disjoint from generators
- **Decision:** Judges = Mistral Small, GLM (Zhipu), Llama-3.3-70B — no family overlap with the 5 generator families; one invariant ensemble for all arms; blinded, randomized presentation order.
- **Rationale:** LLM judges systematically prefer outputs from their own family (self-preference bias); disjointness removes it. Ensemble-of-judges with prompt variants averages out idiosyncratic prompt sensitivity. Measurement invariance requires the same instrument across all conditions.
- **Grounding:** Self-preference/self-recognition bias in LLM judges (Panickssery, Bowman & Feng 2024, NeurIPS); LLM-as-judge validity and position bias (Zheng et al. 2023, MT-Bench); cheap-ensemble adequacy demonstrated by Paper 2's Fleiss κ = 0.68 on Novelty.
- **Implemented in:** plan §4.2 judges; config `tiers.judges`, `judge_disjointness_rule`, `judging.blinding`.

## D10. Judge prompts frozen at preregistration
- **Decision:** The 3 proven judge prompt variants from persona-model-fit are reused verbatim and never redesigned mid-study.
- **Rationale:** Changing the measurement instrument mid-study destroys comparability and, empirically, reliability: Paper 1 documents two prompt-"optimization" attempts that collapsed inter-rater κ to ≈0.
- **Grounding:** Own prior evidence (Paper 1, DOI 10.5281/zenodo.17407392); instrumentation threat to validity (Shadish, Cook & Campbell 2002); preregistration of measures (Nosek et al. 2018, PNAS).
- **Implemented in:** plan §4.8(6); config `judging.judge_prompts_frozen`; `evaluation/judge_prompts/`.

## D11. Dual inter-rater reliability: Fleiss' κ AND ICC(2,k)
- **Decision:** Report both statistics per dimension on ALL solutions.
- **Rationale:** κ (categorical agreement) preserves comparability with Paper 2; ICC(2,k) (consistency of the mean of k raters) matches the actual estimand — the 9-score mean — and was Paper 1's metric. Full-sample computation avoids the subset limitation of Paper 1 (35 items).
- **Grounding:** Fleiss (1971); Shrout & Fleiss (1979) ICC selection guidelines; McGraw & Wong (1996).
- **Implemented in:** plan §4.7; config `analysis.irr`.

## D12. Estimation-first statistics: effect sizes + bootstrap CIs + FDR + Bayes factors
- **Decision:** Cohen's d with 5,000-resample percentile bootstrap CIs (seed 42); Welch's t throughout; Benjamini–Hochberg FDR across the contrast family; JZS Bayes factors (exact, via pingouin) alongside Paper 2's Rouder approximation for comparability; post-hoc power reported.
- **Rationale:** Continuation of the exact stack in `stats_with_anlysis.py` (persona-model-fit repo) for cross-paper comparability, with two upgrades: standardized Welch's t (Paper 2 mixed Student's/Welch's) and exact JZS BF (Paper 2 used exp(−t²/2)√(n/2)).
- **Grounding:** Estimation statistics (Cumming 2014, Psych Science); bootstrap CIs (Efron & Tibshirani 1993); Welch (1947) and its default recommendation (Delacre et al. 2017); Benjamini & Hochberg (1995, JRSS-B); JZS priors (Rouder et al. 2009, PBR).
- **Implemented in:** plan §4.7; config `analysis.inherited_stack`; `analysis/stats.py` (Phase 4).

## D13. Robustness battery
- **Decision:** Isolation Forest outlier sensitivity (contamination 0.1, seed 42); 80/20 split-half by problem; leave-one-judge-out; leave-one-family-out; mean-vs-median sensitivity; fresh-10 out-of-sample subset.
- **Rationale:** Inherited from `stats_with_anlysis.py` (Paper 2 achieved mean-vs-median r = 0.997); leave-one-out at the *judge* and *family* level tests that no single rater or vendor drives conclusions.
- **Grounding:** Isolation Forest (Liu, Ting & Zhou 2008, ICDM); influence/sensitivity analysis tradition (Belsley, Kuh & Welsch 1980); multiverse-style robustness reporting (Steegen et al. 2016).
- **Implemented in:** plan §4.7; config `analysis`.

## D14. Fresh post-cutoff cases as contamination control
- **Decision:** 10 author-drafted 2026 cases, analyzed strictly as an out-of-sample robustness set (never pooled into the domain grid).
- **Rationale:** Benchmark problems predating model training cutoffs risk memorization; replicating key contrasts on post-cutoff material bounds the contamination threat. Keeping the set separate preserves its value as an independent replication.
- **Grounding:** Data-contamination literature (Sainz et al. 2023, EMNLP Findings; Zhou et al. 2023 "Don't Make Your LLM an Evaluation Benchmark Cheater"); out-of-sample replication logic (Open Science Collaboration 2015). The 100-problem persona-model-fit set was excluded on exactly this ground (DeepSeek-adjacent material).
- **Implemented in:** plan §4.3; `data/problems/fresh_business_cases_10.json`.

## D15. Cost-matched comparison (A6) and T-EGR (§4.5)
- **Decision:** The killer contrast holds *dollars* constant: the best frontier model gets the same budget as the pooled median cost of the cheap persona team. Economic DV = T-EGR = (Novelty ratio)/(Cost ratio).
- **Rationale:** "Teams beat a frontier model" is trivial if the team costs more; equal-cost framing is the managerially meaningful decision problem (orchestrate minis vs buy the flagship) and this study's core positioning gap.
- **Grounding:** Cost-controlled evaluation gap in multi-agent LLM literature (positioning vs Wang et al. 2024 Mixture-of-Agents; Stanford 2026 single-agent result — genuine equipoise); EGR introduced in Paper 2, extended here to team level.
- **Implemented in:** plan §4.5; config `tiers.frontier_cost_matched_A6`, `economic_dv`.

## D16. Pre-registration and frozen protocol
- **Decision:** Hypotheses, contrasts, selection rules (A6 baseline, F-T family rule, special-arm family), prompts, and the full randomized run ledger are frozen and committed (GitHub tag / OSF) BEFORE the main run.
- **Rationale:** Eliminates HARKing and analytic flexibility; selection rules stated as *rules* (e.g., "highest mean Novelty in F-S-N") rather than post-hoc choices remain confirmatory.
- **Grounding:** Nosek et al. (2018, PNAS) preregistration revolution; Simmons, Nelson & Simonsohn (2011) researcher degrees of freedom; Wagenmakers et al. (2012) purely confirmatory research.
- **Implemented in:** plan §4.7 rigor package, §4.9 ledger; `PROTOCOL.md` (Phase 1 tag).

## D17. Execution resilience: preregistered run ledger with idempotent resume (§4.9)
- **Decision:** `runs/ledger.csv` — complete randomized, arm-interleaved run list (seed 42) committed at preregistration; statuses PENDING/RUNNING/DONE/FAILED_RETRYABLE/FAILED_PERMANENT; 3 retries (5/30/120 s backoff); ≤4 concurrent; `parsed_ok` gate so failures are re-run, never scored.
- **Rationale:** (a) Interleaving makes any interruption (credit outage, disconnect) ignorable for internal validity — no arm is systematically run at a different time than another; (b) idempotent resume makes the experiment restartable without human bookkeeping; (c) the parsed_ok gate fixes Paper 4's documented flaw where API error strings scored 0 and silently consumed budget.
- **Grounding:** Randomization/interleaving against temporal confounds (provider model drift — Chen, Zaharia & Zou 2023 "How is ChatGPT's behavior changing over time?"); missing-data ignorability under randomized interruption (Rubin 1976); Paper 4's runner as negative precedent.
- **Implemented in:** plan §4.9; config `execution_resilience`; DATA-DICTIONARY `runs/ledger.csv`.

## D18. Personas and role-congruence (H5)
- **Decision:** Reuse the 3 validated cultural personas verbatim; pre-registered congruent persona→role mapping (Culture_5→Builder, Culture_Expert→Critic, Culture_11→Refiner); A8 shuffles the mapping.
- **Rationale:** Verbatim reuse = validated instruments and construct continuity across the research program; the congruence contrast isolates person-role *fit* from persona *presence*.
- **Grounding:** Persona effects and best-persona evidence (Paper 2: Culture_5 d = 0.908); team role theory (Belbin 1981); person-role fit / contingency theory (Lawrence & Lorsch 1967); congruence hypotheses in composition research (Bell 2007, JAP meta-analysis).
- **Implemented in:** plan §4.1 persona tables; `data/personas/cultural_personas.json`; config `persona_role_mapping_congruent`.

## D19. Oracle-portfolio analysis (exploratory)
- **Decision:** Compute the per-problem best-cell "oracle router" as the attainable upper bound; report the A7-adaptive-vs-oracle gap.
- **Rationale:** Paper 4 found the union of conditions solved +42.9% more than any single condition — heterogeneity across problems is the value pool that adaptive routing (A7, Kimi V3 designer) tries to capture; the oracle quantifies how much of that pool is captured.
- **Grounding:** Oracle/upper-bound analysis in model-routing and ensemble literature (e.g., Jiang et al. 2023 LLM-Blender); portfolio framing from Paper 4's Strategic Selector.
- **Implemented in:** plan §4.7; config `analysis.oracle_portfolio`.

## D20. Computational reproducibility: all executed code is committed (code availability)
- **Decision:** Every script created and run at any phase (ledger generation, run execution, judging, aggregation, statistics) is committed to `code/` or `analysis/` BEFORE its outputs are trusted; pinned dependencies (`requirements.txt`), seed 42 everywhere, all parameters read from `config/experiment_config.json`, scripts idempotent, secrets only via environment variables. No result may exist in the repository without the committed code that produced it.
- **Rationale:** The claim "anyone can re-run this experiment" requires the full computational chain, not just data: code + config + data + environment. This also protects the author — reviewers and replicators can audit exactly what was executed, and the paper's Code Availability statement becomes a pointer to the repo rather than a promise.
- **Grounding:** Reproducible computational research standards (Peng 2011, Science; Sandve et al. 2013, PLOS Comp Bio "Ten Simple Rules for Reproducible Computational Research"; Stodden et al. 2016, Science — enhancing reproducibility for computational methods); TOP guidelines Level II–III code transparency (Nosek et al. 2015, Science). Precedent: persona-model-fit and OODA-Belbin repos already publish their execution code (`code/stats_with_anlysis.py`, `API_model_files/`).
- **Implemented in:** `code/README.md` (script inventory + conventions); repo README Reproduction section; MANIFEST Entry 6.

## D21. Cost accounting under time-of-day provider discounts
- **Decision:** Primary cost analysis (T-EGR) uses **pinned standard prices** frozen at Phase 0 (time-invariant per model); the actual paid price under off-peak discounts is recorded per run in the ledger (`started_at_utc`, `in_discount_window`, `paid_price_usd`) and analyzed only as a **sensitivity analysis**. All runs execute inside one fixed window — 14:00–00:00 UTC (22:00–08:00 Beijing) — which hits the Qwen off-peak discount and fully avoids both DeepSeek peak-surge windows (09:00–12:00, 14:00–18:00 UTC+8).
- **Rationale:** Time-varying prices would make the economic DV depend on *when* a run happened to execute — an arbitrary nuisance variable that confounds the frontier-vs-cheap cost contrast and destroys reproducibility (a replicator running at a different hour would get different T-EGR values). Pinning standard prices makes cost a deterministic function of tokens; running inside one fixed window makes the paid-price sensitivity interpretable (all runs face the same discount regime) and minimizes real spend. Discount windows are promotional and revocable, so they cannot anchor the primary analysis.
- **Grounding:** Standardization of measurement conditions / control of nuisance variables (Montgomery 2017, ch. 2; blocking-and-holding-constant logic); reproducible cost reporting requires deterministic pricing rules (Stodden et al. 2016); sensitivity analysis as robustness practice (Thabane et al. 2013, BMC Med Res Methodol).
- **Implemented in:** `config/model_registry.json` (`execution_window`, per-provider `discount_window`/`surge_window`); ledger columns (Phase 1).

## D22. Phase 0 model pins — Eastern families, judges, designer, fallback
- **Decision:** Pin (a) **kimi**: frontier `kimi-k3` ($3/$15 per 1M), cheap `kimi-k2.6` ($0.95/$4); (b) **qwen**: frontier `qwen3.7-max-2026-06-08` (pinned $1.25/$3.75), cheap `qwen3.7-plus-2026-05-26` (pinned $0.32/$1.28) — **dated snapshots**, not moving aliases; (c) **judges** all via Together.ai: `mistralai/Mistral-Small-24B-Instruct-2501`, `zai-org/GLM-4.7`, `meta-llama/Llama-3.3-70B-Instruct-Turbo`; (d) **designer** (A7): `kimi-k3` at temperature 0; (e) **fallback family**: `deepseek-v4-pro`/`deepseek-v4-flash`. GPT/Claude/Gemini pins pending API keys. Every pin verified to exist on the author's accounts by `code/pin_models.py` (free /models listings).
- **Rationale:** Dated snapshots guarantee the same weights serve every run and any future replication (moving aliases like `qwen3.7-max` silently re-point). Qwen cheap sibling `3.7-plus` is chosen over the cheaper `flash` because it shares the *same generation* as the frontier, keeping the tier contrast a clean within-generation price contrast. Judges on one aggregator (Together) give uniform API semantics, one rate-limit domain, and API-reported per-token prices, while preserving the D8 generator/judge family disjointness ({mistral, zhipu, meta} ∩ {openai, anthropic, google, moonshot, alibaba} = ∅). GLM-4.7 is picked over GLM-5.x as the judge because judges need validated cheap capacity, not frontier reasoning — and its $0.45/$2.0 pricing keeps the 9-score ensemble affordable at ~13,000 judgments.
- **Grounding:** Version pinning as a computational-reproducibility requirement (Sandve et al. 2013, Rule 4: archive exact versions; Stodden et al. 2016); construct validity of the tier factor requires within-family, within-generation price contrast (Shadish, Cook & Campbell 2002, ch. 3); instrument stability for raters (frozen judge models = frozen instrument, cf. D9/D10).
- **Implemented in:** `config/model_registry.json`; `code/pin_models.py` (verification, all PASS 2026-07-30); `config/experiment_config.json` tiers/judges/designer to be synced at freeze.

## D23. Token-invariant cost accounting: cost = tokens × versioned price vector
- **Decision (by author):** The ledger stores **tokens** (`input_tokens`, `output_tokens` from each API's `usage` field) as the invariant measured quantity — required non-null before a run is `DONE`. Dollar cost is never stored as an observed number; it is always **recomputed** as tokens × `config/price_vector.json`, a versioned, swappable file frozen at preregistration (v2026-07-30). Robustness panel: (a) T-EGR recomputed under alternative price vectors; (b) a price-free token-efficiency ratio (Novelty per 1K output tokens) reported with the cross-family tokenizer caveat.
- **Rationale:** Prices change constantly; tokens do not. Splitting the physical quantity from the price lens makes every economic figure exactly re-derivable by anyone, at any later date, under any price regime — one file swap re-prices the whole study. Raw token counts alone cannot replace dollars: tokenizers differ across families and the cheap-team arm deliberately spends more tokens at lower unit price, which is the very effect under study; dollars net those forces.
- **Grounding:** Separation of measurement from valuation parallels quantity/price index decomposition in economics (Diewert 1976, superlative index numbers); reproducibility requires deterministic derivation chains from raw data (Sandve et al. 2013, Rule 6: avoid manual result manipulation; Peng 2011); multiverse/robustness analysis across analytic choices (Steegen et al. 2016, Perspectives on Psychological Science).
- **Implemented in:** `config/price_vector.json`; `model_registry.json` `_purpose` (analysis authority note); ledger schema (Phase 1: token columns required); supersedes the paid-price emphasis of D21 — D21's execution-window and discount-sensitivity logic remains, but the primary chain is now tokens × frozen vector.

## D24. Phase 0 model pins — Western families (completes D22)
- **Decision:** Pin (a) **gpt**: frontier `gpt-5.6-sol` ($5/$30), cheap `gpt-5.6-luna` ($1/$6) — the 5.6 family is an explicit same-generation size ladder (Sol > Terra > Luna); (b) **claude**: frontier `claude-opus-5` ($5/$25), cheap `claude-haiku-4-5-20251001` ($1/$5, dated snapshot); `claude-fable-5` ($10/$50, Mythos-class) excluded as an above-flagship premium tier; Sonnet 5 rejected as sibling (mid-tier; intro pricing expires 2026-09-01); (c) **gemini**: frontier `gemini-3.1-pro-preview` ($2/$12), cheap `gemini-3.1-flash-lite` ($0.25/$1.50, GA, same 3.1 generation) — preview risk flagged with preregistered fallback `gemini-2.5-pro`. All verified on the author's accounts (`pin_models.py`, 16/16 PASS).
- **Rationale:** Frontier construct = each family's *mainline flagship* (excluding above-flagship premium tiers like Fable/Mythos and ‘pro/reasoning-max’ SKUs) so the tier contrast is comparable across all five families; cheap sibling = the family's current cheap tier, same-generation where the provider offers one (gpt, qwen, gemini), nearest-current otherwise (claude, kimi). Price ratios: gpt 5×, claude 5×, gemini 8×, kimi ~3.6×, qwen ~3.4× — heterogeneity noted; the mixed model's family random effect absorbs family-level cost-ratio differences, and T-EGR is computed within-family before pooling.
- **Grounding:** Same as D22 (Sandve et al. 2013 Rule 4 version pinning; Shadish, Cook & Campbell 2002 construct validity); cross-classified comparability requires a uniform operational definition of the ‘frontier’ level across families (Montgomery 2017, factor-level definition).
- **Implemented in:** `config/model_registry.json` (all TO_PIN resolved); `config/price_vector.json`; `config/experiment_config.json` tiers/judges/designer synced.

---

## D25. Main problem set approved (Business_Problem_16–30)
- **Decision (by author, 2026-07-30):** The 15 new domain-stratified problems (Business_Problem_16–30, `data/problems/business_problems_domain_15.json`) are approved as drafted. The 30-problem main set (original 15 + new 15, 6 domains × 5) is content-final; it freezes at the preregistration tag. Domain tags for the original 15 (`domain_map.json`) remain the only problem-related item pending author confirmation.
- **Academic grounding:** Approval completes the stimulus-sampling requirement (Westfall, Kenny & Judd 2014 — ≥30 problem-level clusters) and makes H2 domain moderation confirmatory (6 × 5 balanced grid).

## D26. No human validation panel — LLM-judge-only measurement
- **Decision (by author, 2026-07-30):** There will be NO human raters. Phase 3 (blind human panel, stratified 10% sample, 2 raters, human–AI correlation) is removed from the execution plan.
- **Academic grounding / mitigation strategy (in lieu of a human panel):**
  - Instrument continuity: the 3 judge prompt variants are reused verbatim from Papers 1–2, where the same instrument produced the reported reliability; prompts are never redesigned (Paper 1's two optimization attempts collapsed κ to ≈0).
  - Literature support for LLM-judge validity at ensemble scale: *Judge's Verdict* (arXiv:2510.09738, 54 judges vs human); Badshah 2025 (Fleiss' κ for judge–human agreement).
  - Internal reliability reported in full: Fleiss' κ AND ICC(2,k) per dimension on ALL solutions (9 ratings each); leave-one-judge-out robustness; judge families disjoint from all generator families (mistral/zhipu/meta vs openai/anthropic/google/moonshot/alibaba); verbatim Paper 1 blinding instruction.
  - **Stated explicitly as a limitation** in the paper (§5 item 7): construct validity rests on prior instrument validation and judge-ensemble agreement, not a fresh human panel; human validation listed as future work.
- **Consequence:** §4.6 Measures table, §5 Method/Limitations, §6 Phase 3, and `experiment_config.json` updated; budget/time freed (~1 week, panel logistics).

## D27. Generation temperature 1 for ALL families (provider-forced deviation from 0.7)
- **Decision (by author, 2026-07-31):** Generation temperature is set to 1 uniformly across all 30 fixed pipelines and all 5 families, replacing the pre-registered 0.7.
- **Trigger (empirical, logged):** Production smoke tests returned HTTP 400 from two of five family APIs at temp 0.7 — Moonshot kimi-k3/k2.6 ("invalid temperature: only 1 is allowed for this model") and OpenAI gpt-5.6-sol/luna ("'temperature' does not support 0.7 with this model. Only the default (1) value is supported"). Both are hard API-side policies; no platform-side workaround exists. claude/gemini/qwen accepted 0.7.
- **Alternatives considered:** (a) per-family temperature (0.7 where allowed, 1 where forced) — rejected: introduces a family-confounded generation-parameter difference into every cross-family comparison; (b) dropping the gpt and kimi families — rejected: loses 12/30 pipelines and 2/5 families, crippling the family-as-block design.
- **Rationale for uniform temp=1:** holding the generation parameter constant across all families preserves ceteris paribus for cross-family contrasts (Shadish, Cook & Campbell 2002); within-family contrasts are unaffected either way since temperature never varies within a family. Temp 1 is the provider default for the newest frontier models and matches Paper 1's sampling regime (Papers 1–2 sampled at temp 1 / 0.7 — see D3 grounding). D3's core principle (sampled stochasticity, repetitions as the stochasticity sample, never temp 0) is fully retained.
- **Reporting obligation:** the paper's Method section MUST report this as a documented deviation from the pre-registered value, with the API error messages as evidence that the setting was externally forced, not researcher-chosen post hoc.
- **Implemented in:** all 30 production pipelines (projects 13–42) via `code/apply_d27_temp1.mjs`; registry `d27` block; config `generation.temperature`; plan §4.8(1).

## D28. Generation max_tokens 8192 for ALL families (was 2048; empty-output artifact)
- **Decision (by author, 2026-07-31):** Generation `max_tokens` raised from the pre-registered 2048 to 8192, uniformly across all 30 fixed pipelines and all 5 families.
- **Trigger (empirical, logged):** In the Phase 0 smoke test (30/30 runs completed), the two kimi team cells (oe-kimi-C-T-N run 42, oe-kimi-C-T-P run 43) completed with normal token counts but an EMPTY final response. Root cause isolated experimentally: kimi's hidden reasoning tokens count against the completion budget — kimi-k2.6 solo at maxTokens=100 returned empty content (run 52); the identical prompt at maxTokens=8192 returned a full 8,532-char response (run 53). Team-cell contexts (builder+critic outputs) induce enough reasoning to exhaust 2048 before any visible text.
- **Alternatives considered:** (a) kimi-only raise — rejected: family-confounded budget difference; (b) keep 2048 — rejected: kimi team cells would systematically produce empty solutions, destroying two cells of the factorial.
- **Rationale for uniform 8192:** the cap is unobservable to the model, so raising it cannot change generation behavior except by removing truncation/empty-output artifacts; cost is still measured (not capped) — `agentRuns.tokensUsed` remains the cost DV, and reasoning tokens ARE genuine cost that the economics analysis should capture. Uniformity preserves cross-family ceteris paribus (same logic as D27).
- **Reporting obligation:** documented deviation from the pre-registered 2048, reported in Method alongside D27; the kimi empty-output artifact and its isolation procedure belong in the Method's pilot/smoke-test paragraph.
- **Implemented in:** all 30 production pipelines via `code/apply_d28_maxtokens.mjs`; registry `d28` block; config `generation.max_tokens` (+note); plan §4.4 cost controls.

## Maintenance rule
Every future design or analysis decision MUST be appended here (topic-organized) and to
`MANIFEST.md` (chronological) **with its academic grounding at the time it is made**.
These two files are source material for the paper's Methodology section.
