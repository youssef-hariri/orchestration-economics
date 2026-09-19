# Figure Selection Guide — Economics of Orchestration Paper

**Version:** 2026-08-08 · **Scope:** 22 generated figures + variation catalogue  
**Audience:** (1) AI drafting the final manuscript, (2) human reviewer selecting optimal figures  
**Rule:** Every figure must carry an evidentiary claim. No decorative figures.

---

## How to Use This Guide

1. **For the AI drafter:** Use the "Placement" and "Caption template" fields to insert figure references into `FULL-PAPER-DRAFT.md`. Replace bracketed placeholders with actual values from the text.
2. **For the human reviewer:** Use the "Priority" column to decide inclusion. "Must-have" figures are pre-selected; "Reviewer choice" figures are optional and flagged with the tradeoffs.
3. **For generating variations:** See the "Possible variations" subsection under each figure. If a variation is needed, the generation script can be extended.

---

## Quick-Reference Priority Table

| # | Figure | Priority | Placement | Claim Supported |
|---|--------|----------|-----------|-----------------|
| 1 | Design schematic | **Must-have** | §3.1 | Experimental design integrity |
| 2 | Forest plot (quality by cell) | **Must-have** | §4.1 | H1: tier × structure interaction |
| 3 | Cost-effectiveness scatter | **Must-have** | §4.6 | Pareto frontier stability |
| 4 | Gap recovery + dimensions | **Must-have** | §4.4 | H3: refinement boundary |
| 5 | Code prevalence heatmap | **Must-have** | §4.5 | Mechanism: coverage vs density |
| 6 | T-EGR bar chart | **Reviewer choice** | §4.6 or Discussion | Economic efficiency ranking |
| 7 | Cross-family matrix | **Reviewer choice** | §4.4 or Supplementary | Cross-family generalizability |
| 8 | Robustness LOO | **Reviewer choice** | §4.7 or Supplementary | A2 battery: sensitivity |
| 9 | Meta-analysis forest | **Reviewer choice** | §4.7 or Supplementary | Generalization across families |
| 10 | Persona dimensions | **Reviewer choice** | §4.2 or Supplementary | Persona penalty mechanism |
| 11 | Pilot v1 vs v2 | **Supplementary** | — | Replication stability |
| 12 | Length-quality correlation | **Supplementary** | §4.4 (inline ref) | Dilution hypothesis rejection |
| 13 | LMM coefficients | **Supplementary** | — | Exploratory model diagnostics |
| 14 | Kappa reliability | **Supplementary** | — | Codebook validation |
| 15 | Convergence summary | **Supplementary** | — | Qualitative mechanism summary |
| 16 | ANOVA η² | **Supplementary** | — | Effect size decomposition |
| 17 | EB shrinkage | **Supplementary** | — | Shrinkage diagnostics |
| 18 | T-EGR radar | **Supplementary** | — | Alternative T-EGR view |
| 19 | φ-Sensitivity three-panel | **Must-have** | §4.6 | Price-assumption robustness |
| 20 | Contingency flowchart | **Must-have** | §5.1 | Practitioner decision rules |
| 21 | Sequential boundary | **Reviewer choice** | §4.1 | O'Brien–Fleming stopping |
| 22 | Persona radar overlay | **Reviewer choice** | §4.2 | Style-over-substance signature |
| 23 | Study 3 family × domain landscape | **Must-have** | §4.3 | Family-specific orchestration economics |
| 8 | Robustness LOO | **Reviewer choice** | §4.7 or Supplementary | A2 battery: sensitivity |
| 9 | Meta-analysis forest | **Reviewer choice** | §4.7 or Supplementary | Generalization across families |
| 10 | Persona dimensions | **Reviewer choice** | §4.2 or Supplementary | Persona penalty mechanism |
| 11 | Pilot v1 vs v2 | **Supplementary** | — | Replication stability |
| 12 | Length-quality correlation | **Supplementary** | §4.4 (inline ref) | Dilution hypothesis rejection |
| 13 | LMM coefficients | **Supplementary** | — | Exploratory model diagnostics |
| 14 | Kappa reliability | **Supplementary** | — | Codebook validation |
| 15 | Convergence summary | **Supplementary** | — | Qualitative mechanism summary |
| 16 | ANOVA η² | **Supplementary** | — | Effect size decomposition |
| 17 | EB shrinkage | **Supplementary** | — | Shrinkage diagnostics |
| 18 | T-EGR radar | **Supplementary** | — | Alternative T-EGR view |

---

## Must-Have Figures (Pre-Selected)

---

### Figure 1. Experimental Design: 2 × 2 × 2 Factorial + Apparatus

- **File:** `figures/fig1_design_schematic.{png,pdf}`
- **Data source:** PAPER-STRUCTURE.md (design specification)
- **Placement:** §3.1 (Research design), immediately after the design paragraph
- **Size recommendation:** Full text width (~15 cm), landscape orientation
- **Aspect ratio:** 4:3
- **Color scheme:** Tier = green, Structure = yellow, Persona = red; cells color-coded by tier
- **Claim supported:** "The experiment is a 2 × 2 × 2 between-cell factorial with model family as a blocking factor" — visual proof of the design structure and sample sizes.
- **Caption template:**
  > Figure 1. Experimental design and apparatus. Top: the three manipulated factors (tier, structure, persona) and their levels. Middle: the eight resulting cells with per-cell sample sizes (cheap cells n = 285, frontier cells n = 190). Bottom: the generator apparatus (builder → critic → refiner) and the blinded three-judge evaluation panel. The dashed green arrow indicates the Study 2 refinement pass.
- **In-text reference:** "The design is shown in Figure 1."
- **LaTeX label:** `\label{fig:design}`

