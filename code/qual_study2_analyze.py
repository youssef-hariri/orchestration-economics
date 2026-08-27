#!/usr/bin/env python3
"""Protocol 10 sec 5 — locked analysis plan.

Loads closed-coding vectors + triples, computes:
- prevalence profile per family x role (orig/refined/fsn), averaged over both coders;
- RQ2 convergence: share of codes where refined moves toward fsn vs away;
- RQ1 frontier residual edge: codes with fsn - refined >= 0.30 (kappa-reliable only);
- RQ3 saturation: count of codes that changed orig->refined per family.
Output: results/qual2_analysis.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGE_THRESHOLD = 0.30


def main():
    pack = json.load(open(ROOT / "runs/qual2/triples.json"))
    fam_of = {t["tripleId"]: t["family"] for t in pack["triples"]}
    kappa_res = json.load(open(ROOT / "results/qual2_kappa.json"))
    codebook = json.load(open(ROOT / "results/qual2_codebook.json"))["items"]
    ids = [c["id"] for c in codebook]
    reliable = {c for c in ids if kappa_res["per_item"][c]["kappa"] >= 0.70}

    vecs = {}  # key -> coder -> vector
    for line in open(ROOT / "runs/logs/qual2_closed.jsonl"):
        j = json.loads(line)
        if j.get("vector") is not None:
            vecs.setdefault(j["key"], {})[j["coder_family"]] = j["vector"]

    FAMS = ["kimi", "claude", "qwen"]
    # prevalence[fam][role][cid] = mean presence over texts and coders
    prev = {f: {r: {c: [] for c in ids} for r in ["orig", "refined", "fsn"]} for f in FAMS}
    n_ok = 0
    for t in pack["triples"]:
        for role in ["orig", "refined", "fsn"]:
            key = f"{t['tripleId']}:{role}"
            v = vecs.get(key)
            if not v or len(v) < 2:
                continue
            n_ok += 1
            for c in ids:
                prev[t["family"]][role][c].append(
                    sum(v[k][c] for k in v) / len(v))

    prevalence = {f: {r: {c: round(sum(v) / len(v), 3) if v else None
                          for c, v in prev[f][r].items()}
                      for r in prev[f]} for f in FAMS}

    # RQ2 convergence: per family, per code, delta_toward =
    # |orig-fsn| - |refined-fsn|  (>0 means refined moved toward frontier)
    convergence = {}
    for f in FAMS:
        moved = stayed = 0
        per_code = {}
        for c in ids:
            o, r, s = prevalence[f]["orig"][c], prevalence[f]["refined"][c], prevalence[f]["fsn"][c]
            if o is None or r is None or s is None:
                continue
            dt = abs(o - s) - abs(r - s)
            per_code[c] = round(dt, 3)
            if dt > 0.05:
                moved += 1
            elif dt < -0.05:
                stayed += 1
        convergence[f] = {"toward": moved, "away": stayed, "flat": len(ids) - moved - stayed,
                          "share_toward": round(moved / len(ids), 2), "per_code": per_code}

    # RQ1 frontier residual edge (reliable codes only)
    edge = {}
    for f in FAMS:
        rows = []
        for c in ids:
            r, s = prevalence[f]["refined"][c], prevalence[f]["fsn"][c]
            if r is None or s is None:
                continue
            gap = s - r
            rows.append({"code": c, "fsn": s, "refined": r, "gap": round(gap, 3),
                         "kappa_reliable": c in reliable})
        rows.sort(key=lambda x: -x["gap"])
        edge[f] = [x for x in rows if x["gap"] >= EDGE_THRESHOLD and x["kappa_reliable"]]

    # RQ3 saturation: codes that changed orig->refined (|delta| >= 0.2)
    saturation = {}
    for f in FAMS:
        changed = [c for c in ids
                   if prevalence[f]["orig"][c] is not None and prevalence[f]["refined"][c] is not None
                   and abs(prevalence[f]["refined"][c] - prevalence[f]["orig"][c]) >= 0.2]
        saturation[f] = {"n_changed_codes": len(changed), "changed_codes": changed}

    result = {"n_texts_coded": n_ok, "pooled_kappa": kappa_res["pooled_kappa"],
              "kappa_reliable_codes": sorted(reliable),
              "items_below_threshold": kappa_res["items_below_threshold"],
              "prevalence": prevalence, "convergence_rq2": convergence,
              "frontier_edge_rq1": edge, "saturation_rq3": saturation}
    dst = ROOT / "results/qual2_analysis.json"
    dst.write_text(json.dumps(result, indent=1) + "\n")
    print(f"-> {dst}")
    print(f"pooled kappa={kappa_res['pooled_kappa']}; below-threshold codes: "
          f"{kappa_res['items_below_threshold']}")
    for f in FAMS:
        cv = convergence[f]
        print(f"{f}: RQ2 toward={cv['toward']} away={cv['away']} flat={cv['flat']} "
              f"| RQ3 changed codes={saturation[f]['n_changed_codes']}")
        for e in edge[f]:
            print(f"  edge: {e['code']} fsn={e['fsn']:.2f} refined={e['refined']:.2f} gap={e['gap']:+.2f}")


if __name__ == "__main__":
    main()
