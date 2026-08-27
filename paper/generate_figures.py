#!/usr/bin/env python3
"""
Generate all figures for the Economics of Orchestration paper.
Outputs: PNG + PDF for each figure in research/orchestration-economics/paper/figures/
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import seaborn as sns

# Setup paths
BASE = "research/orchestration-economics"
OUTDIR = f"{BASE}/paper/figures"
os.makedirs(OUTDIR, exist_ok=True)

# Style setup
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.dpi'] = 150

CELL_ORDER = ['C-S-P', 'C-S-N', 'C-T-P', 'C-T-N', 'F-S-P', 'F-S-N', 'F-T-P', 'F-T-N']
CELL_LABELS = {
    'C-S-P': 'C-S-P\n(cheap solo + persona)',
    'C-S-N': 'C-S-N\n(cheap solo)',
    'C-T-P': 'C-T-P\n(cheap team + persona)',
    'C-T-N': 'C-T-N\n(cheap team)',
    'F-S-P': 'F-S-P\n(frontier solo + persona)',
    'F-S-N': 'F-S-N\n(frontier solo)',
    'F-T-P': 'F-T-P\n(frontier team + persona)',
    'F-T-N': 'F-T-N\n(frontier team)',
}
CELL_COLORS = {
    'C-S-P': '#2E86AB',  # blue
    'C-S-N': '#2E86AB',
    'C-T-P': '#A23B72',  # purple
    'C-T-N': '#A23B72',
    'F-S-P': '#F18F01',  # orange
    'F-S-N': '#F18F01',
    'F-T-P': '#C73E1D',  # red
    'F-T-N': '#C73E1D',
}

def savefig(name):
    plt.savefig(f"{OUTDIR}/{name}.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{OUTDIR}/{name}.pdf", bbox_inches='tight')
    plt.close()
    print(f"Saved {name}.png + .pdf")


# =============================================================================
# FIGURE 1: 2×2×2 Design Schematic
# =============================================================================
fig, ax = plt.subplots(1, 1, figsize=(10, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_title('Figure 1. Experimental Design: 2 × 2 × 2 Factorial + Apparatus', fontweight='bold', pad=20)

# Title box
title_box = FancyBboxPatch((0.5, 8.8), 9, 0.9, boxstyle="round,pad=0.1", 
                            facecolor='#E8F4F8', edgecolor='#2E86AB', linewidth=2)
ax.add_patch(title_box)
ax.text(5, 9.25, '38 Business Problems × 5 Model Families × 10 Replicates = 1,900 Runs', 
        ha='center', va='center', fontsize=11, fontweight='bold')

# Factor boxes
factors = [
    (1, 6.8, 'TIER', ['Cheap (C)', 'Frontier (F)'], '#D4EDDA', '#28A745'),
    (4, 6.8, 'STRUCTURE', ['Solo (S)', 'Team (T)'], '#FFF3CD', '#FFC107'),
    (7, 6.8, 'PERSONA', ['None (N)', 'Loaded (P)'], '#F8D7DA', '#DC3545'),
]
for x, y, title, levels, fc, ec in factors:
    box = FancyBboxPatch((x, y), 2.2, 1.8, boxstyle="round,pad=0.08", 
                          facecolor=fc, edgecolor=ec, linewidth=2)
    ax.add_patch(box)
    ax.text(x+1.1, y+1.5, title, ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(x+1.1, y+1.0, levels[0], ha='center', va='center', fontsize=9)
    ax.text(x+1.1, y+0.5, levels[1], ha='center', va='center', fontsize=9)

# Arrow down
ax.annotate('', xy=(5, 5.5), xytext=(5, 6.7),
            arrowprops=dict(arrowstyle='->', color='#333', lw=2))
ax.text(5.3, 6.1, 'crossed', ha='left', va='center', fontsize=8, style='italic', color='#666')

# 8 cells grid
cells = [
    ('C-S-N', 0.8, 4.0), ('C-S-P', 3.3, 4.0),
    ('C-T-N', 5.8, 4.0), ('C-T-P', 8.3, 4.0),
    ('F-S-N', 0.8, 2.3), ('F-S-P', 3.3, 2.3),
    ('F-T-N', 5.8, 2.3), ('F-T-P', 8.3, 2.3),
]
for cell, x, y in cells:
    color = CELL_COLORS[cell]
    box = FancyBboxPatch((x, y), 1.8, 1.2, boxstyle="round,pad=0.05",
                          facecolor='white', edgecolor=color, linewidth=2)
    ax.add_patch(box)
    ax.text(x+0.9, y+0.7, cell, ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(x+0.9, y+0.3, f'n={285 if cell.startswith("C") else 190}', 
            ha='center', va='center', fontsize=7, color='#666')

# Apparatus flow
ax.annotate('', xy=(5, 1.8), xytext=(5, 2.2),
            arrowprops=dict(arrowstyle='->', color='#333', lw=2))

# Generator box
gen_box = FancyBboxPatch((1.5, 0.3), 3, 1.2, boxstyle="round,pad=0.08",
                          facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2)
ax.add_patch(gen_box)
ax.text(3, 1.1, 'Generator(s)', ha='center', va='center', fontsize=9, fontweight='bold')
ax.text(3, 0.6, 'builder → critic → refiner', ha='center', va='center', fontsize=7)

# Judge box
judge_box = FancyBboxPatch((5.5, 0.3), 3, 1.2, boxstyle="round,pad=0.08",
                            facecolor='#F3E5F5', edgecolor='#7B1FA2', linewidth=2)
ax.add_patch(judge_box)
ax.text(7, 1.1, 'Judge Panel (blinded)', ha='center', va='center', fontsize=9, fontweight='bold')
ax.text(7, 0.6, '3 judges × 3 prompt variants', ha='center', va='center', fontsize=7)

# Arrow between them
ax.annotate('', xy=(5.5, 0.9), xytext=(4.5, 0.9),
            arrowprops=dict(arrowstyle='->', color='#333', lw=1.5))
ax.text(5, 0.5, 'answer', ha='center', va='center', fontsize=7, color='#666')

# Refinement arrow (Study 2)
ax.annotate('', xy=(3, 0.25), xytext=(3, 1.8),
            arrowprops=dict(arrowstyle='->', color='#28A745', lw=1.5, linestyle='--'))
ax.text(1.8, 1.0, 'Study 2:\nrefinement', ha='center', va='center', fontsize=7, color='#28A745')

savefig('fig1_design_schematic')


# =============================================================================
# FIGURE 2: Forest Plot — Quality by Cell with 95% CIs
# =============================================================================
# Load cell summary data for phi=0.5
df_cells = pd.read_csv(f"{BASE}/results/cost/cell_summary.csv")
df_cells = df_cells[df_cells['phi'] == 0.5].copy()
df_cells['cell'] = df_cells['cell'].astype(str)
df_cells['ci_lower'] = df_cells['mean_quality'] - 1.96 * df_cells['sd_quality'] / np.sqrt(df_cells['n'])
df_cells['ci_upper'] = df_cells['mean_quality'] + 1.96 * df_cells['sd_quality'] / np.sqrt(df_cells['n'])

fig, ax = plt.subplots(figsize=(8, 5))

y_pos = np.arange(len(CELL_ORDER))
means = [df_cells[df_cells['cell'] == c]['mean_quality'].values[0] for c in CELL_ORDER]
ci_low = [df_cells[df_cells['cell'] == c]['ci_lower'].values[0] for c in CELL_ORDER]
ci_high = [df_cells[df_cells['cell'] == c]['ci_upper'].values[0] for c in CELL_ORDER]
colors = [CELL_COLORS[c] for c in CELL_ORDER]

ax.errorbar(means, y_pos, xerr=[np.array(means)-np.array(ci_low), np.array(ci_high)-np.array(means)],
            fmt='o', markersize=10, capsize=5, capthick=2, elinewidth=2,
            color='#333', ecolor='#666')

# Color the points
for i, (m, c) in enumerate(zip(means, colors)):
    ax.scatter(m, i, s=120, c=c, zorder=5, edgecolors='white', linewidth=1.5)

ax.set_yticks(y_pos)
ax.set_yticklabels([CELL_LABELS[c] for c in CELL_ORDER])
ax.set_xlabel('Mean Composite Quality Score (1–5 scale)', fontweight='bold')
ax.set_title('Figure 2. Quality by Experimental Cell with 95% Confidence Intervals', fontweight='bold')
ax.axvline(x=means[CELL_ORDER.index('F-S-N')], color='#F18F01', linestyle='--', alpha=0.5, label='F-S-N baseline')
ax.set_xlim(3.9, 4.8)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)
ax.legend(loc='lower right')

# Add tier separators
ax.axhline(y=3.5, color='#999', linestyle='-', alpha=0.3, linewidth=0.5)
ax.text(4.75, 3.7, 'Cheap', ha='right', va='center', fontsize=8, color='#2E86AB', fontweight='bold')
ax.text(4.75, 3.3, 'Frontier', ha='right', va='center', fontsize=8, color='#C73E1D', fontweight='bold')

savefig('fig2_forest_plot')


# =============================================================================
# FIGURE 4: Gap Recovery — Study 2 Refinement Results
# =============================================================================
with open(f"{BASE}/results/refine_study2_pooled.json") as f:
    refine = json.load(f)

families = ['kimi', 'claude', 'qwen']
# Pre-refinement gaps (from paper: kimi d=-0.71, claude d=-1.42, qwen d=-2.17 for CTP vs FSN)
# Actually let's compute from the H2.1 data
pre_gaps = []
post_gaps = []
recovery_pct = []
for fam in families:
    h2 = refine['H2.1_refined_vs_FSN'][fam]
    post_gap = abs(h2['d'])  # refined vs FSN (negative means refined < FSN)
    # Pre-refinement gap: from paper text §4.3
    pre_map = {'kimi': 0.71, 'claude': 1.42, 'qwen': 2.17}
    pre_gap = pre_map[fam]
    pre_gaps.append(pre_gap)
    post_gaps.append(post_gap)
    recovery_pct.append((1 - post_gap/pre_gap) * 100)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

# Left panel: Gap recovery bars
x = np.arange(len(families))
width = 0.3
bars1 = axes[0].bar(x - width/2, pre_gaps, width, label='Pre-refinement gap', color='#E74C3C', alpha=0.8)
bars2 = axes[0].bar(x + width/2, post_gaps, width, label='Post-refinement gap', color='#3498DB', alpha=0.8)

axes[0].set_ylabel('|Effect size| vs F-S-N baseline', fontweight='bold')
axes[0].set_title('Gap Recovery by Family', fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels([f.title() for f in families])
axes[0].legend(loc='upper right')
axes[0].set_ylim(0, 2.5)
axes[0].grid(axis='y', alpha=0.3)

# Add recovery % labels
for i, (pg, rec) in enumerate(zip(post_gaps, recovery_pct)):
    axes[0].text(i, pg + 0.08, f'{rec:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#27AE60')

# Right panel: Per-dimension gains for refined vs original CTP
# Extract dimension-level data
dims = ['Novelty', 'Usefulness', 'Flexibility', 'Elaboration', 'Cultural Sensitivity']
dim_data = {fam: [] for fam in families}
for fam in families:
    for dim in dims:
        key = f"{fam}:{dim}"
        if key in refine['secondary_refined_vs_original_CTP_per_dim']:
            dim_data[fam].append(refine['secondary_refined_vs_original_CTP_per_dim'][key]['d'])
        else:
            dim_data[fam].append(0)

x2 = np.arange(len(dims))
width2 = 0.25
for i, fam in enumerate(families):
    offset = (i - 1) * width2
    axes[1].bar(x2 + offset, dim_data[fam], width2, label=fam.title(), alpha=0.8)

axes[1].set_ylabel("Cohen's d (refined − original)", fontweight='bold')
axes[1].set_title('Refinement Effect by Dimension', fontweight='bold')
axes[1].set_xticks(x2)
axes[1].set_xticklabels(dims, rotation=15, ha='right')
axes[1].axhline(y=0, color='#333', linewidth=0.8)
axes[1].legend(loc='upper right')
axes[1].grid(axis='y', alpha=0.3)

fig.suptitle('Figure 4. Study 2: Refinement Probe Results', fontweight='bold', fontsize=13, y=1.02)
plt.tight_layout()
savefig('fig4_gap_recovery')


# =============================================================================
# FIGURE 5: Code Prevalence Heatmap (orig/refined/fsn × 13 codes)
# =============================================================================
with open(f"{BASE}/results/qual2_analysis.json") as f:
    qual = json.load(f)

codes = list(qual['prevalence']['kimi']['orig'].keys())
code_labels = {
    'diagnostic_reframe': 'Diagnostic\nreframe',
    'named_concepts': 'Named\nconcepts',
    'assumption_test': 'Assumption\ntesting',
    'concise_maxims': 'Concise\nmaxims',
    'operational_parameters': 'Operational\nparams',
    'cultural_localization': 'Cultural\nlocalization',
    'structured_report': 'Structured\nreport',
    'external_authority': 'External\nauthority',
    'phased_timeline': 'Phased\ntimeline',
    'tables_matrices': 'Tables &\nmatrices',
    'quantified_targets': 'Quantified\ntargets',
    'granular_ops_detail': 'Granular\nops detail',
    'redundancy_bloat': 'Redundancy /\nbloat',
}

# Create a combined heatmap with families as rows and codes as columns
# Structure: 9 rows (3 families × 3 conditions) × 13 codes
families_hm = ['kimi', 'claude', 'qwen']
conditions = ['orig', 'refined', 'fsn']
cond_labels = {'orig': 'Original CTP', 'refined': 'Refined CTP', 'fsn': 'Frontier FSN'}

fig, axes = plt.subplots(1, 3, figsize=(14, 8), sharey=True)

for idx, fam in enumerate(families_hm):
    ax = axes[idx]
    data = np.zeros((len(conditions), len(codes)))
    for i, cond in enumerate(conditions):
        for j, code in enumerate(codes):
            data[i, j] = qual['prevalence'][fam][cond][code]
    
    # Mark kappa-reliable codes
    reliable = qual['kappa_reliable_codes']
    
    im = ax.imshow(data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(np.arange(len(codes)))
    ax.set_xticklabels([code_labels.get(c, c) for c in codes], rotation=45, ha='right', fontsize=8)
    ax.set_yticks(np.arange(len(conditions)))
    ax.set_yticklabels([cond_labels[c] for c in conditions])
    ax.set_title(fam.title(), fontweight='bold', fontsize=11)
    
    # Add text annotations
    for i in range(len(conditions)):
        for j in range(len(codes)):
            val = data[i, j]
            text_color = 'white' if val > 0.6 else '#333'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=7, color=text_color, fontweight='bold')
    
    # Add asterisk for kappa-reliable codes
    for j, code in enumerate(codes):
        if code in reliable:
            ax.text(j, -0.6, '✓', ha='center', va='center', fontsize=10, color='#27AE60', fontweight='bold')

# Shared colorbar
fig.subplots_adjust(right=0.88)
cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.set_label('Prevalence (proportion of texts)', fontweight='bold')

fig.suptitle('Figure 5. Code Prevalence Heatmap: Original, Refined, and Frontier (Study 2)', 
             fontweight='bold', fontsize=13, y=0.98)

savefig('fig5_code_heatmap')


# =============================================================================
# Bonus: T-EGR Bar Chart (could be Figure 6 or supplementary)
# =============================================================================
with open(f"{BASE}/results/cost/cost_effectiveness.json") as f:
    ce = json.load(f)

tegr = ce['t_egr_pooled_mean_per_cell']
tegr_items = [(k, v) for k, v in tegr.items()]
tegr_items.sort(key=lambda x: x[1], reverse=True)

fig, ax = plt.subplots(figsize=(8, 4.5))
cells = [x[0] for x in tegr_items]
values = [x[1] for x in tegr_items]
colors_tegr = [CELL_COLORS[c] for c in cells]

bars = ax.barh(range(len(cells)), values, color=colors_tegr, edgecolor='white', linewidth=1)
ax.set_yticks(range(len(cells)))
ax.set_yticklabels([CELL_LABELS[c] for c in cells])
ax.set_xlabel('T-EGR (quality ratio / cost ratio, F-S-N = 1.0)', fontweight='bold')
ax.set_title('Figure 6. Tiered Efficiency Gain Ratio (T-EGR) by Cell', fontweight='bold')
ax.axvline(x=1.0, color='#333', linestyle='--', alpha=0.5, label='F-S-N baseline = 1.0')
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)
ax.legend(loc='lower right')

# Add value labels
for i, (bar, val) in enumerate(zip(bars, values)):
    ax.text(val + 0.15, i, f'{val:.2f}', va='center', fontsize=9, fontweight='bold')

savefig('fig6_tegr_bars')

print(f"\nAll figures saved to {OUTDIR}/")
