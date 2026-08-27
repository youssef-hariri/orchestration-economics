#!/usr/bin/env python3
"""Protocol 10 — P0 length-correlation check + 30-triple sample + materials.

P0 (sec 2): correlate length ratio with composite change, per family + pooled.
Sample (sec 3): 30 triples (10/family), seed 20260801, blinded materials pack.
Outputs: runs/qual2/triples.json (materials), prints P0 results.
"""
import json
import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import analyze_main as am            # noqa: E402
import refine_study2_analyze as ra   # noqa: E402

SEED = 20260801
FAMS = ["kimi", "claude", "qwen"]


def main():
    pairs = (json.load(open(ROOT / "runs/refine/sample_pilot.json"))["pairs"]
             + json.load(open(ROOT / "runs/refine/sample_extension.json"))["pairs"])
    store = json.load(open(ROOT / "runs/fulltext/main_fulltext.json"))
    text_by_run = {r["runId"]: r.get("fulltext", "") for r in store["runs"]}

    refined = {}
    for lg in ["runs/logs/refine_pilot.jsonl", "runs/logs/refine_extension.jsonl"]:
        for line in open(ROOT / lg):
            j = json.loads(line)
            if j.get("refined_text"):
                refined[j["ctp_runId"]] = j

    raw = []
    for jf in ["runs/logs/refine_judgments_pilot.jsonl",
               "runs/logs/refine_judgments_extension.jsonl"]:
        raw += [json.loads(l) for l in open(ROOT / jf) if l.strip()]
    ref_rows = ra.agg([r for r in raw if not r.get("error") and not r.get("incomplete")])
    main_recs, _ = am.load_judgments(ROOT / "runs/logs/main_judgments.jsonl")
    main_rows = ra.agg(main_recs)

    # ---- P0: length ratio vs composite change
    print("P0: correlation(length ratio, composite change)")
    p0 = {}
    for fam in FAMS + ["pooled"]:
        sel = [p for p in pairs if fam == "pooled" or p["family"] == fam]
        lr, dc = [], []
        for p in sel:
            j = refined.get(p["ctp_runId"])
            o, r = main_rows.get(p["ctp_runId"]), ref_rows.get(f"R{p['ctp_runId']}")
            if j and o and r:
                lr.append(j["refined_len"] / j["orig_len"])
                dc.append(r["composite"] - o["composite"])
        lr, dc = np.array(lr), np.array(dc)
        pr = stats.pearsonr(lr, dc)
        sp = stats.spearmanr(lr, dc)
        spr = getattr(sp, "statistic", None)
        if spr is None:
            spr = sp.correlation
        spp = getattr(sp, "pvalue", None)
        if spp is None:
            spp = sp.pvalue
        p0[fam] = {"n": int(len(lr)), "pearson_r": round(float(pr[0]), 3),
                   "pearson_p": round(float(pr[1]), 4),
                   "spearman_r": round(float(spr), 3),
                   "spearman_p": round(float(spp), 4)}
        print(f"  {fam:7s} n={len(lr):3d} pearson r={pr[0]:+.3f} "
              f"(p={pr[1]:.3f}) spearman r={spr:+.3f} (p={spp:.3f})")

    # ---- sample 30 triples
    rng = random.Random(SEED)
    picked = []
    for fam in FAMS:
        ids = sorted(p["ctp_runId"] for p in pairs if p["family"] == fam)
        picked += rng.sample(ids, 10)
    pair_by_id = {p["ctp_runId"]: p for p in pairs}
    triples = []
    for i, cid in enumerate(sorted(picked)):
        p = pair_by_id[cid]
        triples.append({
            "tripleId": f"T{i + 1:02d}", "family": p["family"],
            "problemId": p["problemId"], "problem_text": p["problem_text"],
            "texts": {
                "orig": text_by_run[p["ctp_runId"]],
                "refined": refined[cid]["refined_text"],
                "fsn": text_by_run[p["fsn_runId"]],
            }})
    dst = ROOT / "runs/qual2/triples.json"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps({"seed": SEED, "p0": p0, "triples": triples},
                              indent=1, ensure_ascii=False) + "\n")
    print(f"\n30 triples -> {dst} (wave1 = first 2 per family: "
          f"{[t['tripleId'] for t in triples if int(t['tripleId'][1:]) % 10 <= 2][:8]}...)")


if __name__ == "__main__":
    main()
