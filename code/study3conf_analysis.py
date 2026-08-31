#!/usr/bin/env python3
"""Protocol 16 — Study 3 confirmatory replication: FROZEN analysis (gates R1-R5).

Pre-registered (OSF zkm8v, 2026-08-30) BEFORE generation; this script is written
and hash-locked BEFORE judging (same discipline as the Protocol-12 wave).

Data:
  - D-SELF runs: runs/logs/study3conf_ledger.jsonl (status=completed) joined to
    runs/study3conf/study3conf_judgments.jsonl (judge_v2 output; key = runId string
    "D-SELF__{family}__{problem}__rep{r}").
  - Comparator: wave F-S-N, runs/logs/wave_run_ledger.json (completed, cell F-S-N)
    joined by numeric runId to runs/logs/wave_judgments.jsonl. Both frozen
    2026-08-24; NO new frontier-solo generation.

Judgment handling (identical to Study 3, code/study3_analysis.py): skip rows with
error/incomplete; dedupe last-wins per (runId, judge_family, variant); per-run
score = mean of the 9 judgments (3 judges x 3 variants); per-problem score =
mean over available reps. Unit of analysis = problem (Welch two-sample across
problems, arm n vs comparator n = #problems with >=1 rep on each side).
p-values: normal approximation (same as Study 3: norm_cdf on the t statistic);
disclosed approximation, n ~ 28-30 problems per side.

Gates (binding, OSF zkm8v; each gate is a separate family-specific hypothesis, so
no cross-gate multiplicity correction by design):
  R1 kimi:   one-sided p(+)  < .05 AND d > 0
  R2 qwen:   one-sided p(+)  < .05 AND d > 0
  R3 gemini: one-sided p(+)  < .05 AND d > 0
  R4 gpt:    TOST equivalence — 90% CI of d fully inside [-0.30, +0.30]
  R5 claude: one-sided p(-)  < .05 AND d < -1.0

Outputs (D54): results/study3conf_results.json + analysis/results/study3conf_gates.csv
"""
import csv
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIM = "Novelty"
GATES = {"kimi": ("pos", None), "qwen": ("pos", None), "gemini": ("pos", None),
         "gpt": ("tost", 0.30), "claude": ("neg", -1.0)}


def norm_cdf(x):
    return (1 + math.erf(x / math.sqrt(2))) / 2


def load_judgments(path):
    """runId -> mean Novelty over deduped (judge, variant) judgments."""
    per = {}
    for line in open(path):
        j = json.loads(line)
        if j.get("error") or j.get("incomplete"):
            continue
        per[(str(j["runId"]), j["judge_family"], j["variant"])] = j["scores"][DIM]
    run = defaultdict(list)
    for (rid, jf, var), s in per.items():
        run[rid].append(s)
    return {rid: sum(v) / len(v) for rid, v in run.items()}


def problem_means(items):
    """items: list of (problemId, score) -> {problem: mean over reps}"""
    acc = defaultdict(list)
    for pid, s in items:
        acc[pid].append(s)
    return {p: sum(v) / len(v) for p, v in acc.items()}


def main():
    # --- D-SELF arm (Protocol 16)
    arm_judgments = load_judgments(ROOT / "runs/study3conf/study3conf_judgments.jsonl")
    arm_items = []
    for rid, s in arm_judgments.items():
        _, fam, pid, rep = rid.split("__")
        arm_items.append((fam, pid, s))
    arm_by_fam = defaultdict(list)
    for fam, pid, s in arm_items:
        arm_by_fam[fam].append((pid, s))
    arm_pm = {f: problem_means(v) for f, v in arm_by_fam.items()}

    # --- wave F-S-N comparator (frozen)
    wled = json.load(open(ROOT / "runs/logs/wave_run_ledger.json"))["results"]
    meta = {str(r["runId"]): r for r in wled
            if r.get("cell") == "F-S-N" and r.get("status") == "completed"}
    base_judgments = load_judgments(ROOT / "runs/logs/wave_judgments.jsonl")
    base_items = [(r["family"], r["problemId"], base_judgments[rid])
                  for rid, r in meta.items() if rid in base_judgments]
    base_by_fam = defaultdict(list)
    for fam, pid, s in base_items:
        base_by_fam[fam].append((pid, s))
    base_pm = {f: problem_means(v) for f, v in base_by_fam.items()}

    # --- gates
    rows = []
    for fam, (kind, bound) in GATES.items():
        a = [s for p, s in sorted(arm_pm.get(fam, {}).items()) if p in base_pm.get(fam, {})]
        b = [base_pm[fam][p] for p, _ in sorted(arm_pm.get(fam, {}).items()) if p in base_pm.get(fam, {})]
        # a and b are aligned per problem (paired problems), but the pre-registered
        # test is Welch two-sample (conservative; comparator runs are independent runs)
        na, nb = len(a), len(b)
        if na < 2 or nb < 2:
            rows.append({"gate": {"kimi": "R1", "qwen": "R2", "gemini": "R3",
                                  "gpt": "R4", "claude": "R5"}[fam],
                         "family": fam, "n_arm_problems": na, "n_base_problems": nb,
                         "rule": "insufficient data", "pass": False})
            continue
        ma, mb = st.mean(a), st.mean(b)
        va, vb = st.variance(a), st.variance(b)
        sp = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
        d = (ma - mb) / sp if sp else 0.0
        denom = math.sqrt(va / na + vb / nb)
        t = (ma - mb) / denom if denom else 0.0
        p_pos = 1 - norm_cdf(t)
        p_neg = norm_cdf(t)
        se_d = math.sqrt((na + nb) / (na * nb) + d * d / (2 * (na + nb - 2)))
        ci_lo, ci_hi = d - 1.645 * se_d, d + 1.645 * se_d
        if kind == "pos":
            passed = bool(p_pos < 0.05 and d > 0)
            detail = f"p(+)={p_pos:.4f}"
        elif kind == "neg":
            passed = bool(p_neg < 0.05 and d < bound)
            detail = f"p(-)={p_neg:.4f}, d<{bound}"
        else:  # tost
            passed = bool(ci_lo > -bound and ci_hi < bound)
            detail = f"90%CI=[{ci_lo:.3f},{ci_hi:.3f}] within ±{bound}"
        rows.append({"gate": {"kimi": "R1", "qwen": "R2", "gemini": "R3",
                              "gpt": "R4", "claude": "R5"}[fam],
                     "family": fam, "n_arm_problems": na, "n_base_problems": nb,
                     "mean_arm": round(ma, 3), "mean_FSN_wave": round(mb, 3),
                     "d": round(d, 3), "t": round(t, 3),
                     "p_one_sided_pos": round(p_pos, 4), "p_one_sided_neg": round(p_neg, 4),
                     "d_ci90_lo": round(ci_lo, 3), "d_ci90_hi": round(ci_hi, 3),
                     "rule": detail, "pass": passed})

    headline = all(r["pass"] for r in rows if r["gate"] in ("R1", "R2", "R3", "R5"))
    out = {"study": "study3_confirmatory", "protocol": "16", "registration": "osf.io/zkm8v",
           "unit_of_analysis": "problem (Welch across problems; normal-approx p, as Study 3)",
           "dimension": DIM, "gates": rows,
           "headline_family_moderation_replicated": headline}
    json.dump(out, open(ROOT / "results/study3conf_results.json", "w"), indent=2)
    ar = ROOT / "analysis/results"
    ar.mkdir(parents=True, exist_ok=True)
    with open(ar / "study3conf_gates.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
