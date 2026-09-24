"""Redraw fig3 cost-effectiveness scatter from frozen results/cost/cost_effectiveness.json
with light 95% CI (of the mean) error bars instead of full-SD crosses."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot
setup_plot()
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "FULL-PAPER-DRAFT-BUSINESS-v14.1_with_figures"
d = json.load(open(ROOT / "results" / "cost" / "cost_effectiveness.json"))
cs = d["cell_summary_primary"]
CELLS = ["C-S-P", "C-S-N", "C-T-P", "C-T-N", "F-S-P", "F-S-N", "F-T-N", "F-T-P"]

fig, ax = plt.subplots(figsize=(8.5, 6))
cmap = {"C": "#2b8cbe", "F": "#de2d26"}
for c in CELLS:
    v = cs[c]
    # 95% CI of the mean (thin, readable) instead of full SD
    xerr = 1.96 * v["sd_cost"] / np.sqrt(v["n"])
    yerr = 1.96 * v["sd_quality"] / np.sqrt(v["n"])
    ax.errorbar(v["mean_cost"], v["mean_quality"], xerr=xerr, yerr=yerr,
                fmt="o", ms=9, color=cmap[c[0]], ecolor=cmap[c[0]],
                elinewidth=0.9, capsize=2.5, alpha=0.9, zorder=3)
    ax.annotate(c, (v["mean_cost"], v["mean_quality"]), textcoords="offset points",
                xytext=(7, 6), fontsize=9)
front = d["pareto_by_phi"]["0.5"]
pts = sorted([(cs[c]["mean_cost"], cs[c]["mean_quality"]) for c in front])
ax.plot([p[0] for p in pts], [p[1] for p in pts], "k--", lw=1, alpha=0.7,
        label="Pareto frontier (φ = 0.5)")
fam_color = {"kimi": "#1f77b4", "claude": "#d62728", "qwen": "#2ca02c"}
for rp in d["refined_ctp_points"]:
    ax.plot(rp["mean_cost"], rp["mean_quality"], "D", ms=9,
            markeredgecolor="black", color=fam_color[rp["family"]], zorder=4)
    ax.annotate(f"refined C-T-P ({rp['family']})", (rp["mean_cost"], rp["mean_quality"]),
                textcoords="offset points", xytext=(7, -13), fontsize=8)
ax.set_xlabel("Mean cost per run (USD, φ = 0.5)")
ax.set_ylabel("Mean judged composite quality (1–5)")
ax.set_title("Cost-effectiveness frontier: 8 cells + Study-2 refined C-T-P\n"
             "(error bars: 95% CI of the mean)")
ax.legend(loc="lower right", fontsize=9)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "fig3_cost_scatter.png", dpi=200, bbox_inches="tight")
print("saved fig3_cost_scatter.png")
