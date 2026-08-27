#!/usr/bin/env python3
"""
Generate comprehensive supplementary figures for the Economics of Orchestration paper.
Covers: cross-model comparisons, robustness, meta-analysis, qualitative studies, LMM, etc.
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

BASE = "research/orchestration-economics"
OUTDIR = f"{BASE}/paper/figures"
os.makedirs(OUTDIR, exist_ok=True)

plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.dpi'] = 150

def savefig(name):
    plt.savefig(f"{OUTDIR}/{name}.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{OUTDIR}/{name}.pdf", bbox_inches='tight')
    plt.close()
    print(f"  Saved {name}")

# Load all JSON data sources
with open(f"{BASE}/results/interim2_analysis.json") as f:
    main = json.load(f)
with open(f"{BASE}/results/exploratory_analysis.json") as f:
    expl = json.load(f)
with open(f"{BASE}/results/cross_family.json") as f:
    xf = json.load(f)
with open(f"{BASE}/results/pilot_v2_analysis.json") as f:
    pilot = json.load(f)
with open(f"{BASE}/results/interim1_sequential_analysis.json") as f:
    interim1 = json.load(f)
with open(f"{BASE}/results/qual2_analysis.json") as f:
    qual = json.load(f)
with open(f"{BASE}/results/qual2_kappa.json") as f:
    kappa = json.load(f)
with open(f"{BASE}/results/cost/cost_effectiveness.json") as f:
    ce = json.load(f)

# ============================================================
# FIG 7: Cross-Family Comparison Matrix (original + refined)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Original CTP vs cross-family FSN
orig = xf['A_original_ctp_vs_cross_family_fsn']
pairs_a = list(orig.keys())
d_vals_a = [orig[p]['d'] for p in pairs_a]
labels_a = [p.replace('->', ' → ') for p in pairs_a]

y_pos = np.arange(len(labels_a))
colors_a = ['#E74C3C' if d < 0 else '#27AE60' for d in d_vals_a]
bars = axes[0].barh(y_pos, d_vals_a, color=colors_a, edgecolor='white', height=0.6)
axes[0].set_yticks(y_pos)
axes[0].set_yticklabels(labels_a)
axes[0].axvline(x=0, color='#333', linewidth=0.8)
axes[0].set_xlabel("Cohen's d (negative = worse than target FSN)", fontweight='bold')
axes[0].set_title('A. Original CTP vs Cross-Family FSN', fontweight='bold')
axes[0].grid(axis='x', alpha=0.3)
for bar, d in zip(bars, d_vals_a):
    axes[0].text(d - 0.05 if d < 0 else d + 0.05, bar.get_y() + bar.get_height()/2,
                f'{d:.2f}', ha='right' if d < 0 else 'left', va='center', fontsize=8, fontweight='bold')

# Panel B: Refined CTP vs cross-family FSN
ref = xf['B_refined_vs_cross_family_fsn']
pairs_b = list(ref.keys())
d_vals_b = [ref[p]['d'] for p in pairs_b]
labels_b = [p.replace('->', ' → ') for p in pairs_b]

colors_b = ['#E74C3C' if d < 0 else '#27AE60' for d in d_vals_b]
bars = axes[1].barh(np.arange(len(labels_b)), d_vals_b, color=colors_b, edgecolor='white', height=0.6)
axes[1].set_yticks(np.arange(len(labels_b)))
axes[1].set_yticklabels(labels_b)
axes[1].axvline(x=0, color='#333', linewidth=0.8)
axes[1].set_xlabel("Cohen's d (negative = worse than target FSN)", fontweight='bold')
axes[1].set_title('B. Refined CTP vs Cross-Family FSN', fontweight='bold')
axes[1].grid(axis='x', alpha=0.3)
for bar, d in zip(bars, d_vals_b):
    axes[1].text(d - 0.05 if d < 0 else d + 0.05, bar.get_y() + bar.get_height()/2,
                f'{d:.2f}', ha='right' if d < 0 else 'left', va='center', fontsize=8, fontweight='bold')

fig.suptitle('Figure 7. Cross-Family Comparison Matrix (Study 2)', fontweight='bold', fontsize=13, y=1.02)
plt.tight_layout()
savefig('fig7_cross_family_matrix')

# ============================================================
# FIG 8: Robustness Checks — Leave-One-Out Sensitivity
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Leave-one-family-out
lofo = main['A2_5_leave_one_family_out']
full_d = lofo['full_d']
folds_fam = lofo['folds']

fam_names = [f['removed'].title() for f in folds_fam]
fam_ds = [f['d'] for f in folds_fam]
fam_ps = [f['p'] for f in folds_fam]

y_pos = np.arange(len(fam_names))
xerr_vals = [abs(f['d'] - full_d) for f in folds_fam]
axes[0].errorbar(fam_ds, y_pos, fmt='o', markersize=10, color='#2E86AB',
                xerr=xerr_vals, capsize=5, capthick=2, elinewidth=2, ecolor='#999')
axes[0].scatter(fam_ds, y_pos, s=120, c='#2E86AB', zorder=5, edgecolors='white', linewidth=1.5)
axes[0].axvline(x=full_d, color='#E74C3C', linestyle='--', linewidth=1.5, label=f'Full d = {full_d:.3f}')
axes[0].set_yticks(y_pos)
axes[0].set_yticklabels(fam_names)
axes[0].set_xlabel("Cohen's d for tier × structure interaction", fontweight='bold')
axes[0].set_title('A. Leave-One-Family-Out', fontweight='bold')
axes[0].invert_yaxis()
axes[0].grid(axis='x', alpha=0.3)
axes[0].legend(loc='lower right')
for i, (d, p) in enumerate(zip(fam_ds, fam_ps)):
    sig = '*' if p < 0.05 else 'n.s.'
    axes[0].text(d - 0.02, i + 0.25, f'p={p:.3f} {sig}', ha='right', va='bottom', fontsize=7, color='#666')

# Panel B: Leave-one-problem-out (sample of 10)
loop = main['A2_6_leave_one_problem_out']['folds'][:10]
prob_names = [f['removed'].replace('Business_Problem_', 'P') for f in loop]
prob_ds = [f['d'] for f in loop]

y_pos = np.arange(len(prob_names))
axes[1].scatter(prob_ds, y_pos, s=80, c='#A23B72', zorder=5, edgecolors='white', linewidth=1)
axes[1].axvline(x=full_d, color='#E74C3C', linestyle='--', linewidth=1.5, label=f'Full d = {full_d:.3f}')
axes[1].set_yticks(y_pos)
axes[1].set_yticklabels(prob_names)
axes[1].set_xlabel("Cohen's d for tier × structure interaction", fontweight='bold')
axes[1].set_title('B. Leave-One-Problem-Out (sample)', fontweight='bold')
axes[1].invert_yaxis()
axes[1].grid(axis='x', alpha=0.3)
axes[1].legend(loc='lower right')
axes[1].set_xlim(-0.35, -0.15)

fig.suptitle('Figure 8. Robustness: Leave-One-Out Sensitivity (A2 Battery)', fontweight='bold', fontsize=13, y=1.02)
plt.tight_layout()
savefig('fig8_robustness_loo')

# ============================================================
# FIG 9: Meta-Analysis Forest Plot — Per-Family Interaction
# ============================================================
meta = expl['A3_4_meta_analysis']
per_fam = meta['per_family']

fig, ax = plt.subplots(figsize=(8, 4.5))

fams = list(per_fam.keys())
meta_ds = [per_fam[f]['d'] for f in fams]
meta_ses = [per_fam[f]['se_boot'] for f in fams]

y_pos = np.arange(len(fams))
ax.errorbar(meta_ds, y_pos, xerr=[1.96*s for s in meta_ses], fmt='o', markersize=10,
            color='#2E86AB', capsize=5, capthick=2, elinewidth=2, ecolor='#666')
ax.scatter(meta_ds, y_pos, s=120, c='#2E86AB', zorder=5, edgecolors='white', linewidth=1.5)

ax.axvline(x=meta['pooled_d'], color='#E74C3C', linestyle='--', linewidth=2,
           label=f"Pooled d = {meta['pooled_d']:.3f} (I² = {meta['I2_pct']:.1f}%, τ² = {meta['tau2']:.3f})")

ax.set_yticks(y_pos)
ax.set_yticklabels([f.title() for f in fams])
ax.set_xlabel("Cohen's d for tier × structure interaction", fontweight='bold')
ax.set_title('Figure 9. Random-Effects Meta-Analysis: Interaction by Family (A3.4)', fontweight='bold')
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)
ax.legend(loc='lower right')
ax.set_xlim(-0.8, 0.2)

for i, f in enumerate(fams):
    d = per_fam[f]['d']
    se = per_fam[f]['se_boot']
    ci_low = d - 1.96*se
    ci_high = d + 1.96*se
    sig = '***' if ci_high < 0 else 'n.s.'
    ax.text(ci_low - 0.03, i, sig, ha='right', va='center', fontsize=8, color='#666')

savefig('fig9_meta_analysis_forest')

# ============================================================
# FIG 10: Persona Dimension Decomposition
# ============================================================
pdims = expl['A3_5_persona_dimensions']

fig, ax = plt.subplots(figsize=(9, 4.5))

dims = [p['dimension'] for p in pdims]
d_vals = [p['d_P_minus_N'] for p in pdims]
sigs = [p['sig_fdr'] for p in pdims]

x_pos = np.arange(len(dims))
colors = ['#27AE60' if d > 0 else '#E74C3C' for d in d_vals]
bars = ax.bar(x_pos, d_vals, color=colors, edgecolor='white', width=0.6)

ax.axhline(y=0, color='#333', linewidth=0.8)
ax.set_xticks(x_pos)
ax.set_xticklabels(dims, rotation=15, ha='right')
ax.set_ylabel("Cohen's d (Persona − No Persona)", fontweight='bold')
ax.set_title('Figure 10. Persona Effect by Quality Dimension (FDR-corrected)', fontweight='bold')
ax.grid(axis='y', alpha=0.3)

for bar, d, sig in zip(bars, d_vals, sigs):
    label = f'{d:.2f}'
    if sig:
        label += ' *'
    ax.text(bar.get_x() + bar.get_width()/2, d + 0.05 if d > 0 else d - 0.08,
            label, ha='center', va='bottom' if d > 0 else 'top', fontsize=9, fontweight='bold')

ax.text(0.98, 0.98, '* p_FDR < 0.05', transform=ax.transAxes, ha='right', va='top',
        fontsize=9, color='#666', style='italic')

savefig('fig10_persona_dimensions')

# ============================================================
# FIG 11: Pilot v1 vs v2 Stability
# ============================================================
fig, ax = plt.subplots(figsize=(9, 5))

cells_pv = ['C-S-N', 'C-S-P', 'C-T-N', 'C-T-P', 'F-S-N', 'F-S-P', 'F-T-N', 'F-T-P']
v1_means = [pilot['cell_means_v1'][c]['mean'] for c in cells_pv if c in pilot['cell_means_v1']]
v2_means = [pilot['cell_means_v2'][c]['mean'] for c in cells_pv if c in pilot['cell_means_v2']]
v1_stds = [pilot['cell_means_v1'][c]['std'] for c in cells_pv if c in pilot['cell_means_v1']]
v2_stds = [pilot['cell_means_v2'][c]['std'] for c in cells_pv if c in pilot['cell_means_v2']]
valid_cells = [c for c in cells_pv if c in pilot['cell_means_v1'] and c in pilot['cell_means_v2']]

x = np.arange(len(valid_cells))
width = 0.35

bars1 = ax.bar(x - width/2, v1_means, width, yerr=v1_stds, capsize=4, label='Pilot v1', color='#3498DB', alpha=0.8)
bars2 = ax.bar(x + width/2, v2_means, width, yerr=v2_stds, capsize=4, label='Pilot v2', color='#E74C3C', alpha=0.8)

ax.set_xticks(x)
ax.set_xticklabels(valid_cells, rotation=0)
ax.set_ylabel('Mean Composite Quality', fontweight='bold')
ax.set_title(f"Figure 11. Pilot Replication Stability (v1 vs v2, r = {pilot['v1_vs_v2']['pearson_r']:.3f})", fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(3.8, 4.8)

ax.text(0.02, 0.02, f"Mean shift (v2 − v1): +{pilot['v1_vs_v2']['mean_shift_v2_minus_v1']:.3f}",
        transform=ax.transAxes, ha='left', va='bottom', fontsize=9, color='#666',
        bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))

savefig('fig11_pilot_stability')

# ============================================================
# FIG 12: Length-Quality Correlation by Family
# ============================================================
lq = pilot['length_quality_r_v2']
fig, ax = plt.subplots(figsize=(8, 4.5))

fam_lq = [(k, v['r_loglen_quality'], v['p']) for k, v in lq.items() if k != 'ALL']
fam_names_lq = [f.title() for f, _, _ in fam_lq]
r_vals = [r for _, r, _ in fam_lq]
p_vals = [p for _, _, p in fam_lq]

x = np.arange(len(fam_names_lq))
colors = ['#27AE60' if p < 0.05 else '#95A5A6' for p in p_vals]
bars = ax.bar(x, r_vals, color=colors, edgecolor='white', width=0.6)

ax.axhline(y=0, color='#333', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(fam_names_lq)
ax.set_ylabel('Pearson r (log(length) vs quality)', fontweight='bold')
ax.set_title('Figure 12. Length-Quality Correlation by Family (Pilot v2)', fontweight='bold')
ax.grid(axis='y', alpha=0.3)

for bar, r, p in zip(bars, r_vals, p_vals):
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
    ax.text(bar.get_x() + bar.get_width()/2, r + 0.02 if r > 0 else r - 0.04,
            f'{r:.3f}\n{sig}', ha='center', va='bottom' if r > 0 else 'top', fontsize=8)

ax.text(0.98, 0.98, f"Pooled: r = {lq['ALL']['r_loglen_quality']:.3f}",
        transform=ax.transAxes, ha='right', va='top', fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#E8F8F5', alpha=0.8))

savefig('fig12_length_quality')

# ============================================================
# FIG 13: LMM Coefficient Plot (Exploratory Analysis)
# ============================================================
fe = expl['A3_1_lmm']['fe']
fig, ax = plt.subplots(figsize=(8, 5))

terms = list(fe.keys())
coefs = [fe[t]['coef'] for t in terms]
pvals = [fe[t]['p'] for t in terms]

ses_approx = [abs(c) / (2 * (0.5 - abs(0.5 - p) + 0.001)) for c, p in zip(coefs, pvals)]
ci_lower = [c - 1.96*s for c, s in zip(coefs, ses_approx)]
ci_upper = [c + 1.96*s for c, s in zip(coefs, ses_approx)]

y_pos = np.arange(len(terms))
ax.errorbar(coefs, y_pos, xerr=[np.array(coefs)-np.array(ci_lower), np.array(ci_upper)-np.array(coefs)],
            fmt='o', markersize=8, capsize=5, capthick=2, elinewidth=2, color='#2E86AB', ecolor='#666')
ax.scatter(coefs, y_pos, s=100, c='#2E86AB', zorder=5, edgecolors='white', linewidth=1.5)
ax.axvline(x=0, color='#E74C3C', linestyle='--', linewidth=1)

ax.set_yticks(y_pos)
ax.set_yticklabels(terms)
ax.set_xlabel('Coefficient (quality units)', fontweight='bold')
ax.set_title('Figure 13. Exploratory LMM Coefficients (A3.1)', fontweight='bold')
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

for i, (c, p) in enumerate(zip(coefs, pvals)):
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
    ax.text(c + 0.01, i - 0.25, f'p={p:.4f} {sig}', ha='left', va='top', fontsize=7, color='#666')

savefig('fig13_lmm_coefficients')

# ============================================================
# FIG 14: Kappa Reliability Plot
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))

items = list(kappa['per_item'].keys())
kappas = [kappa['per_item'][i]['kappa'] for i in items]
pct_agrees = [kappa['per_item'][i]['pct_agree'] for i in items]

item_labels = {
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

labels = [item_labels.get(i, i) for i in items]
x = np.arange(len(items))

ax2 = ax.twinx()

bars = ax.bar(x, kappas, color=['#27AE60' if k >= 0.7 else '#E74C3C' for k in kappas],
              edgecolor='white', width=0.6, alpha=0.8, label="Cohen's κ")
ax2.scatter(x, pct_agrees, s=80, c='#3498DB', zorder=5, marker='D', label='% Agreement')

ax.axhline(y=0.7, color='#F39C12', linestyle='--', linewidth=1.5, label='κ = 0.70 gate')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
ax.set_ylabel("Cohen's κ", fontweight='bold', color='#27AE60')
ax2.set_ylabel('% Agreement', fontweight='bold', color='#3498DB')
ax.set_title("Figure 14. Inter-Coder Reliability by Code (κ = 0.824 pooled, n = 90)", fontweight='bold')
ax.set_ylim(0, 1.15)
ax2.set_ylim(75, 105)

lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

savefig('fig14_kappa_reliability')

# ============================================================
# FIG 15: Qualitative Convergence Summary
# ============================================================
fig, ax = plt.subplots(figsize=(8, 4.5))

families_q = ['kimi', 'claude', 'qwen']
toward = [qual['convergence_rq2'][f]['toward'] for f in families_q]
away = [qual['convergence_rq2'][f]['away'] for f in families_q]
flat = [qual['convergence_rq2'][f]['flat'] for f in families_q]

x = np.arange(len(families_q))
width = 0.25

bars1 = ax.bar(x - width, toward, width, label='Toward frontier', color='#27AE60', alpha=0.8)
bars2 = ax.bar(x, away, width, label='Away from frontier', color='#E74C3C', alpha=0.8)
bars3 = ax.bar(x + width, flat, width, label='Unchanged', color='#95A5A6', alpha=0.8)

ax.set_xticks(x)
ax.set_xticklabels([f.title() for f in families_q])
ax.set_ylabel('Number of codes (out of 13)', fontweight='bold')
ax.set_title('Figure 15. Refinement Convergence: Toward / Away / Flat by Family', fontweight='bold')
ax.legend(loc='upper right')
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 12)

for i, f in enumerate(families_q):
    share = qual['convergence_rq2'][f]['share_toward']
    ax.text(i, 11, f'{share:.0%}', ha='center', va='top', fontsize=10, fontweight='bold', color='#27AE60')

savefig('fig15_convergence_summary')

# ============================================================
# FIG 16: ANOVA Partial Eta-Squared
# ============================================================
fig, ax = plt.subplots(figsize=(8, 4.5))

anova = main['A2_3_anova']['terms']
terms_anova = list(anova.keys())
eta2s = [anova[t]['partial_eta2'] for t in terms_anova]
pvals_anova = [anova[t]['p'] for t in terms_anova]

term_labels = {
    'C(tier)': 'Tier',
    'C(structure)': 'Structure',
    'C(persona)': 'Persona',
    'C(tier):C(structure)': 'Tier × Structure',
    'C(tier):C(persona)': 'Tier × Persona',
    'C(structure):C(persona)': 'Structure × Persona',
    'C(tier):C(structure):C(persona)': 'Tier × Str × Per',
}

labels_a = [term_labels.get(t, t) for t in terms_anova]
x = np.arange(len(labels_a))

bars = ax.bar(x, eta2s, color=['#E74C3C' if p < 0.05 else '#95A5A6' for p in pvals_anova],
              edgecolor='white', width=0.6)

ax.set_xticks(x)
ax.set_xticklabels(labels_a, rotation=30, ha='right')
ax.set_ylabel('Partial η²', fontweight='bold')
ax.set_title('Figure 16. ANOVA Effect Sizes (Partial η²)', fontweight='bold')
ax.grid(axis='y', alpha=0.3)

for bar, e, p in zip(bars, eta2s, pvals_anova):
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
    ax.text(bar.get_x() + bar.get_width()/2, e + 0.002, f'{e:.4f}\n{sig}',
            ha='center', va='bottom', fontsize=8)

savefig('fig16_anova_eta2')

# ============================================================
# FIG 17: Empirical Bayes Shrinkage
# ============================================================
fig, ax = plt.subplots(figsize=(8, 4.5))

shrink = expl['A3_3_empirical_bayes']
shrunk = shrink['shrunk_d']
raw_ds = expl['A3_4_meta_analysis']['per_family']

fams_sh = list(shrunk.keys())
raw_vals = [raw_ds[f]['d'] for f in fams_sh]
shrunk_vals = [shrunk[f] for f in fams_sh]

x = np.arange(len(fams_sh))
width = 0.35

bars1 = ax.bar(x - width/2, raw_vals, width, label='Raw d', color='#3498DB', alpha=0.8)
bars2 = ax.bar(x + width/2, shrunk_vals, width, label='Empirical-Bayes shrunk', color='#E74C3C', alpha=0.8)

ax.axhline(y=shrink['pooled_d'], color='#27AE60', linestyle='--', linewidth=2,
           label=f"Pooled d = {shrink['pooled_d']:.3f}")
ax.set_xticks(x)
ax.set_xticklabels([f.title() for f in fams_sh])
ax.set_ylabel("Cohen's d", fontweight='bold')
ax.set_title('Figure 17. Empirical-Bayes Shrinkage: Raw vs Shrunk Estimates (A3.3)', fontweight='bold')
ax.legend(loc='lower right')
ax.grid(axis='y', alpha=0.3)

savefig('fig17_eb_shrinkage')

# ============================================================
# FIG 18: T-EGR Radar Chart
# ============================================================
fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

tegr = ce['t_egr_pooled_mean_per_cell']
cells_r = list(tegr.keys())
values_r = list(tegr.values())

cells_r, values_r = zip(*sorted(zip(cells_r, values_r), key=lambda x: x[1], reverse=True))

angles = np.linspace(0, 2*np.pi, len(cells_r), endpoint=False).tolist()
values_r = list(values_r) + [values_r[0]]
angles += angles[:1]

ax.plot(angles, values_r, 'o-', linewidth=2, color='#2E86AB')
ax.fill(angles, values_r, alpha=0.25, color='#2E86AB')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(cells_r)
ax.set_ylim(0, max(values_r) * 1.1)
ax.set_title('Figure 18. T-EGR Radar Chart (Pooled, F-S-N = 1.0)', fontweight='bold', pad=20)

savefig('fig18_tegr_radar')

print(f"\n=== All supplementary figures saved to {OUTDIR}/ ===")
