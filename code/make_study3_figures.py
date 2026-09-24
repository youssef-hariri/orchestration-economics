"""Generate the three missing Study-3 / P16 figures for the paper.
Reads only frozen raw result files; saves PNGs into the paper figures folder.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot
setup_plot()
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "FULL-PAPER-DRAFT-BUSINESS-v14.1_with_figures"

FAM_ORDER = ["gemini", "qwen", "kimi", "gpt", "claude"]
DOM_ORDER = ["strategy_market_entry", "marketing_communications", "hr_organization",
             "product_innovation", "finance_business_models", "operations_supply_chain"]
DOM_LABEL = {
    "strategy_market_entry": "Strategy",
    "marketing_communications": "Marketing",
    "hr_organization": "HR",
    "product_innovation": "Product",
    "finance_business_models": "Finance",
    "operations_supply_chain": "Operations",
}
FAM_LABEL = {"gemini": "Gemini", "qwen": "Qwen", "kimi": "Kimi", "gpt": "GPT-5.6", "claude": "Claude"}

# ---------- Figure 1: Study 3 family x domain heatmap ----------
d = json.load(open(ROOT / "results" / "study3_by_family_domain.json"))
mat = np.full((len(FAM_ORDER), len(DOM_ORDER)), np.nan)
for r in d["rows"]:
    i = FAM_ORDER.index(r["family"]); j = DOM_ORDER.index(r["domain"])
    mat[i, j] = r["d_vs_FSN_D-SELF"]

fig, ax = plt.subplots(figsize=(9.5, 4.6))
vmax = 3.0
im = ax.imshow(mat, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")
ax.set_xticks(range(len(DOM_ORDER)), [DOM_LABEL[x] for x in DOM_ORDER])
ax.set_yticks(range(len(FAM_ORDER)), [FAM_LABEL[x] for x in FAM_ORDER])
for i in range(len(FAM_ORDER)):
    for j in range(len(DOM_ORDER)):
        if not np.isnan(mat[i, j]):
            ax.text(j, i, f"{mat[i,j]:+.1f}", ha="center", va="center",
                    fontsize=9, color="black")
ax.set_title("Study 3: D-SELF Novelty effect vs frontier solo (Cohen's d), by family × domain\n"
             "(descriptive; cells of 2–5 problems, underpowered for inference by design)",
             fontsize=10)
fig.colorbar(im, ax=ax, label="Cohen's d vs F-S-N", shrink=0.85)
fig.savefig(OUT / "fig_study3_family_domain.png", bbox_inches="tight", dpi=200)
plt.close(fig)

# ---------- Figure 2: Study 3 economics scatter ----------
e = json.load(open(ROOT / "results" / "study3_economics.json"))
rows = {r["family"]: r for r in e["rows"]}
fig, ax = plt.subplots(figsize=(8.5, 5.5))
ax.axvspan(0.2, 1, ymin=0.5, ymax=1, color="green", alpha=0.08)
ax.text(0.02, 0.97, "STRICTLY DOMINANT (better & cheaper) →", transform=ax.transAxes,
        fontsize=8.5, color="darkgreen", va="top")
ax.axhline(0, color="gray", lw=0.8); ax.axvline(1, color="gray", lw=0.8)
for fam in FAM_ORDER:
    r = rows[fam]
    ax.scatter(r["cost_ratio_self_vs_fsn"], r["dself_d_quality"], marker="o", s=90,
               color="tab:blue", zorder=3)
    ax.scatter(r["cost_ratio_front_vs_fsn"], r["dfront_d_quality"], marker="^", s=90,
               color="tab:orange", zorder=3)
    ax.annotate(FAM_LABEL[fam], (r["cost_ratio_self_vs_fsn"], r["dself_d_quality"]),
                textcoords="offset points", xytext=(8, 5), fontsize=9)
    ax.annotate(FAM_LABEL[fam], (r["cost_ratio_front_vs_fsn"], r["dfront_d_quality"]),
                textcoords="offset points", xytext=(8, -12), fontsize=9, color="tab:orange")
ax.set_xscale("log")
ax.set_xticks([0.24, 0.5, 1, 2, 4], ["0.24×", "0.5×", "1×", "2×", "4×"])
ax.set_xlabel("Cost per solution vs frontier solo (×, log scale)")
ax.set_ylabel("Novelty effect vs frontier solo (Cohen's d)")
ax.set_title("Study 3 economics: cheap auto-designed pipelines vs their family's frontier solo")
ax.scatter([], [], marker="o", s=90, color="tab:blue", label="D-SELF (cheap designs & executes)")
ax.scatter([], [], marker="^", s=90, color="tab:orange", label="D-FRONT (frontier designs, cheap executes)")
ax.legend(loc="lower left", fontsize=9)
fig.savefig(OUT / "fig_study3_econ_scatter.png", bbox_inches="tight", dpi=200)
plt.close(fig)

# ---------- Figure 3: Protocol 16 predicted vs observed gates ----------
p = json.load(open(ROOT / "results" / "study3conf_results.json"))
PRED = {"kimi": 0.85, "qwen": 0.55, "gemini": 0.46, "gpt": 0.0, "claude": -3.15}
gates = {g["family"]: g for g in p["gates"]}
order = ["kimi", "qwen", "gemini", "gpt", "claude"]
fig, ax = plt.subplots(figsize=(8.5, 4.8))
x = np.arange(len(order)); w = 0.36
obs = [gates[f]["d"] for f in order]
lo = [gates[f]["d_ci90_lo"] for f in order]; hi = [gates[f]["d_ci90_hi"] for f in order]
passed = [gates[f]["pass"] for f in order]
ax.bar(x - w/2, [PRED[f] for f in order], w, color="lightgray", edgecolor="gray",
       label="Predicted (Study 3 point estimate)")
colors = ["tab:green" if ok else "tab:red" for ok in passed]
ax.bar(x + w/2, obs, w, color=colors)
ax.errorbar(x + w/2, obs, yerr=[np.array(obs)-np.array(lo), np.array(hi)-np.array(obs)],
            fmt="none", ecolor="black", capsize=4, lw=1)
from matplotlib.patches import Patch
for xi, o, ok, h in zip(x, obs, passed, hi):
    ax.text(xi + w/2, (h + 0.18) if o >= 0 else (o - 0.62), "PASS" if ok else "fail",
            ha="center", fontsize=9, fontweight="bold",
            color="tab:green" if ok else "tab:red")
ax.axhline(0, color="gray", lw=0.8)
ax.set_xticks(x, [FAM_LABEL[f] for f in order])
ax.set_ylabel("Cohen's d on Novelty (D-SELF vs frozen wave F-S-N)")
ax.set_title("Protocol 16 transport test: extremes replicate, mid-tier effects do not (2/5 gates)",
             pad=14)
ax.legend(handles=[Patch(facecolor="lightgray", edgecolor="gray",
                         label="Predicted (Study 3 point estimate)"),
                   Patch(facecolor="tab:green", label="Observed — gate PASS"),
                   Patch(facecolor="tab:red", label="Observed — gate fail")],
          fontsize=9, loc="lower left")
ax.set_ylim(-3.6, 2.2)
fig.savefig(OUT / "fig_p16_gates.png", bbox_inches="tight", dpi=200)
plt.close(fig)

print("saved:", [f.name for f in OUT.glob("fig_study3*.png")] + [f.name for f in OUT.glob("fig_p16*.png")])
