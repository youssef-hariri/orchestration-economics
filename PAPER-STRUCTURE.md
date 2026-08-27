# Paper Structure — The Economics of Orchestration

**Version:** v2 (2026-08-07) · **Status:** author review
**Structural template:** the author's own published style, extracted from
`.paper-research/paperB.txt` (*Doing More with Less*, DOI 10.5281/zenodo.19533619)
and `paperA.txt` (*LLM-Creativity*, DOI 10.5281/zenodo.17407392):
numbered sections (1 Introduction, 2 Literature Review, 3 Methodology,
4 Results, 5 Discussion, 6 Limitations, 7 Future Directions, 8 Conclusion),
funnel introduction with numbered contributions and a roadmap paragraph,
Literature Review as themed streams with an integration paragraph,
Methodology split into Design / Apparatus / Measurement / Statistics /
Validity / Availability, Results subsections each ending in a **Key Takeaway**.
**Literature rule:** only references with verified DOIs (register at bottom;
PENDING-VERIFY items excluded from the draft until confirmed).

**Working title:**
"The Economics of Orchestration: When Cheap Multi-Agent Pipelines Substitute
for Frontier Models — and When They Do Not"

---

## Abstract (structure, ~250 words, 5 sentences blocks)

1. Context + gap: orchestration of cheap models is claimed to substitute for
   frontier models, but no cost-matched pre-registered test exists.
2. Design: 2 (tier) × 2 (structure) × 2 (persona) factorial, 5 model families,
   19 confirmatory business problems (30 total; 11 pilot excluded per pre-registration),
   1,900 runs, blinded 3-judge × 3-variant LLM panel,
   token-invariant cost accounting (frozen price vector).
3. Study 1: structure substitutes for tier only at the cheap end (C-S-N = 98%
   of frontier quality at 23% of cost); persona cells Pareto-dominated.
4. Study 2: a $0.002 refinement pass recovers 60–64% of the frontier gap and
   ties the weakest frontier, but never wins; qualitative coding (κ = 0.824)
   shows orchestration buys coverage, the frontier wins on density.
5. Economics + contributions: stable Pareto frontier, T-EGR up to 8.6 for
   cheap solo vs 1.0 baseline; practitioner contingency rules.
6. **Keywords:** LLM Orchestration, Multi-Agent Pipelines, Cost-Performance
   Analysis, LLM-as-a-Judge, T-EGR, Pre-registration.

## List of Abbreviations (table)

| Abbr | Definition |
|---|---|
| CTP | cheap team with persona |
| EGR / T-EGR | (Tiered) Efficiency Gain Ratio |
| FSN | frontier solo, no persona |
| ICER | incremental cost-effectiveness ratio |
| IRR | inter-rater reliability |
| LLM | large language model |
| P0–P3 | pre-registered protocol numbers |
| SESOI | smallest effect size of interest |

---

## 1 Introduction (funnel, 5 paragraphs + roadmap)

### P1 — Background and the contested assumption
- The orchestration bet: industry moves from "one big model" to pipelines and
  agent teams; the implicit claim is that structure substitutes for model tier.
- Hook in the author's own lineage: personas bridge cost–performance for solo
  models (Paper 2, 10.5281/zenodo.19533619); this paper asks whether the same
  holds for TEAMS and pipelines.

### P2 — Prior approaches and why they are insufficient
- Productivity experiments show large gains from single chatbots
  [R1][R2][R3] but treat the model as given, not orchestrated.
- Multi-agent and ensemble work shows quality gains [R4][R5] but rarely
  reports dollars; cost reports ignore quality.

### P3 — Three gaps
- (i) no factorial, cost-matched comparison of cheap pipelines vs frontier solo;
- (ii) no mechanistic account of WHAT orchestration adds (structure? length?
  insight?); (iii) no economic metric robust to price assumptions.

### P4 — This study (one paragraph summary of design and headline numbers)
- 2×2×2 factorial × 5 families × 19 problems × reps 3/2 (n = 1,900); blinded
  LLM panel; Study 2 refinement probe + qualitative coding; cost-effectiveness
  frontier with T-EGR (heir to the EGR metric of Paper 2).

### P5 — Numbered contributions (5, matching paperB style)
1. First cost-matched pre-registered factorial experiment on orchestration
   economics (negative superiority results reported as primary findings).
2. T-EGR: a price-assumption-robust economic metric; Pareto frontier stable
   across the φ price panel.
3. Mechanism: "coverage vs density" from quantitative + qualitative Study 2
   (κ = 0.824 codebook reliability).
4. Refinement boundary: parity reachable at $0.002, superiority never reached.
5. Practitioner contingency rules (cell → use-case → T-EGR decision table).

