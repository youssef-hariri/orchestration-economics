#!/usr/bin/env python3
"""Frozen computation: per-family paired contrast CTP vs F-S-N (Study 1).

Persists the values cited in paper/P5_v15.5.tex sec:frontier-gap
(kimi d=-0.71, claude d=-1.42, qwen d=-2.17; all CIs exclude zero after Holm).
Closes claim-map gap PM-S1_012 / audit S1_012.

Pairing: within each family, C-T-P and F-S-N runs are matched on problemId;
d = mean(diff)/sd(diff) (paired Cohen's d), t = one-sample t on diffs,
CI = bootstrap 95% on mean diff (same BOOT_N/seed as analyze_main),
Holm correction across the five families.
Output: results/ctp_vs_fsn_by_family.json
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# --- Loaders copied verbatim from code/analyze_main.py (same conventions) ---
DIMS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]
BOOT_N, BOOT_SEED = 5000, 42  # identical to analyze_main.py

def load_judgments(path):
    last = {}
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        last[(r["runId"], r["judge_family"], r["variant"])] = r
    recs = list(last.values())
    bad = [r for r in recs if r.get("error") or r.get("incomplete")]
    return [r for r in recs if not (r.get("error") or r.get("incomplete"))], len(bad)

def judgment_mean(scores):
    vals = [v for v in scores.values() if isinstance(v, (int, float))]
    return float(np.mean(vals)) if vals else None

def build_run_table(recs, meta):
    rows, by_run = [], {}
    for r in recs:
        m = judgment_mean(r.get("scores") or {})
        if m is None:
            continue
        by_run.setdefault(r["runId"], []).append((m, r["scores"]))
    for run_id, js in by_run.items():
        if run_id not in meta:
            continue
        md = meta[run_id]
        tier, structure, persona = md["cell"].split("-")
        rows.append({
            "runId": run_id, "problemId": md["problemId"], "cell": md["cell"],
            "tier": tier, "structure": structure, "persona": persona,
            "family": md["family"], "n_judg": len(js),
            "composite": float(np.mean([x[0] for x in js])),
        })
    return pd.DataFrame(rows)
# --- end verbatim block ------------------------------------------------------

def boot_ci_paired(diff, n_boot=BOOT_N, seed=BOOT_SEED):
    rng = np.random.default_rng(seed)
    n = len(diff)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = diff[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def perm_p_paired(diff, n_perm=100000, seed=BOOT_SEED):
    rng = np.random.default_rng(seed)
    obs = abs(diff.mean())
    signs = rng.choice([-1.0, 1.0], size=(n_perm, len(diff)))
    null = np.abs((signs * diff).mean(axis=1))
    return float((np.sum(null >= obs) + 1) / (n_perm + 1))


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = [None] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def main():
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    meta = {r["runId"]: r for r in store["runs"] if r.get("fulltext")}
    recs, _ = load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    t = build_run_table(recs, meta)

    out = {"amendment": "persisted 2026-09-19 (closes claim-map gap PM-S1_012 / audit S1_012)",
           "contrast": "C-T-P minus F-S-N, paired on problemId, composite DV",
           "per_family": {}}
    pvals, fams = [], []
    for fam in sorted(t.family.unique()):
        ctp = t[(t.family == fam) & (t.cell == "C-T-P")].set_index("problemId")["composite"]
        fsn = t[(t.family == fam) & (t.cell == "F-S-N")].set_index("problemId")["composite"]
        common = ctp.index.intersection(fsn.index)
        diff = (ctp[common] - fsn[common]).to_numpy()
        n = len(diff)
        d = float(diff.mean() / diff.std(ddof=1))
        tv = float(diff.mean() / (diff.std(ddof=1) / np.sqrt(n)))
        pv = perm_p_paired(diff)
        lo, hi = boot_ci_paired(diff)
        out["per_family"][fam] = {"n_pairs": n, "mean_diff": round(float(diff.mean()), 4),
                                  "sd_diff": round(float(diff.std(ddof=1)), 4),
                                  "d": round(d, 4), "t": round(tv, 3), "p": round(pv, 6),
                                  "boot95CI_mean_diff": [round(lo, 4), round(hi, 4)]}
        pvals.append(pv)
        fams.append(fam)
    adj = holm(pvals)
    for fam, p_holm in zip(fams, adj):
        out["per_family"][fam]["p_holm"] = round(p_holm, 6)
        out["per_family"][fam]["ci_excludes_zero"] = (
            out["per_family"][fam]["boot95CI_mean_diff"][0] > 0 or
            out["per_family"][fam]["boot95CI_mean_diff"][1] < 0)
    out["all_five_negative"] = all(f["mean_diff"] < 0 for f in out["per_family"].values())
    path = ROOT / "results" / "ctp_vs_fsn_by_family.json"
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps({f: {"d": v["d"], "p_holm": v["p_holm"]} for f, v in out["per_family"].items()}, indent=1))
    print("written:", path)


if __name__ == "__main__":
    main()
