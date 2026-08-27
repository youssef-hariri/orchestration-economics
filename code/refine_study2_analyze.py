#!/usr/bin/env python3
"""Protocol 09 / Study 2 — pilot analysis (locked plan, Protocol 09 sec 6).

Paired comparisons on the same instrument:
  H2.1 primary : refined C-T-P vs matched F-S-N (per family, Holm)
  H2.2 protect : Novelty(refined) vs Novelty(original C-T-P), margin -0.10
  H2.3 repair  : Usefulness/Elaboration(refined) vs original C-T-P
Secondary block: all 5 dims refined vs original C-T-P, BH-FDR.
Output: results/refine_study2_pilot.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import analyze_main as am  # noqa: E402

DIMS = am.DIMS
N_BOOT = 1000
SEED = 42


def agg(recs):
    """per-run composite + per-dim means from judgment records."""
    out = {}
    for r in recs:
        m = am.judgment_mean(r.get("scores") or {})
        if m is None:
            continue
        out.setdefault(r["runId"], []).append((m, r["scores"]))
    rows = {}
    for rid, js in out.items():
        dim = {}
        for d in DIMS:
            vals = [s[d] for _, s in js if isinstance(s.get(d), (int, float))]
            dim[d] = float(np.mean(vals)) if vals else np.nan
        rows[rid] = {"composite": float(np.mean([x[0] for x in js])), **dim,
                     "n_judg": len(js)}
    return rows


def paired_stats(diff, n_boot=N_BOOT, seed=SEED):
    n = len(diff)
    mean = float(np.mean(diff))
    sd = float(np.std(diff, ddof=1))
    t, p_two = stats.ttest_1samp(diff, 0)
    p_one = p_two / 2 if t > 0 else 1 - p_two / 2
    rng = np.random.default_rng(seed)
    boots = [float(np.mean(rng.choice(diff, n, replace=True))) for _ in range(n_boot)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"n": int(n), "mean_diff": round(mean, 4), "sd_diff": round(sd, 4),
            "d": round(mean / sd, 3) if sd > 0 else None,
            "t": round(float(t), 3), "p_one_sided": round(float(p_one), 5),
            "ci95_boot": [round(lo, 4), round(hi, 4)]}


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        adj[i] = running = max(running, min(1.0, pvals[i] * (m - rank)))
    return adj.tolist()


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", nargs="+",
                    default=["runs/refine/sample_pilot.json"])
    ap.add_argument("--judgments", nargs="+",
                    default=["runs/logs/refine_judgments_pilot.jsonl"])
    ap.add_argument("--refine-logs", nargs="+",
                    default=["runs/logs/refine_pilot.jsonl"])
    ap.add_argument("--phase", default="pilot")
    ap.add_argument("--out", default="results/refine_study2_pilot.json")
    args = ap.parse_args()

    pairs = []
    for s in args.samples:
        pairs += json.load(open(ROOT / s))["pairs"]

    raw = []
    for jf in args.judgments:
        raw += [json.loads(l) for l in open(ROOT / jf) if l.strip()]
    refined = agg([r for r in raw if not r.get("error") and not r.get("incomplete")])
    main_recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    main_rows = agg(main_recs)

    # H2.1: refined vs FSN per family
    h21 = {}
    pvals = []
    fams = []
    for fam in ["kimi", "claude", "qwen"]:
        fs, rs = [], []
        for p in pairs:
            if p["family"] != fam:
                continue
            r = refined.get(f"R{p['ctp_runId']}")
            f = main_rows.get(p["fsn_runId"])
            if r and f:
                rs.append(r["composite"])
                fs.append(f["composite"])
        diff = np.array(rs) - np.array(fs)
        st = paired_stats(diff)
        h21[fam] = st
        pvals.append(st["p_one_sided"])
        fams.append(fam)
    adj = holm(np.array(pvals))
    for fam, a in zip(fams, adj):
        h21[fam]["p_holm"] = round(float(a), 5)
        h21[fam]["sig_holm_05"] = bool(a < 0.05)

    # H2.2/H2.3 + secondary: refined vs original CTP per dimension
    per_dim = {}
    all_p = []
    keys = []
    for fam in ["kimi", "claude", "qwen"]:
        for dim in DIMS + ["composite"]:
            o, r = [], []
            for p in pairs:
                if p["family"] != fam:
                    continue
                rr = refined.get(f"R{p['ctp_runId']}")
                oo = main_rows.get(p["ctp_runId"])
                if rr and oo:
                    r.append(rr[dim])
                    o.append(oo[dim])
            diff = np.array(r) - np.array(o)
            st = paired_stats(diff)
            per_dim[f"{fam}:{dim}"] = st
            all_p.append(st["p_one_sided"])
            keys.append(f"{fam}:{dim}")
    # BH-FDR within secondary block (two-sided equivalents)
    two_sided = [min(1.0, 2 * min(p, 1 - p)) for p in all_p]
    order = np.argsort(two_sided)
    m = len(order)
    fdr = np.empty(m)
    run = 1.0
    for rank_idx in range(m - 1, -1, -1):
        i = order[rank_idx]
        fdr[i] = run = min(run, two_sided[i] * m / (rank_idx + 1))
    for k, q in zip(keys, fdr):
        per_dim[k]["p_FDR"] = round(float(q), 5)

    h22 = {fam: per_dim[f"{fam}:Novelty"] for fam in ["kimi", "claude", "qwen"]}
    h22_pass = {fam: bool(v["mean_diff"] >= -0.10) for fam, v in h22.items()}
    h23 = {fam: {d: per_dim[f"{fam}:{d}"] for d in ["Usefulness", "Elaboration"]}
           for fam in ["kimi", "claude", "qwen"]}

    # length audit
    refine_log = []
    for rl in args.refine_logs:
        refine_log += [json.loads(l) for l in open(ROOT / rl) if l.strip()]
    ok = [j for j in refine_log if j.get("refined_text")]
    ratio = np.mean([j["refined_len"] / j["orig_len"] for j in ok])

    result = {
        "protocol": "09", "phase": args.phase, "seeds": [20260730, 20260731],
        "n_pairs": len(pairs),
        "g1_feasibility": {"completion": round(len(ok) / len(pairs), 3),
                           "pass": bool(len(ok) / len(pairs) >= 0.95)},
        "length_ratio_refined_over_original": round(float(ratio), 3),
        "H2.1_refined_vs_FSN": h21,
        "H2.2_novelty_protection": {"results": h22, "noninferiority_margin": -0.10,
                                    "pass": h22_pass},
        "H2.3_repair": h23,
        "secondary_refined_vs_original_CTP_per_dim": per_dim,
        "gate_G2": {"rule": "all three families d>=0.2 with CI excluding 0 -> full run",
                    "evaluation": {fam: {"d": v["d"],
                                         "ci_excludes_zero": not (v["ci95_boot"][0] <= 0 <= v["ci95_boot"][1])}
                                   for fam, v in h21.items()}},
    }
    dst = ROOT / args.out
    dst.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"done -> {dst}\n")
    print("H2.1 refined vs FSN (primary):")
    for fam, v in h21.items():
        print(f"  {fam:7s} d={v['d']:+.3f}  diff={v['mean_diff']:+.3f}  "
              f"CI={v['ci95_boot']}  p_one={v['p_one_sided']:.4f}  p_holm={v['p_holm']:.4f} "
              f"{'SIG' if v['sig_holm_05'] else ''}")
    print("\nH2.2 Novelty protection (refined vs original CTP):")
    for fam, v in h22.items():
        print(f"  {fam:7s} diff={v['mean_diff']:+.3f} CI={v['ci95_boot']}  "
              f"{'PASS' if h22_pass[fam] else 'FAIL'}")
    print("\nH2.3 repair (refined vs original CTP):")
    for fam, dims in h23.items():
        print(f"  {fam:7s} Usefulness {dims['Usefulness']['mean_diff']:+.3f} "
              f"(FDR={dims['Usefulness']['p_FDR']:.3f}), "
              f"Elaboration {dims['Elaboration']['mean_diff']:+.3f} "
              f"(FDR={dims['Elaboration']['p_FDR']:.3f})")
    print(f"\nG1 feasibility: {result['g1_feasibility']['completion']*100:.0f}% "
          f"| length ratio refined/original = {ratio:.2f}")


if __name__ == "__main__":
    main()
