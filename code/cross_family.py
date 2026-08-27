#!/usr/bin/env python3
"""Protocol 09 sec 9 — cross-family secondary analysis (locked rule, descriptive).

(A) Study-1 original C-T-P vs other families' F-S-N, all 6 directions, Holm.
(B) Study-2 refined answers vs other families' F-S-N, same minimal-runId rule.
Zero new API calls — pure recomputation over locked data.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import analyze_main as am            # noqa: E402
import refine_study2_analyze as ra   # noqa: E402

FAMS = ["kimi", "claude", "qwen"]


def fsn_min_by_problem(fsn_rows):
    """family -> problemId -> minimal-runId F-S-N row (locked rule)."""
    idx = {}
    for r in fsn_rows:
        key = (r["family"], str(r["problemId"]))
        if key not in idx or r["runId"] < idx[key]["runId"]:
            idx[key] = r
    return idx


def main():
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    meta = {r["runId"]: r for r in store["runs"] if r.get("fulltext")}
    recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    df = pd.DataFrame(am.build_run_table(recs, meta))

    ctp = df[(df.tier == "C") & (df.structure == "T") & (df.persona == "P")]
    fsn = df[(df.tier == "F") & (df.structure == "S") & (df.persona == "N")]
    fsn_idx = fsn_min_by_problem(fsn.to_dict("records"))

    # ---- (A) original C-T-P vs cross-family F-S-N, 6 directions
    dirs = [(a, b) for a in FAMS for b in FAMS if a != b]
    A = {}
    for a, b in dirs:
        c, f = [], []
        for r in ctp[ctp.family == a].to_dict("records"):
            mate = fsn_idx.get((b, str(r["problemId"])))
            if mate is not None:
                c.append(float(r["composite"]))
                f.append(float(mate["composite"]))
        A[f"{a}->{b}"] = ra.paired_stats(np.array(c) - np.array(f))
    pvals = np.array([A[k]["p_one_sided"] for k in A])
    holm = ra.holm(pvals)
    for k, h in zip(A, holm):
        A[k]["p_holm"] = round(float(h), 5)
        A[k]["sig_holm_05"] = bool(h < 0.05)

    # ---- (B) refined answers vs cross-family F-S-N
    pairs = (json.load(open(ROOT / "runs/refine/sample_pilot.json"))["pairs"]
             + json.load(open(ROOT / "runs/refine/sample_extension.json"))["pairs"])
    raw = []
    for jf in ["runs/logs/refine_judgments_pilot.jsonl",
               "runs/logs/refine_judgments_extension.jsonl"]:
        raw += [json.loads(l) for l in open(ROOT / jf) if l.strip()]
    ref_rows = ra.agg([r for r in raw if not r.get("error") and not r.get("incomplete")])
    main_rows = ra.agg(recs)

    B = {}
    for a, b in dirs:
        r, f = [], []
        for p in pairs:
            if p["family"] != a:
                continue
            mate = fsn_idx.get((b, str(p["problemId"])))
            ref = ref_rows.get(f"R{p['ctp_runId']}")
            if mate is not None and ref is not None:
                m = main_rows.get(mate["runId"])
                if m is not None:
                    r.append(ref["composite"])
                    f.append(m["composite"])
        B[f"{a}->{b}"] = ra.paired_stats(np.array(r) - np.array(f))

    result = {"protocol": "09", "section": "9 cross-family secondary",
              "status": "descriptive (family quality confounded with design)",
              "A_original_ctp_vs_cross_family_fsn": A,
              "B_refined_vs_cross_family_fsn": B}
    dst = ROOT / "results/cross_family.json"
    dst.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"done -> {dst}\n")
    print("(A) original C-T-P vs cross-family F-S-N:")
    for k, v in A.items():
        print(f"  {k:13s} n={v['n']:3d} diff={v['mean_diff']:+.3f} d={v['d']:+.3f} "
              f"CI={v['ci95_boot']} p_holm={v['p_holm']:.4f}"
              f" {'WIN' if v['sig_holm_05'] and v['mean_diff'] > 0 else ''}")
    print("\n(B) refined C-T-P vs cross-family F-S-N:")
    for k, v in B.items():
        print(f"  {k:13s} n={v['n']:3d} diff={v['mean_diff']:+.3f} d={v['d']:+.3f} "
              f"CI={v['ci95_boot']}")


if __name__ == "__main__":
    main()
