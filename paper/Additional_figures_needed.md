# Additional Figures Needed — Economics of Orchestration Paper

**Date:** 2026-08-08  
**Status:** ✅ ALL ITEMS COMPLETE  
**Audience:** AI figure generation agent  
**Source audit:** FULL-PAPER-DRAFT.md (v1, 1007 lines) cross-referenced with FIGURE-SELECTION-GUIDE.md

---

## 1. Critical: Missing Figure Insertion ✅ COMPLETE

### Figure 3 — Cost-Effectiveness Frontier Scatter

- **Status:** ✅ Generated, copied to `paper/figures/fig3_cost_scatter.{png,pdf}`, and **embedded** in the paper draft at §4.6.
- **Action taken:** Copied from `results/cost/cost_effectiveness_scatter.{png,pdf}` → `paper/figures/fig3_cost_scatter.{png,pdf}`.
- **Embedding:** Inserted after the cell-means table in §4.6, before Figure 6.
- **Caption:**
  > Figure 3. Cost–quality scatter plot with Pareto frontier (dashed line, φ = 0.50). Error bars show ±1 SD on both axes. Diamond markers show the three refined CTP points from Study 2 (kimi: $0.065, quality 4.585; claude: $0.198, quality 4.559; qwen: $0.017, quality 4.398). The frontier {C-S-P, C-S-N, C-T-N, F-S-N, F-T-N} is stable across the full φ sensitivity panel.

---

## 2. Recommended: Figures Already Generated (fig7–fig10) ✅ CONFIRMED

These figures are generated and referenced in the FIGURE-SELECTION-GUIDE.md. The v2 draft will add inline references.

| # | Figure | File | Placement in v2 | Status |
|---|--------|------|-----------------|--------|
| 7 | Cross-family matrix | `figures/fig7_cross_family_matrix.png` | §4.4 (after gap recovery paragraph) | ✅ Exists |
| 8 | Robustness LOO | `figures/fig8_robustness_loo.png` | §4.7 (robustness checks) | ✅ Exists |
| 9 | Meta-analysis forest | `figures/fig9_meta_analysis_forest.png` | §4.7 (after meta-analysis paragraph) | ✅ Exists |
| 10 | Persona dimensions | `figures/fig10_persona_dimensions.png` | §4.2 (persona penalty) | ✅ Exists |

---

## 3. New Figures to Generate ✅ ALL COMPLETE

### Figure 19 — φ-Sensitivity Three-Panel Scatter ✅

- **Status:** ✅ Generated and embedded in §4.6.
- **File:** `paper/figures/fig19_phi_sensitivity.{png,pdf}`
- **Data source:** `results/cost/cell_summary.csv` (all three φ values: 0.25, 0.50, 0.75)
- **Layout:** 1×3 subplots, shared axes, Pareto frontier highlighted in each panel
- **Caption:**
  > Figure 19. Pareto frontier stability across the price-assumption sensitivity panel. Left: φ = 0.25 (input-heavy blend). Center: φ = 0.50 (primary analysis). Right: φ = 0.75 (output-heavy blend). The frontier set {C-S-P, C-S-N, C-T-N, F-S-N, F-T-N} is identical in all three panels, satisfying the pre-registered cross-φ stability rule.
- **Embedding:** §4.6, after Pareto discussion paragraph.

### Figure 20 — Summary Decision Flowchart (Practitioner Contingency Rules) ✅

- **Status:** ✅ Generated and embedded in §5.1.
- **File:** `paper/figures/fig20_contingency_rules.{png,pdf}`
- **Content:** Flowchart with START → budget tier → coverage/density questions → cell recommendations with T-EGR values + warning box for F-T cells.
- **Caption:**
  > Figure 20. Practitioner contingency rules. Decision flowchart mapping budget tier and task type to the recommended orchestration cell, with expected T-EGR. Derived from the §5.1 contingency model.
- **Embedding:** §5.1, after contingency model paragraph.

### Figure 21 — Sequential Analysis Boundary Plot ✅

- **Status:** ✅ Generated and embedded in §4.1.
- **File:** `paper/figures/fig21_sequential_boundary.{png,pdf}`
- **Data source:** Protocol 03 spending function + interim analysis z-scores
- **Layout:** OBF upper/lower boundaries with shaded continuation region; interim 1 at info fraction 0.2 (t = −1.63, continue); interim 2 at 1.0 (z = −2.447, boundary crossed, H1 supported).
- **Caption:**
  > Figure 21. Sequential analysis with O'Brien–Fleming spending function. The test statistic z = −2.447 crosses the interim-2 boundary |z| ≥ 1.977 (dashed line). The shaded region is the continuation region. The pre-registered decision is to stop and report H1 as supported.
- **Embedding:** §4.1, after Key Takeaway paragraph and before Figure 2.

### Figure 22 — Dimension-Level Radar: Persona vs. No-Persona (All Cells) ✅

