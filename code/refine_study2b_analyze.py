#!/usr/bin/env python3
"""Protocol 11 / Study 2b — arm-aware analysis (locked plan, Protocol 11 sec 7).

Frozen BEFORE any new data are generated (pre-registered analysis script).
Reuses refine_study2_analyze.py helpers verbatim (same aggregation, same
bootstrap/Holm machinery) so Study 2 and Study 2b statistics are identical.

Modes:
  --mode arm      H3.1 refined vs matched F-S-N (per family + pooled, Holm),
                  H3.2 Novelty protection (margin -0.10), H3.3 repair block,
                  secondary per-dim BH-FDR, G1 feasibility, G2 gate.
  --mode identity H3.4 refiner-identity contrast: paired composite(W) - composite(U)
                  on pairs judged under BOTH refiners; pooled primary,
                  per-family with Holm secondary; two-sided.

Output: JSON report to --out.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import analyze_main as am  # noqa: E402
import refine_study2_analyze as r2  # noqa: E402  (frozen Study-2 helpers)

DIMS = am.DIMS
FAMS_ALL = ["gpt", "claude", "gemini", "kimi", "qwen"]


def load_pairs(paths):
    pairs = []
    for s in paths:
        pairs += json.load(open(ROOT / s))["pairs"]
    return pairs


def load_judgments(paths):
    raw = []
    for jf in paths:
        raw += [json.loads(l) for l in open(ROOT / jf) if l.strip()]
    return r2.agg([r for r in raw if not r.get("error") and not r.get("incomplete")])


def main_rows():
    """Locked Study-1 judgments: original C-T-P and F-S-N scores (reused, never re-judged)."""
    recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    return r2.agg(recs)


def h31_block(pairs, refined, mrows, fams):
    """H3.1: refined vs matched F-S-N — per family (Holm) + pooled."""
    out, pvals, keys, all_diff = {}, [], [], []
    for fam in fams:
        fs, rs = [], []
        for p in pairs:
            if p["family"] != fam:
                continue
            r = refined.get(f"R{p['ctp_runId']}")
            f = mrows.get(p["fsn_runId"])
            if r and f:
                rs.append(r["composite"])
                fs.append(f["composite"])
        diff = np.array(rs) - np.array(fs)
        st = r2.paired_stats(diff) if len(diff) else None
        out[fam] = st
        if st:
            pvals.append(st["p_one_sided"])
            keys.append(fam)
            all_diff += diff.tolist()
    if pvals:
        adj = r2.holm(np.array(pvals))
        for fam, a in zip(keys, adj):
            out[fam]["p_holm"] = round(float(a), 5)
            out[fam]["sig_holm_05"] = bool(a < 0.05)
    out["pooled"] = r2.paired_stats(np.array(all_diff)) if all_diff else None
    return out


def dim_block(pairs, refined, mrows, fams):
    """Refined vs original C-T-P per dimension (H3.2/H3.3 + secondary BH-FDR)."""
    per_dim, all_p, keys = {}, [], []
    for fam in fams:
        for dim in DIMS + ["composite"]:
            o, rr = [], []
            for p in pairs:
                if p["family"] != fam:
                    continue
                r = refined.get(f"R{p['ctp_runId']}")
                oo = mrows.get(p["ctp_runId"])
                if r and oo:
                    rr.append(r[dim])
                    o.append(oo[dim])
            st = r2.paired_stats(np.array(rr) - np.array(o)) if rr else None
            per_dim[f"{fam}:{dim}"] = st
            if st:
                all_p.append(st["p_one_sided"])
                keys.append(f"{fam}:{dim}")
    if all_p:  # BH-FDR within the secondary block (two-sided equivalents)
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
    return per_dim


def mode_arm(args):
    pairs = load_pairs(args.samples)
    refined = load_judgments(args.judgments)
    mrows = main_rows()
    fams = sorted({p["family"] for p in pairs})

    h31 = h31_block(pairs, refined, mrows, fams)
    per_dim = dim_block(pairs, refined, mrows, fams)
    h32 = {fam: per_dim.get(f"{fam}:Novelty") for fam in fams}
    h32_pass = {fam: bool(v and v["mean_diff"] >= -0.10) for fam, v in h32.items()}
    h33 = {fam: {d: per_dim.get(f"{fam}:{d}") for d in ["Usefulness", "Elaboration"]}
           for fam in fams}

    refine_log = []
    for rl in args.refine_logs:
        refine_log += [json.loads(l) for l in open(ROOT / rl) if l.strip()]
    ok = [j for j in refine_log if j.get("refined_text")]
    completion = len(ok) / len(pairs) if pairs else 0.0
    ratio = float(np.mean([j["refined_len"] / j["orig_len"] for j in ok])) if ok else None

    result = {
        "protocol": "11", "study": "2b", "mode": "arm", "arm": args.arm,
        "phase": args.phase, "families": fams, "n_pairs": len(pairs),
        "g1_feasibility": {"completion": round(completion, 3),
                           "pass": bool(completion >= 0.95)},
        "length_ratio_refined_over_original": round(ratio, 3) if ratio else None,
        "H3.1_refined_vs_FSN": h31,
        "H3.2_novelty_protection": {"results": h32, "noninferiority_margin": -0.10,
                                    "pass": h32_pass},
        "H3.3_repair": h33,
        "secondary_refined_vs_original_CTP_per_dim": per_dim,
        "gate_G2": {"rule": "every family in arm-phase: d>=0.2 and bootstrap CI "
                            "excludes 0 -> extend to remaining pairs",
                    "evaluation": {fam: {"d": v["d"],
                                         "ci_excludes_zero": not (
                                             v["ci95_boot"][0] <= 0 <= v["ci95_boot"][1])}
                                   for fam, v in h31.items()
                                   if isinstance(v, dict) and fam != "pooled"}},
    }
    dst = ROOT / args.out
    dst.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"arm {args.arm} {args.phase}: {len(pairs)} pairs -> {dst}")


def mode_identity(args):
    """H3.4: paired composite(W) - composite(U) on pairs judged under both refiners."""
    pairs = load_pairs(args.samples)
    u_rows = load_judgments(args.judgments_u)
    w_rows = load_judgments(args.judgments_w)

    by_fam = {}
    for p in pairs:
        u = u_rows.get(f"R{p['ctp_runId']}")
        w = w_rows.get(f"R{p['ctp_runId']}")
        if u and w:
            by_fam.setdefault(p["family"], []).append(w["composite"] - u["composite"])

    out, pvals, keys, all_diff = {}, [], [], []
    for fam in sorted(by_fam):
        diff = np.array(by_fam[fam])
        st = two_sided_paired(diff)
        out[fam] = st
        pvals.append(st["p_two_sided"])
        keys.append(fam)
        all_diff += diff.tolist()
    if pvals:
        adj = r2.holm(np.array(pvals))
        for fam, a in zip(keys, adj):
            out[fam]["p_holm"] = round(float(a), 5)
            out[fam]["sig_holm_05"] = bool(a < 0.05)
    out["pooled"] = two_sided_paired(np.array(all_diff)) if all_diff else None

    result = {
        "protocol": "11", "study": "2b", "mode": "identity",
        "contrast": "composite(within-family refiner) - composite(universal refiner)",
        "direction": "two-sided (decomposition test, no pre-committed direction)",
        "families": sorted(by_fam),
        "n_pairs_pooled": len(all_diff),
        "H3.4_refiner_identity": out,
    }
    dst = ROOT / args.out
    dst.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"identity contrast: {len(all_diff)} paired -> {dst}")


def two_sided_paired(diff):
    """Paired stats with TWO-sided p (H3.4 is a decomposition, not a superiority test).
    BUGFIX 2026-08-22 (disclosed in MANIFEST): original 2*p_one_sided truncated to
    1.0 for negative effects; corrected to 2*min(p, 1-p), matching dim_block above."""
    st = r2.paired_stats(diff)
    st["p_two_sided"] = round(min(1.0, 2 * min(st["p_one_sided"], 1 - st["p_one_sided"])), 5)
    return st


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["arm", "identity"], required=True)
    ap.add_argument("--arm", default=None, help="U or W (mode arm)")
    ap.add_argument("--phase", default="pilot")
    ap.add_argument("--samples", nargs="+", required=True)
    ap.add_argument("--judgments", nargs="+", default=[], help="refined judgments (mode arm)")
    ap.add_argument("--judgments-u", nargs="+", default=[], help="universal-refiner judgments (mode identity)")
    ap.add_argument("--judgments-w", nargs="+", default=[], help="within-family judgments (mode identity)")
    ap.add_argument("--refine-logs", nargs="+", default=[])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.mode == "arm":
        assert args.judgments, "--judgments required in arm mode"
        mode_arm(args)
    else:
        assert args.judgments_u and args.judgments_w, \
            "--judgments-u and --judgments-w required in identity mode"
        mode_identity(args)


if __name__ == "__main__":
    main()