### Roadmap paragraph
- "Section 2 reviews…, Section 3 describes…, Section 4 presents…, Section 5
  discusses…, Section 6 acknowledges limitations, Section 7 outlines future
  directions, Section 8 concludes." (exact paperB formula)

---

## 2 Literature Review (4 themed streams + integration, paperB style)

### 2.1 Productivity effects of generative AI
- 2.1.1 Controlled experiments: quality uplift concentrated in low performers
  [R1]; novice gains in field settings [R2].
- 2.1.2 The jagged frontier: AI helps inside its capability boundary, hurts
  outside [R3] — anticipates our persona penalty and negative superiority.

### 2.2 Multi-agent LLM systems and ensemble generation
- 2.2.1 Sampling-based aggregation (self-consistency) [R4]; debate-style
  multi-agent reasoning [R5].
- 2.2.2 Gap sentence: gains reported without matched costs.

### 2.3 LLM-as-a-judge evaluation methodology
- Bias taxonomy (position, verbosity, self-preference) and panel remedy
  [R7][R6]; link to §3.5 bias-control battery.

### 2.4 Open-science methodology and economic measurement
- Preregistration [R8]; multiverse robustness [R9]; reproducible computation
  [R10]; pilot-effect-size discipline [R11]; effect-size reporting [R12];
  coder agreement [R13]; token-invariant costing grounded in quantity–price
  decomposition [R15].

### Integration paragraph
- Synthesize the four streams into the contingency question this paper tests:
  structure × tier × persona, priced; end with the three pre-registered
  hypotheses they motivate.

---

## 3 Methodology