- **Status:** ✅ Generated and embedded in §4.2.
- **File:** `paper/figures/fig22_persona_radar.{png,pdf}`
- **Data source:** `results/cost/cell_summary.csv` (dimension means by cell)
- **Layout:** Two overlaid radar polygons (P = red dashed, N = blue solid) on 5 axes (Novelty, Usefulness, Flexibility, Elaboration, Cultural Sensitivity)
- **Caption:**
  > Figure 22. Quality-dimension radar for persona-loaded (red, dashed) versus no-persona (blue, solid) cells. The persona polygon is visibly smaller on Usefulness and Elaboration, slightly larger on Novelty — the visual signature of the style-over-substance tradeoff.
- **Embedding:** §4.2, after Key Takeaway paragraph and before §4.3.

---

## 4. Variations of Existing Figures (Optional, On-Demand)

Generate these only if the author or reviewer requests them. See FIGURE-SELECTION-GUIDE.md for detailed variation specs.

| Base Fig | Variation | When to Generate | Status |
|----------|-----------|-----------------|--------|
| Fig 2 (forest) | Family-faceted (5 small multiples) | If reviewer asks for family heterogeneity | ⏸️ On demand |
| Fig 3 (scatter) | Three-panel φ comparison | Superseded by new Fig 19 above | ✅ Done (Fig 19) |
| Fig 4 (gap recovery) | With G2 gate annotation (d=0.20 dashed line) | If reviewer questions G2 failure | ⏸️ On demand |
| Fig 5 (heatmap) | Simplified (κ-reliable codes only, 7 codes) | If strict figure space | ⏸️ On demand |
| Fig 8 (LOO) | Full 19-fold problem LOO | If reviewer asks for completeness | ⏸️ On demand |

---

## 5. Figure Numbering Crosswalk

The current draft uses this numbering (after v2 insertions):

| Draft Label | Guide # | File | Section | Status |
|-------------|---------|------|---------|--------|
| Figure 1 | 1 | `fig1_design_schematic.png` | §3.1 | ✅ |
| Figure 2 | 2 | `fig2_forest_plot.png` | §4.1 | ✅ |
| Figure 3 | 3 | `fig3_cost_scatter.png` | §4.6 | ✅ Embedded |
| Figure 4 | 4 | `fig4_gap_recovery.png` | §4.4 | ✅ |
| Figure 5 | 5 | `fig5_code_heatmap.png` | §4.5 | ✅ |
| Figure 6 | 6 | `fig6_tegr_bars.png` | §4.6 | ✅ |
| Figure 7 | 7 | `fig7_cross_family_matrix.png` | §4.4 | ✅ |
| Figure 8 | 8 | `fig8_robustness_loo.png` | §4.7 | ✅ |
| Figure 9 | 9 | `fig9_meta_analysis_forest.png` | §4.7 | ✅ |
| Figure 10 | 10 | `fig10_persona_dimensions.png` | §4.2 | ✅ |
| Figure 11 | 19 (new) | `fig19_phi_sensitivity.png` | §4.6 | ✅ Generated & Embedded |
| Figure 12 | 20 (new) | `fig20_contingency_rules.png` | §5.1 | ✅ Generated & Embedded |
| Figure 13 | 21 (new) | `fig21_sequential_boundary.png` | §4.1 | ✅ Generated & Embedded |
| Figure 14 | 22 (new) | `fig22_persona_radar.png` | §4.2 | ✅ Generated & Embedded |

**Note:** Figures 11–18 from the guide (supplementary) are already generated and remain supplementary.

---

## 6. Generation Scripts

- `paper/generate_figures.py` — core figures (1, 2, 4, 5, 6)
- `paper/generate_supplementary_figures.py` — supplementary (7–18)
- `paper/generate_new_figures.py` — new figures (19–22)

Regenerate existing figures:
```bash
cd /Users/youssefhariri/Documents/app\ 25
python research/orchestration-economics/paper/generate_figures.py
python research/orchestration-economics/paper/generate_supplementary_figures.py
python research/orchestration-economics/paper/generate_new_figures.py
```

---

## Summary: Action Items

| Priority | Action | Figures | Status |
|----------|--------|---------|--------|
| **Immediate** | Copy Fig 3 (cost scatter) to `figures/` | Fig 3 | ✅ Complete |
| **Must-generate** | φ-sensitivity three-panel scatter | Fig 19 | ✅ Complete |
| **Must-generate** | Practitioner contingency flowchart | Fig 20 | ✅ Complete |
| **Should-generate** | Sequential analysis boundary plot | Fig 21 | ✅ Complete |
| **Nice-to-have** | Persona radar overlay | Fig 22 | ✅ Complete |
| **On-demand** | Variations of existing (see §4) | Various | ⏸️ Pending request |

**Total figures now in `paper/figures/`:** 44 files (22 PNG + 22 PDF). All 22 figures from the numbering scheme exist and are embedded where specified.

---

*End of Additional Figures Needed — All action items complete.*
