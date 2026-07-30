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

---

## Maintenance rule
Every future design or analysis decision MUST be appended here (topic-organized) and to
`MANIFEST.md` (chronological) **with its academic grounding at the time it is made**.
These two files are source material for the paper's Methodology section.
