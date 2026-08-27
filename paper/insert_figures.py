#!/usr/bin/env python3
"""Insert figure references into the paper draft."""

with open("research/orchestration-economics/paper/FULL-PAPER-DRAFT.md", "r") as f:
    content = f.read()

# Figure 1: After §3.1, before §3.2
old1 = "al., 2018).\n\n## 3.2 Models evaluated"
new1 = "al., 2018).\n\n![Figure 1. Experimental Design: 2 × 2 × 2 Factorial + Apparatus](figures/fig1_design_schematic.png)\n\n## 3.2 Models evaluated"
content = content.replace(old1, new1, 1)

# Figure 2: After §4.1 Key Takeaway, before §4.2
old2 = "and the trade is negative on net.\n\n## 4.2 The persona penalty"
new2 = "and the trade is negative on net.\n\n![Figure 2. Quality by Experimental Cell with 95% Confidence Intervals](figures/fig2_forest_plot.png)\n\n## 4.2 The persona penalty"
content = content.replace(old2, new2, 1)

# Figure 4: After §4.4 Key Takeaway, before §4.5
old4 = "never achieves paired superiority over the frontier.\n\n## 4.5 Study 2"
new4 = "never achieves paired superiority over the frontier.\n\n![Figure 4. Study 2: Refinement Probe Results](figures/fig4_gap_recovery.png)\n\n## 4.5 Study 2"
content = content.replace(old4, new4, 1)

# Figure 5: After §4.5 Key Takeaway, before §4.6
old5 = "Refinement cannot manufacture density.\n\n## 4.6 Economic analysis"
new5 = "Refinement cannot manufacture density.\n\n![Figure 5. Code Prevalence Heatmap: Original, Refined, and Frontier (Study 2)](figures/fig5_code_heatmap.png)\n\n## 4.6 Economic analysis"
content = content.replace(old5, new5, 1)

# Figure 6: After §4.6 table, before §4.7
old6 = "| F-T-P | 190 | 0.3044 | 4.370 | 0.27 |\n\nThe Pareto frontier is **identical across all three φ**"
new6 = "| F-T-P | 190 | 0.3044 | 4.370 | 0.27 |\n\n![Figure 6. Tiered Efficiency Gain Ratio (T-EGR) by Cell](figures/fig6_tegr_bars.png)\n\nThe Pareto frontier is **identical across all three φ**"
content = content.replace(old6, new6, 1)

with open("research/orchestration-economics/paper/FULL-PAPER-DRAFT.md", "w") as f:
    f.write(content)

print("Figure references inserted successfully.")
