"""Simplified Study-2 code figure: dumbbell chart of original -> refined
prevalence per code, frontier prevalence as a marker. One panel per family.
Source: results/qual2_analysis.json (prevalence block).
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot
setup_plot()
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "FULL-PAPER-DRAFT-BUSINESS-v14.1_with_figures"
q = json.load(open(ROOT / "results" / "qual2_analysis.json"))

RQ = {  # codebook grouping (Protocol 10)
    "insight": ["diagnostic_reframe", "named_concepts", "assumption_test",
                "concise_maxims", "cultural_localization", "external_authority"],
    "structure": ["operational_parameters", "structured_report", "phased_timeline",
                  "tables_matrices", "quantified_targets", "granular_ops_detail"],
    "bloat": ["redundancy_bloat"],
}
GROUP_LABEL = {"insight": "INSIGHT", "structure": "STRUCTURE", "bloat": "BLOAT"}
FAMS = ["kimi", "claude", "qwen"]
FAM_LABEL = {"kimi": "Kimi", "claude": "Claude", "qwen": "Qwen"}

codes = RQ["insight"] + RQ["structure"] + RQ["bloat"]
labels = [c.replace("_", " ") for c in codes]

fig, axes = plt.subplots(1, 3, figsize=(13.5, 5.6), sharey=True)
for ax, fam in zip(axes, FAMS):
    prev = q["prevalence"][fam]
    y = list(range(len(codes)))[::-1]
    for yi, code in zip(y, codes):
        o, r, f = prev["orig"][code], prev["refined"][code], prev["fsn"][code]
        ax.plot([o, r], [yi, yi], color="gray", lw=1.5, zorder=1)
        ax.scatter(o, yi, marker="o", s=55, color="tab:blue", zorder=2)
        ax.scatter(r, yi, marker="o", s=55, color="tab:orange", zorder=3)
        ax.scatter(f, yi, marker="D", s=42, color="black", zorder=4)
    ax.set_yticks(y, labels, fontsize=9)
    # group separators
    ax.axhline(len(RQ["structure"]) + 0.5, color="lightgray", lw=1)
    ax.axhline(len(RQ["structure"]) + len(RQ["insight"]) + 0.5, color="lightgray", lw=1)
    ax.text(1.02, len(codes) - 2.5, "INSIGHT", fontsize=8, color="gray", rotation=90, va="center")
    ax.text(1.02, len(RQ["structure"]) + 0.2, "STRUCTURE", fontsize=8, color="gray", rotation=90, va="center")
    ax.text(1.02, 0.4, "BLOAT", fontsize=8, color="gray", rotation=90, va="center")
    ax.set_xlim(-0.05, 1.05)
    ax.set_xlabel("prevalence (share of texts)")
    ax.set_title(FAM_LABEL[fam], fontsize=11)

handles = [plt.Line2D([], [], marker="o", ls="", color="tab:blue", label="Original cheap team"),
           plt.Line2D([], [], marker="o", ls="", color="tab:orange", label="Refined cheap team"),
           plt.Line2D([], [], marker="D", ls="", color="black", label="Frontier solo")]
fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=9.5, frameon=False,
           bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Study 2 — what refinement changes: structure codes move, insight codes do not;\n"
             "frontier solo stands apart on concise maxims (insight) and zero bloat",
             fontsize=11)
fig.tight_layout(rect=[0, 0.05, 1, 0.92])
fig.savefig(OUT / "fig5_code_heatmap.png", bbox_inches="tight", dpi=200)
print("saved fig5_code_heatmap.png (simplified dumbbell)")