### 3.1 Research design
- 2×2×2 factorial: tier (cheap/frontier) × structure (solo/team) × persona
  (none/cultural); family (5) as blocking factor; 19 problems as random
  stimulus effect (no pseudo-replication: aggregate ratings, not stimuli —
  same logic as Paper 1's "6,375 solutions assessed by all five LLMs").
- Pre-registration chain: 10 protocols + amendments, all registered BEFORE
  computation; confirmatory/exploratory separation; mechanical gates never
  adjusted post hoc [R8].

### 3.2 Models evaluated
- 3.2.1 Frontier models (5 families): pin rule, dated snapshots, preview-risk
  fallbacks.
- 3.2.2 Cheap siblings: price ratios 3.4×–8×; heterogeneity absorbed by the
  family random effect.

### 3.3 Orchestration structures and personas
- Solo vs team (builder → critic → refiner, intermediate outputs discarded
  from the final answer — cost bias disclosed); fixed cultural-persona
  mapping (congruent roles, inherited from Paper 2).

### 3.4 Stimuli and response generation
- 30 domain-stratified business problems (15 inherited verbatim from Paper 1,
  DOI 10.5281/zenodo.17407392; 10 fresh post-cutoff cases + extensions);
  11 used for feasibility gating (pilot), 19 for confirmatory analysis;
  identical text across all cells; no instruction wrappers; temperature and
  seed policy.

### 3.5 Evaluation framework
- 3.5.1 Judge model selection: 3 judges, families disjoint from generators
  (D33 replacement rationale).
- 3.5.2 Scoring rubric: six 1–5 dimensions; composite primary outcome;
  frozen 3 prompt variants (never re-optimized — Paper 1 κ-collapse lesson).
- 3.5.3 Inter-rater reliability: Fleiss' κ / ICC(2,k); dimension-level
  agreement reported; blinding and order shuffle as bias controls [R7].

### 3.6 Statistical analysis
- 3.6.1 Effect sizes: Welch d with bootstrap CIs (5,000 resamples, seed 42)
  [R12]; estimation-first reporting.
- 3.6.2 Inferential statistics: mixed models with family random effect
  (pseudo-replication fix over Paper 2); FDR-BH within hypothesis families;
  Holm for directional tests.
- 3.6.3 Economic analysis: token-invariant costing (tokens × frozen price
  vector v2026-07-30 [R15]); blended-φ rule with sensitivity panel φ ∈
  {0.25, 0.5, 0.75} (Amendment A); T-EGR definition (within-family, pooled);
  Pareto frontier + ICER; judge cost excluded.
- 3.6.4 Robustness checks (pre-registered battery): judge LOO, family LOO,
  outlier sensitivity, mean-vs-median, 80/20 problem split, truncation audit
  [R9].
- 3.6.5 Qualitative coding protocol (Study 2): triple sampling (seed
  20260801), two-wave inductive→closed coding, frozen 13-code codebook,
  blinded LLM coders, κ gate 0.70 with base-rate disclosure [R13].

### 3.7 Validity and reliability
- Construct validity (rubric vs persona discourse-style tension); internal
  validity (blinding, frozen configs); external validity (single task domain,
  English business strategy); measurement-threat disclosures (team cost bias,
  truncated answers).

### 3.8 Code and data availability
- Repository, ledger format, OSF registration status, reproduction runbook
  [R10].

---

## 4 Results

### 4.1 Study 1 — factorial main effects and interactions
- 4.1.1 Cell means, n, SD (Table 1); frontier > cheap; team helps but costs
  ~4× tokens.
- 4.1.2 Effect sizes with bootstrap CIs for tier, structure, persona and the
  tier × structure interaction (H1).
- **Key Takeaway:** structure is a cheap-tier amplifier, not a universal
  substitute.

### 4.2 The persona penalty
- 4.2.1 Every P cell Pareto-dominated by its N twin; dimension-level pattern
  (novelty/cultural sensitivity up; usefulness/elaboration down).
- 4.2.2 Echo of Paper 2's contingency result at the TEAM level.
- **Key Takeaway:** persona buys style, not score; costs more per point.

### 4.3 The practicality gap (CTP vs FSN baseline)
- Paired comparisons negative in all families — the gap Study 2 must close.
- **Key Takeaway:** orchestrated cheap teams do not beat a single frontier
  call on matched problems.

### 4.4 Study 2 — refinement probe (quantitative)
- 4.4.1 Gap recovery: 60% (kimi), 8% (claude, saturated), 64% (qwen);
  G1 PASS / G2 mechanical FAIL → superiority formally rejected.
- 4.4.2 Cross-family matrix: no wins, two ties with the weakest frontier
  (rules locked before computation — anti-cherry-picking).
- 4.4.3 Length analysis: r = +0.68 length↔gain; dilution rejected.
- **Key Takeaway:** a $0.002 pass buys parity with the weakest frontier,
  never superiority.

### 4.5 Study 2 — qualitative mechanism
- 4.5.1 Codebook reliability: pooled κ = 0.824; 6 codes below gate disclosed
  as medium reliability.
- 4.5.2 What moves: all 6 changed codes structural; no insight code moves.
- 4.5.3 Residual frontier edge: concise maxims, zero boilerplate; claude
  saturation (0 codes changed).
- **Key Takeaway:** orchestration buys coverage; the frontier wins on density.

### 4.6 Economic analysis
- 4.6.1 Cost–quality map: 8 cells + 3 refined points (scatter, Pareto
  frontier identical across all φ).
- 4.6.2 T-EGR table: C-S-P 8.60 … F-T-P 0.27; ICER best buy C-S-N
  (+$0.016/point), worst F-T-P (+$1.81/point).
- 4.6.3 Refined kimi: parity quality at 78% of frontier cost (absolute-mean
  caveat stated).
- **Key Takeaway:** substitute structure at the cheap end; the frontier team
  is the worst dollar spent.

### 4.7 Robustness checks and generalizability
- Battery outcomes table; stability statement (paperB style: "results are
  stable…").
- **Key Takeaway:** findings survive judge/family/outlier/split perturbations.

### 4.8 Summary of key findings
- Table (paperB Table-9 style): finding | evidence | section.

---

## 5 Discussion
- 5.1 Contingency model of orchestration: when to orchestrate (cheap solo
  end, coverage tasks) vs not (density-critical tasks, frontier budgets);
  decision table.
- 5.2 Why density resists orchestration: additive composition cannot compress;
  connect persona penalty + length correlation; falsifiable prediction
  (subtractive refiner study).
- 5.3 Relation to prior work: extends Paper 2's EGR to teams (T-EGR);
  completes the Paper 4 contingency arc from verifiable to open-ended tasks.
- 5.4 Methodological lessons: negative superiority as primary findings;
  token-invariant costing as reusable infrastructure.

## 6 Limitations
- LLM-only judging (no human panel) with bias controls [R6][R7]; blended-φ
  assumption; single task domain/language; cross-family comparisons
  descriptive; truncation and team-cost disclosures.

## 7 Future Directions
- Subtractive/editing-style refiner; human-panel replication; second task
  domain (code, scientific writing); dynamic pricing integration; persona
  repair study (style-to-substance conversion).

## 8 Conclusion
- Four-sentence verdict + the practitioner sentence ("match the right
  structure to the right tier for the right cost" — mirrors Paper 2's
  closing formula).

---

## Figures and tables (planned)

1. Fig 1: 2×2×2 design + apparatus schematic.
2. Fig 2: forest plot, quality by cell with bootstrap CIs, family facets.
3. Fig 3: cost–quality scatter, Pareto frontier, refined-CTP diamonds
   (from results/cost/cost_effectiveness_scatter.png).
4. Fig 4: gap-recovery + cross-family 6-direction matrix.
5. Fig 5: code-prevalence heatmap (orig/refined/fsn × 13 codes).
6. Table 1: cell summary (cost, quality, SD, T-EGR, ICER).
7. Table 2: robustness battery outcomes.
8. Table 3: codebook with κ per code.
9. Table 4: summary of key findings (§4.8).

## Supplementary (planned)
- Decision register D1–D34 cross-linked; per-run CSVs; judge rationale
  samples; all 10 protocols + amendments; price vectors; runbook.

---

## Reference register (DOI-verified 2026-08-07)

| ID | Citation | DOI | Verified via |
|---|---|---|---|
| R1 | Noy & Zhang (2023), Science 380 | 10.1126/science.adh2586 | science.org |
| R2 | Brynjolfsson, Li & Raymond (2023), NBER WP 31161 | 10.3386/w31161 | nber.org |
| R3 | Dell'Acqua et al. (2023), HBS WP | 10.2139/ssrn.4573321 | ssrn.com |
| R4 | Wang et al. (2023), ICLR 2023 | 10.48550/arXiv.2203.11171 | arxiv.org |
| R5 | Liang et al. (2024), EMNLP 2024 | 10.18653/v1/2024.emnlp-main.992 | aclanthology.org |
| R6 | Verga et al. (2024) | 10.48550/arXiv.2404.18796 | arxiv.org |
| R7 | Zheng et al. (2023), NeurIPS 2023 D&B | 10.48550/arXiv.2306.05685 | arxiv.org |
| R7b | Cohen (1988), Statistical Power Analysis (book) | 10.4324/9780203771587 | re-verify before submit |
| R8 | Nosek et al. (2018), PNAS 115 | 10.1073/pnas.1708274114 | pnas.org |
| R9 | Steegen et al. (2016), Perspect Psychol Sci 11 | 10.1177/1745691616658637 | pubmed/sage |
| R10 | Sandve et al. (2013), PLoS Comput Biol 9 | 10.1371/journal.pcbi.1003285 | journals.plos.org |
| R11 | Albers & Lakens (2018), JESP 74, 187–195 | 10.1016/j.jesp.2017.09.004 | verified 2026-08-07 |
| R12 | Lakens (2013), Front Psychol 4:863 | 10.3389/fpsyg.2013.00863 | frontiersin.org |
| R13 | Cohen (1960), EPM 20, 37–46 | 10.1177/001316446002000104 | journals.sagepub.com |
| R14 | Tomlinson et al. (2024), Sci Rep 14:3732 | 10.1038/s41598-024-54271-x | nature.com (journal DOI) |
| R15 | Diewert (1976), J Econometrics 4:115–145 | 10.1016/0304-4076(76)90009-9 | verified 2026-08-07 |
| R16 | Wei et al. (2022), NeurIPS 2022 | 10.48550/arXiv.2201.11903 | arxiv.org → NeurIPS 2022 |
| R17 | Yao et al. (2023), NeurIPS 2023 | 10.48550/arXiv.2305.10601 | arxiv.org → NeurIPS 2023 |
| R18 | Shinn et al. (2023), NeurIPS 2023 | 10.48550/arXiv.2303.11366 | arxiv.org → NeurIPS 2023 |
| R19 | Snell et al. (2024) | 10.48550/arXiv.2408.03314 | arxiv.org |
| Own | Hariri (2026), Doing More with Less | 10.5281/zenodo.19533619 | local cache paperB.txt |
| Own | Hariri (2025), LLM-Creativity | 10.5281/zenodo.17407392 | local cache / data provenance |
| Own | Hariri (2025), Team Composition Paradox | 10.5281/zenodo.17490945 | DESIGN-DECISIONS.md |

**PENDING-VERIFY (excluded until DOI confirmed):** Jiang et al. 2023
(LLM-Blender); Du et al. 2023 (multiagent debate); Park et al. 2023
(generative agents); Bommasani et al. 2021 (foundation models); Guo et al. 2024
(LLM-MAS survey); Koo et al. 2024 (LLM-as-judge survey); GPT-4 technical report.

## Mapping: completed artifacts → sections
- §3 Methodology ← DESIGN-DECISIONS.md (D1–D34), 10 protocols, config/*.json.
- §4.1–4.3, 4.7 ← Study-1 results + INTERIM decisions + A1–A4 amendments.
- §4.4–4.5 ← REFINE-STUDY2-PILOT.md, QUALITATIVE-STUDY2.md, cross_family.json.
- §4.6 ← COST-EFFECTIVENESS.md, results/cost/*.
- §5 ← all of the above + Papers 2/4 lineage.