#### Possible variations to generate
1. **B&W print version** — remove color fills, use hatching patterns for cell boxes; useful for print journals with color charges
2. **Simplified version (no apparatus)** — top + middle panels only, for journals with strict figure limits
3. **Animated version (for presentations)** — reveal factors sequentially: tier → structure → persona → cells → apparatus; export as GIF or MP4
4. **Family-stratified version** — show the 5 families as rows within each cell, with n per family; useful if reviewer asks for family-level replication detail
5. **Decision-register overlay** — annotate each design element with its corresponding D-number (D1–D39) and protocol number; useful for the pre-registration supplement

---

### Figure 2. Quality by Experimental Cell with 95% Confidence Intervals

- **File:** `figures/fig2_forest_plot.{png,pdf}`
- **Data source:** `results/cost/cell_summary.csv` (φ = 0.5)
- **Placement:** §4.1, after the H1 interaction result paragraph
- **Size recommendation:** Full text width (~15 cm)
- **Aspect ratio:** 16:9
- **Color scheme:** Cheap tier = blue (#2E86AB), team cells = purple (#A23B72), frontier = orange (#F18F01), frontier team = red (#C73E1D)
- **Claim supported:** "Structure is a cheap-tier amplifier, not a universal substitute" — visual evidence that the cheap-team cells approach frontier-solo quality while frontier-team cells show diminishing returns.
- **Caption template:**
  > Figure 2. Mean composite quality score (1–5 scale) by experimental cell with 95% confidence intervals, primary analysis (φ = 0.50). Cells are ordered by cost. The dashed orange line marks the F-S-N baseline. Cheap-team cells (C-T-N, C-T-P) approach frontier-solo quality at a fraction of the cost; frontier-team cells (F-T-N, F-T-P) show only marginal quality gains for large cost increases.
- **In-text reference:** "Figure 2 shows the quality distribution across all eight cells."
- **LaTeX label:** `\label{fig:forest}`

#### Possible variations to generate
1. **Family-faceted version** — 5 small multiples (one per family), each showing the 8 cells; reveals family heterogeneity in the interaction
2. **B&W version with symbols** — circles for cheap, diamonds for frontier; filled = team, hollow = solo; useful for colorblind readers and print
3. **With persona annotation** — vertical brackets connecting persona-loaded to no-persona twins, with the d-value of the persona penalty printed between them
4. **Interactive version (for web appendix)** — hover to show exact mean, SD, n, and cost per cell
5. **Sorted by quality (not cost)** — alternative ordering to emphasize the quality hierarchy rather than the cost progression
6. **With T-EGR annotation** — add a secondary x-axis or label showing T-EGR for each cell

---

### Figure 3. Cost-Effectiveness Frontier: 8 Cells + Study-2 Refined C-T-P

- **File:** `results/cost/cost_effectiveness_scatter.{png,pdf}` (pre-existing)
- **Data source:** `results/cost/cost_effectiveness.json`
- **Placement:** §4.6, at the start of the economic analysis subsection
- **Size recommendation:** Full text width (~15 cm)
- **Aspect ratio:** 4:3
- **Color scheme:** Matches Fig 2 cell colors; refined points as diamond markers
- **Claim supported:** "The Pareto frontier is identical across all three φ" — visual proof of price-assumption robustness and the dominated set of persona-loaded team cells.
- **Caption template:**
  > Figure 3. Cost–quality scatter plot with Pareto frontier (dashed line, φ = 0.50). Error bars show ±1 SD on both axes. Diamond markers show the three refined CTP points from Study 2 (kimi: $0.065, quality 4.585; claude: $0.198, quality 4.559; qwen: $0.017, quality 4.398). The frontier {C-S-P, C-S-N, C-T-N, F-S-N, F-T-N} is stable across the full φ sensitivity panel.
- **In-text reference:** "The cost–quality map is shown in Figure 3."
- **LaTeX label:** `\label{fig:pareto}`

#### Possible variations to generate
1. **Three-panel φ comparison** — ~~side-by-side scatters for φ = 0.25, 0.50, 0.75 showing frontier stability explicitly; strong visual for the robustness claim~~ **Superseded by Figure 19** (see below for full spec)
2. **Log-cost version** — x-axis on log scale to de-emphasize the frontier-team cost inflation and show the cheap-end clustering more clearly
3. **With ICER arrows** — arrows from each dominated cell to its Pareto-dominating neighbor, labeled with ICER values
4. **Animated φ sweep** — show the scatter evolving as φ slides from 0 to 1; useful for presentations
5. **Family-stratified version** — 5 panels, one per family, showing within-family cost-quality clouds; reveals family-level Pareto frontiers
6. **With iso-T-EGR contours** — overlay curves of constant T-EGR on the scatter; mathematically elegant but potentially cluttered

---

### Figure 4. Study 2: Refinement Probe Results

- **File:** `figures/fig4_gap_recovery.{png,pdf}`
- **Data source:** `results/refine_study2_pooled.json`
- **Placement:** §4.4, after the gap-recovery paragraph
- **Size recommendation:** Full text width (~15 cm)
- **Aspect ratio:** 16:9 (two panels side by side)
- **Color scheme:** Pre-refinement = red (#E74C3C), post-refinement = blue (#3498DB); per-family bars in sub-panel
- **Claim supported:** "A $0.002 refinement pass recovers most of the frontier gap on average, never achieves paired superiority" — quantitative gap recovery + per-dimension mechanism.
- **Caption template:**
  > Figure 4. Study 2 refinement probe results. Left: pre-refinement (red) and post-refinement (blue) effect-size gaps versus the F-S-N baseline, by family. Recovery percentages: kimi 58%, claude 8%, qwen 63%. Right: per-dimension Cohen's d for refined versus original CTP, by family. Usefulness and Elaboration show large gains for kimi and qwen (d = 0.8–1.4); claude is unchanged (saturation). Novelty is protected (all families pass the −0.10 non-inferiority margin).
- **In-text reference:** "Figure 4 shows the gap recovery and per-dimension refinement effects."
- **LaTeX label:** `\label{fig:refinement}`

#### Possible variations to generate
1. **Three-panel family-faceted version** — one panel per family (kimi, claude, qwen), each showing pre/post gap + dimension breakdown; useful if the reviewer wants family-specific detail
2. **With G2 gate annotation** — add a horizontal dashed line at d = 0.20 (the G2 superiority threshold) to visually show that no family crosses it
3. **Stacked dimension bars** — show the composite score as the sum of dimension contributions, with color segments; reveals which dimensions drive the composite change
4. **Violin plots of gap distribution** — instead of single d-values, show the distribution of per-problem gap changes; reveals heterogeneity
5. **With length overlay** — add a third small panel showing the length ratio (refined/original) correlation with score change (r = +0.68)
6. **Animated gap closure** — show bars shrinking from pre- to post-refinement with a tween animation; for presentations

---

### Figure 5. Code Prevalence Heatmap: Original, Refined, and Frontier (Study 2)

- **File:** `figures/fig5_code_heatmap.{png,pdf}`
- **Data source:** `results/qual2_analysis.json`
- **Placement:** §4.5, after the codebook reliability paragraph
- **Size recommendation:** Full text width (~15 cm), may need to span two columns
- **Aspect ratio:** 16:9
- **Color scheme:** Yellow (0) → Orange → Red → Dark red (1.0) — sequential colormap
- **Claim supported:** "Orchestration buys coverage (more structure, more length); the frontier wins on density (compressed maxims, zero boilerplate)" — the mechanism.
- **Caption template:**
  > Figure 5. Code prevalence heatmap (Study 2, n = 90 texts). Each panel shows one family (kimi, claude, qwen) with rows = condition (original CTP, refined CTP, frontier FSN) and columns = the 13-code codebook. Color intensity = prevalence (proportion of texts containing the code). Green checkmarks (✓) indicate κ-reliable codes (κ ≥ 0.70). The frontier row shows universal `concise_maxims` (1.00) and zero `redundancy_bloat` (0.00); refined rows show high structural-code prevalence but persistent maxims gap.
- **In-text reference:** "The qualitative mechanism is shown in Figure 5."
- **LaTeX label:** `\label{fig:heatmap}`

#### Possible variations to generate
1. **Difference heatmap** — show refined − original and frontier − refined as separate difference panels; emphasizes what changed and what did not
2. **With κ annotation** — print the exact κ value inside each cell (or as a border color); combines reliability and prevalence in one figure
3. **Clustered reordering** — reorder codes by hierarchical clustering of prevalence patterns; may reveal code families not visible in the arbitrary order
4. **Single-panel version (all families stacked)** — 9 rows × 13 columns; more compact but less readable
5. **Animated transition** — morph from original → refined → frontier for each family; for presentations
6. **Simplified version (κ-reliable codes only)** — show only the 7 reliable codes in a cleaner 3×7 grid; useful if figure limits are strict

---

## Reviewer-Choice Figures (Optional Inclusion)

---

### Figure 6. Tiered Efficiency Gain Ratio (T-EGR) by Cell

- **File:** `figures/fig6_tegr_bars.{png,pdf}`
- **Data source:** `results/cost/cost_effectiveness.json`
- **Placement:** §4.6 (after the cost-quality table) or §5.1 (Discussion, contingency rules)
- **Size recommendation:** Half text width (~8 cm) or full width
- **Aspect ratio:** 16:9
- **Color scheme:** Same cell colors as Fig 2
- **Claim supported:** "C-S-N achieves 98% of frontier quality at 23% of the cost (T-EGR 6.15); the frontier team cell is the worst dollar in the experiment (T-EGR 0.27)" — the economic bottom line.
- **Caption template:**
  > Figure 6. Tiered Efficiency Gain Ratio (T-EGR) by cell, pooled across families. T-EGR = (Quality_cell / Quality_FSN) / (Cost_cell / Cost_FSN). The dashed line marks the F-S-N baseline (T-EGR = 1.0). Cheap solo cells dominate the efficiency ranking; frontier team cells are Pareto-dominated.
- **In-text reference:** "The T-EGR ranking (Figure 6) quantifies the economic conclusion."
- **LaTeX label:** `\label{fig:tegr}`
- **Inclusion rationale:** High-impact single-number summary. Consider if the journal allows 6+ figures. Omit if strict limits (the Pareto scatter in Fig 3 already conveys the same information). **Recommended: include if figure limit ≥ 6.**

#### Possible variations to generate
1. **Family-stratified T-EGR** — 5 small bars per cell, one per family, showing family-specific T-EGR; reveals cross-family variance
2. **With cost annotation** — add a secondary label showing the actual dollar cost per cell
3. **Log-scale version** — compresses the wide dynamic range (0.27 to 8.60) for better readability
4. **Horizontal waterfall chart** — show the contribution of each factor (tier, structure, persona) to the T-EGR deviation from baseline; more explanatory
5. **Interactive version** — slider for φ that updates T-EGR in real time; for web appendix

---

### Figure 7. Cross-Family Comparison Matrix (Study 2)

- **File:** `figures/fig7_cross_family_matrix.{png,pdf}`
- **Data source:** `results/cross_family.json`
- **Placement:** §4.4 (after gap recovery) or Supplementary Material
- **Size recommendation:** Full text width
- **Aspect ratio:** 16:9 (two panels side by side)
- **Color scheme:** Negative d = red (#E74C3C), positive d = green (#27AE60)
- **Claim supported:** Cross-family comparisons are descriptive and confounded — no family wins across the board; refined kimi ties the weakest frontier.
- **Caption template:**
  > Figure 7. Cross-family comparison matrix (descriptive, not causal). Left: original CTP from one family versus FSN from another family. Right: refined CTP versus cross-family FSN. All comparisons remain negative (red bars) after refinement except kimi refined CTP versus qwen FSN (d = +0.10, n.s.). The diagonal (within-family) comparisons are the causal comparisons reported in the main text.
- **In-text reference:** "Cross-family comparisons (Figure 7) are descriptive and confounded with family quality."
- **LaTeX label:** `\label{fig:crossfamily}`
- **Inclusion rationale:** Useful for defending against the "cherry-picking" critique — shows that no cross-family pairing flips the result. **Recommended: include if reviewer asks about generalizability or include in supplementary.**

#### Possible variations to generate
1. **Full matrix heatmap** — 5×5 matrix (families × families) with color intensity = d-value; more compact but less precise
2. **With confidence intervals** — add error bars to each bar for visual uncertainty
3. **Before/after animated** — show the matrix morphing from original to refined; for presentations
4. **With Holm-correction annotation** — mark which comparisons survive multiple-testing correction

---

### Figure 8. Robustness: Leave-One-Out Sensitivity (A2 Battery)

- **File:** `figures/fig8_robustness_loo.{png,pdf}`
- **Data source:** `results/interim2_analysis.json` (A2_5, A2_6)
- **Placement:** §4.7 (Robustness checks) or Supplementary Material
- **Size recommendation:** Full text width
- **Aspect ratio:** 16:9 (two panels)
- **Color scheme:** Blue (#2E86AB) for family LOO, purple (#A23B72) for problem LOO; full-d reference = red dashed
- **Claim supported:** "Findings survive judge, family, problem, and length perturbations; the interaction is small but robust" — the robustness battery.
- **Caption template:**
  > Figure 8. Leave-one-out sensitivity analysis (A2 battery). Left: leave-one-family-out. d ranges from −0.143 (drop kimi) to −0.303 (drop gemini); sign is stable in all five folds. Right: leave-one-problem-out (first 10 of 19 folds shown). d ranges from −0.212 to −0.247; no single problem drives the interaction. The red dashed line marks the full-sample d = −0.227.
- **In-text reference:** "The LOO analysis (Figure 8) confirms no single family or problem drives the interaction."
- **LaTeX label:** `\label{fig:loo}`
- **Inclusion rationale:** Standard robustness visualization for high-impact journals. May be expected by reviewers. **Recommended: include in main text for journals with ≥ 7 figure limit; otherwise supplementary.**

#### Possible variations to generate
1. **Full problem LOO (all 19 folds)** — taller figure showing all problems; current version samples 10 for readability
2. **With p-value annotation** — add asterisks for significance on each point
3. **Combined forest plot** — single forest plot with both family and problem folds interleaved; more compact
4. **With meta-analysis overlay** — add the pooled estimate and prediction interval from the random-effects model
5. **Animated fold reveal** — sequentially remove each family and show the estimate stabilize; for presentations

---

### Figure 9. Random-Effects Meta-Analysis: Interaction by Family

- **File:** `figures/fig9_meta_analysis_forest.{png,pdf}`
- **Data source:** `results/exploratory_analysis.json` (A3.4)
- **Placement:** §4.7 or Supplementary Material
- **Size recommendation:** Half text width (~8 cm)
- **Aspect ratio:** 4:3
- **Color scheme:** Blue (#2E86AB) points, red (#E74C3C) pooled line
- **Claim supported:** "The random-effects meta-analysis over the five families gives a pooled d = −0.270 (CI [−0.472, −0.069]) with low-moderate heterogeneity (I² = 28.5%)" — generalization claim.
- **Caption template:**
  > Figure 9. Random-effects meta-analysis of the tier × structure interaction across five model families (A3.4). Squares = per-family estimates with 95% CIs; diamond = pooled estimate. Heterogeneity: τ² = 0.015, I² = 28.5%, Q = 5.59. The pooled effect is significant (z = −2.64, p = 0.008) with low-moderate heterogeneity.
- **In-text reference:** "Meta-analysis confirms generalization (Figure 9)."
- **LaTeX label:** `\label{fig:meta}`
- **Inclusion rationale:** Elegant and compact. Required if the paper emphasizes the "generalizes across families" claim. **Recommended: include if figure limit ≥ 7; otherwise supplementary.**

#### Possible variations to generate
1. **With prediction interval** — show the 95% prediction interval (for a new family) in addition to the confidence interval
2. **Funnel plot** — standard meta-analysis diagnostic; tests for publication bias (not applicable here but expected by some reviewers)
3. **Cumulative meta-analysis** — show how the pooled estimate evolves as families are added sequentially
4. **Subgroup analysis** — split by family origin (Chinese vs Western) or by price ratio
5. **Bayesian meta-analysis** — show posterior distribution of the pooled effect with credible intervals

---

### Figure 10. Persona Effect by Quality Dimension (FDR-Corrected)

- **File:** `figures/fig10_persona_dimensions.{png,pdf}`
- **Data source:** `results/exploratory_analysis.json` (A3.5)
- **Placement:** §4.2 (The persona penalty) or Supplementary Material
- **Size recommendation:** Full text width or half width
- **Aspect ratio:** 16:9
- **Color scheme:** Positive d = green (#27AE60), negative d = red (#E74C3C)
- **Claim supported:** "Personas trade judged usefulness for a small novelty gain" — the dimension-level decomposition.
- **Caption template:**
  > Figure 10. Persona effect (Persona − No Persona) by quality dimension, exploratory analysis (A3.5). Cohen's d with FDR correction (Benjamini–Hochberg, α = 0.05). Novelty is the sole dimension where personas improve quality (+0.15, p_FDR = 0.001); Usefulness (−1.02) and Elaboration (−0.97) drive the net negative effect.
- **In-text reference:** "The dimension decomposition (Figure 10) shows the tradeoff."
- **LaTeX label:** `\label{fig:personadim}`
- **Inclusion rationale:** Provides mechanistic insight into the persona penalty. The paper already discusses this in §4.2 text. **Recommended: include if figure limit ≥ 6; otherwise supplementary or inline table.**

#### Possible variations to generate
1. **With individual judge traces** — show each judge's dimension rating separately; reveals judge agreement/disagreement
2. **Family-faceted version** — 5 panels showing the same decomposition per family; reveals whether the Novelty gain is universal
3. **With raw score distributions** — violin plots of raw scores per dimension, split by persona; more informative than single d-values
4. **Radar chart version** — ~~show the 5 dimensions as a radar/spider plot for P vs N cells; visually striking~~ **Superseded by Figure 22** (see below for full spec)
5. **With interaction terms** — show how the persona effect varies by tier and structure (2×2 grid of bars)

---

### Figure 19. Pareto Frontier Stability Across φ Sensitivity Panel

- **File:** `figures/fig19_phi_sensitivity.{png,pdf}`
- **Data source:** `results/cost/cell_summary.csv` (all three φ values: 0.25, 0.50, 0.75)
- **Placement:** §4.6, after the Pareto frontier discussion paragraph
- **Size recommendation:** Full text width (~15 cm), landscape orientation
- **Aspect ratio:** 16:3 (1×3 subplots, shared axes)
- **Color scheme:** Matches Fig 3 / cost scatter style; frontier points highlighted with diamond markers
- **Claim supported:** "The Pareto frontier is identical across all three φ" — the paper's strongest robustness claim, now visualized.
- **Caption template:**
  > Figure 19. Pareto frontier stability across the price-assumption sensitivity panel. Left: φ = 0.25 (input-heavy blend). Center: φ = 0.50 (primary analysis). Right: φ = 0.75 (output-heavy blend). The frontier set {C-S-P, C-S-N, C-T-N, F-S-N, F-T-N} is identical in all three panels, satisfying the pre-registered cross-φ stability rule.
- **In-text reference:** "Frontier membership is stable across the sensitivity panel (Figure 19)."
- **LaTeX label:** `\label{fig:phisens}`
- **Inclusion rationale:** The single most impactful missing figure. Reviewers at statistical-methods-aware journals will expect visual proof of the robustness claim. **Must-have if journal figure limit ≥ 7.**

#### Possible variations to generate
1. **With φ = 0.00 and φ = 1.00 extremes** — extend to the pure-input and pure-output price assumptions for completeness
2. **Animated φ sweep** — show the scatter evolving as φ slides from 0 to 1; for presentations
3. **With family stratification** — 3×5 grid (φ × family) showing within-family frontier stability
4. **Difference-from-primary panel** — a fourth panel showing the maximum deviation from φ = 0.50 for each cell

---

### Figure 20. Practitioner Contingency Rules (Decision Flowchart)

- **File:** `figures/fig20_contingency_rules.{png,pdf}`
- **Data source:** Derived from §5.1 contingency model and cell summary statistics
- **Placement:** §5.1 (Discussion, contingency model), after the rules paragraph
- **Size recommendation:** Full text width (~15 cm) or half width if compressed
- **Aspect ratio:** 3:4 (vertical flowchart)
- **Color scheme:** Cheap tier = blue (#2E86AB), frontier = orange (#F18F01); decision nodes = white with borders; terminal cells = colored fills with T-EGR labels
- **Claim supported:** "We contribute practitioner contingency rules mapping cell to use-case to expected T-EGR" — Contribution 5, the actionable output.
- **Caption template:**
  > Figure 20. Practitioner contingency rules. Decision flowchart mapping budget tier and task type to the recommended orchestration cell, with expected T-EGR. START → budget tier (cheap / frontier) → task sensitivity (coverage / density) → recommended cell. The warning box highlights that all frontier-team cells are dominated. Derived from the §5.1 contingency model.
- **In-text reference:** "The practitioner rules are summarized in Figure 20."
- **LaTeX label:** `\label{fig:flowchart}`
- **Inclusion rationale:** Directly supports a numbered contribution. Makes the paper actionable for practitioners. **Must-have.**

#### Possible variations to generate
1. **Simplified version (3 decision nodes)** — START → budget → cell; omits the coverage/density question for brevity
2. **With cost annotation** — add the actual dollar cost next to each terminal cell
3. **With quality annotation** — add the composite quality score next to each terminal cell
4. **Animated version (for presentations)** — reveal the flowchart step-by-step as the speaker narrates
5. **Interactive web version** — clickable flowchart with hover tooltips showing cell details

---

### Figure 21. Sequential Analysis with O'Brien–Fleming Spending Function

- **File:** `figures/fig21_sequential_boundary.{png,pdf}`
- **Data source:** Protocol 03 spending function + interim analysis z-scores
- **Placement:** §4.1, after the H1 result paragraph (before Figure 2)
- **Size recommendation:** Half text width (~8 cm) or full width
- **Aspect ratio:** 4:3
- **Color scheme:** OBF boundaries = red dashed; continuation region = light gray shading; interim points = blue circles with labels; H1 decision = green checkmark
- **Claim supported:** "The sequential-analysis boundary is crossed at the scheduled final look" — the pre-registered stopping rule, visualized.
- **Caption template:**
  > Figure 21. Sequential analysis with O'Brien–Fleming spending function. The test statistic z = −2.447 crosses the interim-2 boundary |z| ≥ 1.977 (dashed red line). The shaded region is the continuation region. Interim 1 at information fraction 0.2: t = −1.63, continue. Interim 2 at information fraction 1.0: z = −2.447, boundary crossed, H1 supported. The pre-registered decision is to stop and report.
- **In-text reference:** "The sequential boundary plot (Figure 21) shows the stopping decision."
- **LaTeX label:** `\label{fig:sequential}`
- **Inclusion rationale:** Required if the target journal values sequential methods (e.g., medical trials, psychology). May be expected by statistical reviewers. **Reviewer choice — include if the target journal emphasizes pre-registered designs.**

#### Possible variations to generate
1. **With alternative spending functions** — overlay Pocock, Haybittle-Peto, and OBF boundaries for comparison
2. **With simulated paths** — show 20 simulated trial paths under H0 and H1 to illustrate power and type-I error
3. **With Bayesian overlay** — add the JZS Bayes factor trajectory (BF = 1.002 at interim 2) as a secondary y-axis
4. **Full information-fraction plot** — extend x-axis to show the theoretical boundary shape across all information fractions (0–1)

---

### Figure 22. Quality-Dimension Radar: Persona vs. No-Persona

- **File:** `figures/fig22_persona_radar.{png,pdf}`
- **Data source:** `results/cost/cell_summary.csv` (dimension means by cell, pooled)
- **Placement:** §4.2, after the persona penalty Key Takeaway (before Figure 10)
- **Size recommendation:** Half text width (~8 cm)
- **Aspect ratio:** 1:1
- **Color scheme:** No-persona = blue solid (#2E86AB); persona-loaded = red dashed (#E74C3C); grid = light gray
- **Claim supported:** "Personas trade judged usefulness for a small novelty gain" — the visual signature of the style-over-substance tradeoff.
- **Caption template:**
  > Figure 22. Quality-dimension radar for persona-loaded (red, dashed) versus no-persona (blue, solid) cells. The persona polygon is visibly smaller on Usefulness and Elaboration, slightly larger on Novelty — the visual signature of the style-over-substance tradeoff. Data are pooled across all eight cells (n = 1,900 runs).
- **In-text reference:** "The dimension-level radar (Figure 22) visualizes the persona tradeoff."
- **LaTeX label:** `\label{fig:radar}`
- **Inclusion rationale:** More visually striking than the bar chart (Fig 10) for the same claim. Radar charts are intuitive for dimension comparisons. **Reviewer choice — include if figure limit ≥ 8 or if the bar chart (Fig 10) is moved to supplementary.**

#### Possible variations to generate
1. **Family-stratified version** — 5 small radar charts, one per family; reveals whether the Novelty gain is universal
2. **With tier stratification** — 2 radar charts (cheap vs frontier), each comparing P vs N; reveals whether the persona effect differs by tier
3. **With structure stratification** — 2 radar charts (solo vs team), each comparing P vs N; reveals whether the persona effect differs by structure
4. **3D version (for presentations)** — a 3D surface plot showing the interaction of tier, structure, and dimension
5. **Normalized version** — all dimensions scaled to [0, 1] to emphasize shape differences rather than absolute magnitude

---

### Figure 23. Study 3 Family × Domain Landscape (Orchestration vs. Frontier Solo)

- **File:** `fig23_study3_family_domain.png` (in the v14 paper directory)
- **Data source:** Study 3 (Protocol 13) family-specific economics; the `tab:study3-econ` effect grid (Novelty ΔQ vs. F-S-N by family and domain)
- **Placement:** §4.3 (Study 3, family-specific economics), immediately after the Study 3 economics table
- **Size recommendation:** Full text width (~15 cm)
- **Aspect ratio:** 16:9
- **Color scheme:** Positive ΔQ (orchestration beats frontier solo) = green (#27AE60); negative ΔQ = red (#E74C3C); family rows ordered by how high the solo frontier ceiling sits
- **Claim supported:** "Orchestration economics are family-specific, not general: cheap auto-designed pipelines beat frontier solo where the solo ceiling is low (Gemini, Qwen, Kimi) and lose where it is high (Claude); the binding moderator is the family, not the task domain."
- **Caption template:**
  > Figure 23. Study 3 family × domain landscape: the Novelty effect of cheap auto-designed pipelines versus frontier solo (F-S-N) across the five families and six business domains. The binding moderator is the family — how high its solo frontier ceiling sits — not the task domain: the domain pattern does not survive within-family conditioning.
- **In-text reference:** "The family-specific economics are shown in Figure 23."
- **LaTeX label:** `\label{fig:study3-family-domain}`
- **Inclusion rationale:** The natural visual for Study 3's family-moderation finding. It was an orphan in v13 (generated but neither listed in this guide nor embedded); v14 embeds it in §4.3. **Must-have — now embedded in v14.**

---

## Supplementary Figures (Not for Main Text)

---

## Supplementary Figures (Not for Main Text)

The following figures are generated for completeness but are **not recommended for the main text** unless a reviewer specifically requests them. They belong in the supplementary materials, the OSF repository, or the reproduction runbook.

---

### Figure 11. Pilot Replication Stability (v1 vs v2)

- **File:** `figures/fig11_pilot_stability.{png,pdf}`
- **Data source:** `results/pilot_v2_analysis.json`
- **Purpose:** Demonstrate that the pilot replication (v1 vs v2) is stable (r = 0.921)
- **Recommended location:** Supplementary Material, "Pilot validation" section
- **When to promote:** If a reviewer questions the pilot-to-main-run pipeline or asks for replication evidence.

#### Possible variations
1. **Bland-Altman plot** — show agreement limits rather than just correlation; standard in medical statistics
2. **Per-family version** — 5 small multiples showing v1 vs v2 for each family
3. **Scatter plot (v1 vs v2)** — show cell means as a scatter with the identity line; Pearson r = 0.921 becomes visually obvious

---

### Figure 12. Length-Quality Correlation by Family

- **File:** `figures/fig12_length_quality.{png,pdf}`
- **Data source:** `results/pilot_v2_analysis.json`
- **Purpose:** Reject the dilution hypothesis (longer ≠ worse); show that length inflation is a prime driver, not a confound
- **Recommended location:** Supplementary Material or inline text reference only
- **When to promote:** If a reviewer explicitly raises the length-confound concern.

#### Possible variations
1. **Scatter plots with regression lines** — one panel per family, showing raw log(length) vs quality with fitted regression; more informative than single r-values
2. **Pooled scatter with family colors** — single panel with 5 colored point clouds
3. **With residual analysis** — show that the length-quality relationship is linear (residuals vs fitted)
4. **By cell rather than by family** — 8 bars showing the correlation within each cell; reveals whether length matters more for some cells

---

### Figure 13. Exploratory LMM Coefficients (A3.1)

- **File:** `figures/fig13_lmm_coefficients.{png,pdf}`
- **Data source:** `results/exploratory_analysis.json` (A3.1)
- **Purpose:** Model diagnostics for the exploratory linear mixed model
- **Recommended location:** Supplementary Material, "Exploratory analyses" section
- **When to promote:** If a reviewer asks for the full model specification or questions the mixed-model results.

#### Possible variations
1. **Full model output table** — formatted regression table with all coefficients, SEs, t-values, p-values, and CIs
2. **Residual diagnostics** — Q-Q plot, residuals vs fitted, scale-location plot; standard for model validation
3. **Random effects distribution** — histogram or caterpillar plot of the problem-level and family-level random effects
4. **Model comparison** — AIC/BIC comparison of models with and without the three-way interaction

---

### Figure 14. Inter-Coder Reliability by Code

- **File:** `figures/fig14_kappa_reliability.{png,pdf}`
- **Data source:** `results/qual2_kappa.json`
- **Purpose:** Validate the qualitative coding reliability (κ = 0.824 pooled)
- **Recommended location:** Supplementary Material, "Qualitative coding protocol" section
- **When to promote:** If a reviewer questions the qualitative methodology or asks for coder reliability.

#### Possible variations
1. **Confusion matrix heatmap** — 13×13 matrix showing coder agreement patterns per code; reveals systematic disagreements
2. **Kappa vs prevalence scatter** — show the relationship between code prevalence and κ; explains the base-rate artifact
3. **Per-coder agreement** — compare the two coders' agreement rates on each code
4. **Bootstrap distribution of κ** — show the sampling distribution of κ via bootstrap; provides confidence intervals

---

### Figure 15. Refinement Convergence: Toward / Away / Flat by Family

- **File:** `figures/fig15_convergence_summary.{png,pdf}`
- **Data source:** `results/qual2_analysis.json`
- **Purpose:** Summarize the qualitative convergence metric (does refinement move cheap outputs toward frontier?)
- **Recommended location:** Supplementary Material or §4.5 (if space permits)
- **When to promote:** If a reviewer asks for a compact summary of the qualitative mechanism.

#### Possible variations
1. **Per-code convergence arrows** — for each of the 13 codes, show an arrow indicating direction and magnitude of change (original → refined → frontier)
2. **Sankey diagram** — flow visualization showing how codes move between conditions
3. **Network graph** — nodes = codes, edges = co-occurrence patterns, colored by convergence direction
4. **With statistical test** — add a χ² test of whether the toward/away/flat distribution differs from chance

---

### Figure 16. ANOVA Effect Sizes (Partial η²)

- **File:** `figures/fig16_anova_eta2.{png,pdf}`
- **Data source:** `results/interim2_analysis.json` (A2_3)
- **Purpose:** Decompose the total variance explained by each factor and interaction
- **Recommended location:** Supplementary Material, "Statistical methods" section
- **When to promote:** If a reviewer asks for the ANOVA results or wants to compare effect sizes across factors.

#### Possible variations
1. **With ω² (omega-squared)** — show both partial η² and the less biased ω² estimate
2. **With power curves** — overlay the observed effect size against the minimum detectable effect at 80% power
3. **Family-stratified ANOVA** — 5 panels, one per family, showing how effect sizes vary
4. **Cumulative variance explained** — stacked bar showing the cumulative R² as factors are added

---

### Figure 17. Empirical-Bayes Shrinkage: Raw vs Shrunk Estimates

- **File:** `figures/fig17_eb_shrinkage.{png,pdf}`
- **Data source:** `results/exploratory_analysis.json` (A3.3)
- **Purpose:** Diagnostic for the empirical-Bayes shrinkage applied to per-family estimates
- **Recommended location:** Supplementary Material, "Exploratory analyses" section
- **When to promote:** If a reviewer questions the shrinkage methodology or asks for raw vs adjusted estimates.

#### Possible variations
1. **Shrinkage path visualization** — show each estimate moving from raw to shrunk as a trajectory; elegant but niche
2. **With prior sensitivity** — show shrunk estimates under different prior specifications
3. **Full Bayesian posterior** — replace EB with MCMC posterior distributions (requires pymc)

---

### Figure 18. T-EGR Radar Chart (Pooled)

- **File:** `figures/fig18_tegr_radar.{png,pdf}`
- **Data source:** `results/cost/cost_effectiveness.json`
- **Purpose:** Alternative visualization of the T-EGR ranking
- **Recommended location:** Not recommended for any section unless a journal specifically requests "innovative visualizations"
- **When to promote:** Almost never. Radar charts are generally discouraged in scientific publications because area perception is biased. Keep as a presentation asset only.

#### Possible variations
1. **Family-stratified radar** — 5 overlapping radar charts; reveals family-specific efficiency profiles
2. **With φ sensitivity** — 3 radar charts for φ = 0.25, 0.50, 0.75; shows T-EGR stability
3. **Normalized radar** — all values scaled to [0, 1] for shape comparison rather than absolute magnitude

---

## Figure-Selection Decision Tree

```
Is the journal's figure limit ≥ 6?
├── YES → Include all Must-have figures (1–5, 19, 20) + select from Reviewer-choice (6–10, 21, 22)
│   ├── If limit = 6 → Must-have: 1–5, 19, 20 (7 figures); drop one of {19, 20} if strictly 6
│   ├── If limit = 7 → Must-have: 1–5, 19, 20 (7 figures)
│   ├── If limit = 8 → Add Fig 21 (sequential) OR Fig 22 (radar)
│   ├── If limit = 9 → Add Figs 21 + 22
│   ├── If limit = 10 → Add Fig 6 (T-EGR)
│   ├── If limit = 11 → Add Fig 10 (persona dimensions)
│   ├── If limit = 12 → Add one of {7, 8, 9}
│   └── If limit ≥ 13 → Include all Reviewer-choice figures
└── NO (limit < 6, e.g., Nature/Science family)
    ├── Keep Must-have: Figs 1, 2, 3, 4, 5 (5 figures)
    ├── Move Fig 19 (φ-sensitivity) to supplementary (text already states the claim)
    ├── Move Fig 20 (flowchart) to supplementary or graphical abstract
    └── Move all Reviewer-choice and Supplementary figures to the supplement
├── YES → Include all Must-have figures (1–5) + select from Reviewer-choice (6–10)
│   ├── If limit = 6 → Add Fig 6 (T-EGR bars) OR Fig 10 (persona dimensions)
│   ├── If limit = 7 → Add Fig 6 + one of {7, 8, 9, 10}
│   ├── If limit = 8 → Add Figs 6 + 8 + 9
│   └── If limit ≥ 9 → Include all Reviewer-choice figures
└── NO (limit < 6, e.g., Nature/Science family)
    ├── Keep Must-have: Figs 1, 2, 3, 4, 5 (5 figures)
    ├── Move Fig 6 (T-EGR) to the cover image or graphical abstract
    └── Move all Reviewer-choice and Supplementary figures to the supplement
```

---

## LaTeX Figure Template (for the AI Drafter)

Use this template for each figure in the LaTeX manuscript:

```latex
\begin{figure}[tbp]
\centering
\includegraphics[width=\textwidth]{figures/figN_NAME.png}
\caption{CAPTION_TEXT}
\label{fig:LABEL}
\begin{flushleft}
\footnotesize
\textit{Note.} DATA_SOURCE. STATISTICAL_DETAIL.
\end{flushleft}
\end{figure}
```

For two-panel figures (e.g., Fig 4, Fig 7, Fig 8), use:

```latex
\begin{figure}[tbp]
\centering
\begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{figures/figN_NAME_panelA.png}
    \caption{Panel A description}
    \label{fig:LABEL_A}
\end{subfigure}
\hfill
\begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{figures/figN_NAME_panelB.png}
    \caption{Panel B description}
    \label{fig:LABEL_B}
\end{subfigure}
\caption{OVERALL_CAPTION}
\label{fig:LABEL}
\end{figure}
```

---

## Colorblind-Safe Palette Reference

All generated figures use the following palette. If a journal requires colorblind-safe figures, verify against this reference:

| Role | Hex | Colorblind-safe? |
|------|-----|------------------|
| Cheap tier | #2E86AB | Yes (blue) |
| Team cells | #A23B72 | Yes (purple) |
| Frontier tier | #F18F01 | Yes (orange) |
| Frontier team | #C73E1D | Caution (red; use with symbol differentiation) |
| Positive / success | #27AE60 | Yes (green) |
| Negative / failure | #E74C3C | Caution (red; pair with ▼ symbol) |
| Neutral / baseline | #95A5A6 | Yes (gray) |

For B&W print: use filled vs. hollow markers, solid vs. dashed lines, and hatching patterns instead of color.

---

## Generation Script Index

| Script | Figures Generated | Runtime |
|--------|-------------------|---------|
| `generate_figures.py` | 1, 2, 4, 5, 6 | ~30 sec |
| `generate_supplementary_figures.py` | 7–18 | ~45 sec |
| `generate_new_figures.py` | 19–22 | ~30 sec |
| Pre-existing (copied) | 3 | N/A |

To regenerate any figure or variation:
```bash
cd /Users/youssefhariri/Documents/app\ 25
python research/orchestration-economics/paper/generate_figures.py
python research/orchestration-economics/paper/generate_supplementary_figures.py
python research/orchestration-economics/paper/generate_new_figures.py
```

For Figure 3 (cost scatter copy):
```bash
cp research/orchestration-economics/results/cost/cost_effectiveness_scatter.png \
   research/orchestration-economics/paper/figures/fig3_cost_scatter.png
cp research/orchestration-economics/results/cost/cost_effectiveness_scatter.pdf \
   research/orchestration-economics/paper/figures/fig3_cost_scatter.pdf


---

## Figure Numbering Crosswalk

The current draft uses this numbering:

| Draft Label | Guide # | File | Section | Priority |
|-------------|---------|------|---------|----------|
| Figure 1 | 1 | `fig1_design_schematic.png` | §3.1 | Must-have |
| Figure 2 | 2 | `fig2_forest_plot.png` | §4.1 | Must-have |
| Figure 3 | 3 | `fig3_cost_scatter.png` | §4.6 | Must-have |
| Figure 4 | 4 | `fig4_gap_recovery.png` | §4.4 | Must-have |
| Figure 5 | 5 | `fig5_code_heatmap.png` | §4.5 | Must-have |
| Figure 6 | 6 | `fig6_tegr_bars.png` | §4.6 | Reviewer choice |
| Figure 7 | 7 | `fig7_cross_family_matrix.png` | §4.4 | Reviewer choice |
| Figure 8 | 8 | `fig8_robustness_loo.png` | §4.7 | Reviewer choice |
| Figure 9 | 9 | `fig9_meta_analysis_forest.png` | §4.7 | Reviewer choice |
| Figure 10 | 10 | `fig10_persona_dimensions.png` | §4.2 | Reviewer choice |
| Figure 11 | 19 | `fig19_phi_sensitivity.png` | §4.6 | Must-have |
| Figure 12 | 20 | `fig20_contingency_rules.png` | §5.1 | Must-have |
| Figure 13 | 21 | `fig21_sequential_boundary.png` | §4.1 | Reviewer choice |
| Figure 14 | 22 | `fig22_persona_radar.png` | §4.2 | Reviewer choice |
| (v14 Fig 14) | 23 | `fig23_study3_family_domain.png` | §4.3 | Must-have — embedded in v14 |

**Note:** Figures 11–18 from the guide (supplementary) are already generated and remain supplementary — they do not need re-numbering unless promoted. The authoritative v14 compiled figure order (15 main-text figures, including fig23) is in `Additional_figures_needed.md` §5.

---

*End of Figure Selection Guide — Updated 2026-08-08*
