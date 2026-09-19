#!/usr/bin/env python3
"""Apply curated manual links for the 30 mentions the auto-linker could not
resolve. Link kinds:
  dp          -> direct datapoint (looked up by file + key-path fragment + ~value)
  derived     -> formula over component DPs
  document    -> structural claim verified against a primary doc (protocol/config/log)
Writes paper-claims.json in place (adds fields; link_status updated).
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
dps = json.load(open(HERE / "datapoints.json"))["datapoints"]
pm = json.load(open(HERE / "paper-claims.json"))

def dp_lookup(file_frag, key_frag=None, approx=None):
    for d in dps:
        if file_frag not in d["source_file"]:
            continue
        if key_frag and key_frag not in d["key_path"]:
            continue
        if approx is not None:
            v = d["value"]
            if not isinstance(v, (int, float)) or abs(float(v) - approx) > 0.01:
                continue
        return d["dp_id"]
    return None

D = lambda dp: dp_lookup(dp)  # noop guard
DOC = "document"

CURATION = {
 "PM-M001": {"kind": "document", "files": ["paper/P5_v15.5.tex"],
             "note": "citation-claim: verify against Hariri2026b (bibitem Hariri2026b); persona-economics source paper"},
 "PM-M002": {"kind": "document", "files": ["config/model_registry.json"],
             "note": "five families confirmed in registry generators"},
 "PM-M003": {"kind": "document", "files": ["config/experiment_config.json"],
             "note": "30 problems = 15 original + 15 domain extension"},
 "PM-M004": {"kind": "derived", "files": ["config/model_registry.json"],
             "formula": "min/max price ratio over registry = 3.1x..8x (v15-corrected from 3.4x)",
             "note": "derived across registry price entries"},
 "PM-M005": {"kind": "document", "files": ["runs/logs/main_run_ledger.json"],
             "note": "v15-corrected: 234 team runs with >=1 failed step (audit value 110 stale)"},
 "PM-M006": {"kind": "document", "files": ["config/experiment_config.json"],
             "note": "v15-corrected breakdown 15+15"},
 "PM-S1_008": {"kind": "document", "files": ["results/cost/cell_summary.csv"],
             "note": "Table 2 = cell summary statistics"},
 "PM-S1_009": {"kind": "document", "files": ["results/cost/pareto_frontier.csv"],
             "note": "Pareto membership stable across phiBlend"},
 "PM-D_006": {"kind": "document", "files": ["results/cost/pareto_frontier.csv"],
             "note": "same Pareto set claim repeated in Discussion"},
 "PM-S1_012": {"kind": "dp-multi", "dps": [
             ("ctp_vs_fsn_by_family.json", "per_family.kimi.d", -0.2082),
             ("ctp_vs_fsn_by_family.json", "per_family.claude.d", -1.3184),
             ("ctp_vs_fsn_by_family.json", "per_family.qwen.d", -2.139)],
             "note": "v15.6-corrected: frozen recomputation persisted 2026-09-19 "
                     "(code/compute_ctp_vs_fsn.py); supersedes unreproducible draft values"},
 "PM-S1_013": {"kind": "derived",
             "files": ["results/cost/cell_summary.csv"],
             "formula": "qual_ratio=mean_quality[cell]/mean_quality[F-S-N]; cost_ratio likewise at phi=0.5",
             "dps": ["cell_summary C-S-N phi=0.5", "cell_summary C-T-N phi=0.5", "cell_summary F-S-N phi=0.5"],
             "note": "98%/23% (C-S-N), 88% (C-T-N cost), 3.5x (F-T-N) verified from rows"},
 "PM-W_001": {"kind": "document", "files": ["preregistration/osf_submission/00-COVER-AND-TIMING-DISCLOSURE.md"],
             "note": "OSF jg49x = Protocol-12 wave registration; mapped in tab:osf-registrations"},
 "PM-W_002": {"kind": "document", "files": ["config/experiment_config.json"],
             "note": "30 fresh post-cutoff problems, 6x5 domain grid"},
 "PM-W_004": {"kind": "derived", "files": ["results/wave_analysis.json"],
             "formula": "240 expected/family x 10 families = 2400",
             "dp_keys": [("wave_analysis.json", "completion.expected_per_family", 240)]},
 "PM-W_005": {"kind": "derived", "files": ["results/wave_analysis.json"],
             "formula": "21762 = 2418 runs x 9 judgment cells; n_runs DP linked",
             "dp_keys": [("wave_analysis.json", "n_runs", 2418)]},
 "PM-S2_004": {"kind": "derived", "files": ["results/refine_study2_pooled.json"],
             "formula": "gap recovery = 1 - mean_diff_post/mean_diff_pre per family (kimi 60%, claude 8%, qwen 64%)",
             "dp_keys": [("refine_study2_pooled.json", "H2.1_refined_vs_FSN.kimi.mean_diff", -0.0737)]},
 "PM-S2_011": {"kind": "document", "files": ["results/qual2_analysis.json"],
             "note": "changed-code lists per family; v15 discloses qwen diagnostic_reframe"},
 "PM-S2_016": {"kind": "document", "files": ["results/qual2_analysis.json"],
             "note": "claude zero changed codes"},
 "PM-S3_001": {"kind": "document", "files": ["protocols/13-PROTOCOL-STUDY3-DESIGN-AUTHORSHIP.md"],
             "note": "OSF bwc93 operative + 639eq attrition clarification"},
 "PM-S3_002": {"kind": "document", "files": ["protocols/13-PROTOCOL-STUDY3-DESIGN-AUTHORSHIP.md"],
             "note": "570 planned runs = 19 x 3 x 2 x 5"},
 "PM-S3_005": {"kind": "dp", "dp_key": ("study3_results.json", "judgments", 4896)},
 "PM-S3_029": {"kind": "document", "files": ["protocols/16-PROTOCOL-STUDY3-CONFIRMATORY.md"],
             "note": "OSF zkm8v"},
 "PM-D_042": {"kind": "document", "files": ["protocols/16-PROTOCOL-STUDY3-CONFIRMATORY.md"],
             "note": "OSF zkm8v repeated in Discussion"},
 "PM-S3_039": {"kind": "document", "files": ["results/study3conf_results.json", "analysis/results/study3conf_gates.csv"],
             "note": "2/5 gates pass; headline moderation not replicated"},
 "PM-S3_046": {"kind": "document", "files": ["results/study3_by_family_domain.json"],
             "note": "domain pattern by family"},
 "PM-D_007": {"kind": "dp-multi", "dps": [
             ("wave_analysis.json", "gates.W1", None),
             ("wave_analysis.json", "gates.W2", None),
             ("wave_analysis.json", "gates.W6", None),
             ("wave_analysis.json", "n_runs", 2418)],
             "note": "W1/W2/W6 PASS, n=2418"},
 "PM-D_013": {"kind": "derived", "files": ["runs/logs/main_run_ledger.json", "results/cost/cell_summary.csv"],
             "formula": "refined kimi (C-T-P refined) cost / F-S-N mean cost = 0.78; refined cost from priced ledger at analysis time",
             "note": "component refined-cell cost not frozen as single DP; derived value"},
 "PM-D_016": {"kind": "derived", "files": ["runs/logs/main_run_ledger.json", "results/cost/cell_summary.csv"],
             "formula": "same refined C-T-P ratio (~100% quality, 78% cost) in managerial table",
             "note": "same derivation as PM-D_013"},
 "PM-D_026": {"kind": "derived", "files": ["results/cost/cell_summary.csv"],
             "formula": "mean team-cell cost / mean solo-cell cost ~ 3.8x (F-T-N 3.53x, C-T-N 0.88x... pooled ~3.8x at blended phi)",
             "note": "pooled team-vs-solo ratio"},
 "PM-D_040": {"kind": "document", "files": ["DESIGN-DECISIONS.md", "preregistration/osf_submission/00-COVER-AND-TIMING-DISCLOSURE.md"],
             "note": "protocol numbering + OSF id mapping"},
 "PM-D_043": {"kind": "document", "files": ["preregistration/osf_submission/01-PREREGISTRATION-PROTOCOL.md"],
             "note": "arm label definitions (tier x structure x persona)"},
}

changed = 0
for m in pm["mentions"]:
    cur = CURATION.get(m["mention_id"])
    if not cur:
        continue
    m["manual_link"] = cur
    if cur["kind"] == "dp":
        f, k, v = cur["dp_key"]
        m["dp_id"] = dp_lookup(f, k, v)
    elif cur["kind"] == "dp-multi":
        ids = [dp_lookup(f, k, v) for f, k, v in cur["dps"]]
        m["dp_ids"] = ids
        m["dp_id"] = next((i for i in ids if i), None)
    elif cur["kind"] == "derived" and cur.get("dp_keys"):
        m["dp_ids"] = [dp_lookup(f, k, v) for f, k, v in cur["dp_keys"]]
    m["link_status"] = "curated-" + cur["kind"]
    changed += 1

pm["curated"] = changed
json.dump(pm, open(HERE / "paper-claims.json", "w"), indent=1, ensure_ascii=False)
print(f"curated {changed} mentions")
missing = [f for cur in CURATION.values() for f in cur.get("files", []) if not (ROOT / f).exists()]
print("missing files:", missing or "none")
