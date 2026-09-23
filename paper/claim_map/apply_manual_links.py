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

# --- 2026-09-21 audit-era additions: 3 new cost-range mentions introduced in v15.6 --------
# (Strategic-implication rewordings of the "$0.002 refinement pass" claims;
# values trace to cost_effectiveness.json refined_ctp_points mean_refine_cost)
REFINE_DPS = ["DP-0084", "DP-0089", "DP-0094"]  # kimi/claude/qwen mean_refine_cost
NEW_MENTIONS = [
 {"mention_id": "PM-S2_901",
  "claim_text": "Refinement pass costs a fraction of a cent per output ($0.001-0.003, family-dependent)",
  "paper_value": "$0.001-0.003",
  "paper_file": "paper/P5_v15.6.tex", "paper_line": 97,
  "verbatim_quote": "costing a fraction of a cent per output (\\$0.001--0.003, family-dependent)",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "dp_ids": REFINE_DPS,
    "files": ["results/cost/cost_effectiveness.json"],
    "note": "range = min/max of per-family mean_refine_cost (qwen 0.00112, claude 0.00324), rounded to 3 decimals"},
  "link_status": "curated-derived"},
 {"mention_id": "PM-S2_902",
  "claim_text": "Refinement pass costs $0.001-0.003 per output (family-dependent; pooled mean approx $0.002)",
  "paper_value": "$0.001-0.003; mean ~$0.002",
  "paper_file": "paper/P5_v15.6.tex", "paper_line": 1615,
  "verbatim_quote": "A refinement pass costing \\$0.001--0.003 per output (family-dependent; pooled mean $\\approx$ \\$0.002)",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "dp_ids": REFINE_DPS,
    "files": ["results/cost/cost_effectiveness.json"],
    "note": "range from per-family mean_refine_cost; pooled mean of (0.00156, 0.00324, 0.00112) = 0.00197 ~= $0.002"},
  "link_status": "curated-derived"},
 {"mention_id": "PM-S2_903",
  "claim_text": "Fraction-of-a-cent refinement pass ($0.001-0.003, family-dependent)",
  "paper_value": "$0.001-0.003",
  "paper_file": "paper/P5_v15.6.tex", "paper_line": 2398,
  "verbatim_quote": "fraction-of-a-cent refinement pass (\\$0.001--0.003, family-dependent)",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "dp_ids": REFINE_DPS,
    "files": ["results/cost/cost_effectiveness.json"],
    "note": "same range derivation as PM-S2_901"},
  "link_status": "curated-derived"},
]
_existing = {m["mention_id"] for m in pm["mentions"]}
added = 0
for nm in NEW_MENTIONS:
    if nm["mention_id"] not in _existing:
        pm["mentions"].append(nm)
        added += 1
pm["count"] = len(pm["mentions"])
json.dump(pm, open(HERE / "paper-claims.json", "w"), indent=1, ensure_ascii=False)
print(f"added {added} new mentions (total {pm['count']})")

# --- 2026-09-21 audit additions: corrected Study-3 sentences (token split, gemini cost, domain means)
NEW2 = [
 {"mention_id": "PM-S3_901",
  "claim_text": "D-SELF vs D-FRONT tokens 34.8M vs 24.3M total; execution-driven (34.0M vs 23.6M); design 0.6M vs 0.7M (2-3%)",
  "paper_value": "34.8M/24.3M; 34.0M/23.6M; 0.6M/0.7M; 2-3%",
  "paper_file": "paper/P5_v15.6.tex",
  "verbatim_quote": "the gap is execution-driven ($34.0$M vs.\\ $23.6$M): design-stage usage is comparable across arms ($0.6$M vs.\\ $0.7$M, 2--3\\% of totals)",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "files": ["results/study3_token_split.json", "results/study3_results.json"],
    "note": "totals = study3_results cost_and_structure (DP-registered); split = study3_token_split rows (design+repair+execution), 2026-09-21 audit"},
  "link_status": "curated-derived"},
 {"mention_id": "PM-S3_902",
  "claim_text": "Gemini cheap pipelines roughly 1.7-4x cheaper than frontier solo (0.59x/0.24x)",
  "paper_value": "1.7-4x; 0.59x/0.24x",
  "paper_file": "paper/P5_v15.6.tex",
  "verbatim_quote": "roughly $1.7$--$4\\times$ cheaper than frontier solo ($0.59\\times$/$0.24\\times$ the cost per solution)",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "files": ["results/study3_economics.json"],
    "note": "reciprocals of gemini cost_ratio_front_vs_fsn 0.59 and cost_ratio_self_vs_fsn 0.24"},
  "link_status": "curated-derived"},
 {"mention_id": "PM-S3_903",
  "claim_text": "Pooled D-FRONT vs FSN domain means: strategy 4.08/4.00, marketing 4.08/4.01, HR 4.11/4.10, product 4.24/4.25, finance 3.81/3.99, operations 3.83/3.95",
  "paper_value": "six domain mean pairs",
  "paper_file": "paper/P5_v15.6.tex",
  "verbatim_quote": "tie in HR ($4.11$ vs.\\ $4.10$) and product ($4.24$ vs.\\ $4.25$), and lose in finance ($3.81$ vs.\\ $3.99$)",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "files": ["results/study3_by_family_domain.json"],
    "note": "unweighted pooled means across families per domain from frozen family x domain rows (descriptive file, underpowered by design)"},
  "link_status": "curated-derived"},
]
_ex2 = {m["mention_id"] for m in pm["mentions"]}
add2 = 0
for nm in NEW2:
    if nm["mention_id"] not in _ex2:
        pm["mentions"].append(nm); add2 += 1
pm["count"] = len(pm["mentions"])
json.dump(pm, open(HERE / "paper-claims.json", "w"), indent=1, ensure_ascii=False)
print(f"added {add2} 2026-09-21 audit mentions (total {pm['count']})")

# --- Conclusion rewrite (2026-09-23): new mentions
NEW3 = [
 {"mention_id": "PM-C_901",
  "claim_text": "Conclusion scope: 5,303 runs, 10 families, 49 problems",
  "paper_value": "5,303 runs; 10 families; 49 problems",
  "paper_file": "paper/P5_v15.6.tex",
  "verbatim_quote": "Across three pre-registered studies and two out-of-sample replications (5{,}303 runs, 10 model families, 49 business problems)",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "files": ["results/interim2_analysis.json", "results/wave_analysis.json", "results/study3_results.json", "results/study3conf_results.json"],
    "note": "5,303 = 1,900 Study-1 + 2,418 wave + 544 Study-3 + 441 Protocol-16; 49 problems = 19 confirmatory + 30 wave"},
  "link_status": "curated-derived"},
 {"mention_id": "PM-C_902",
  "claim_text": "Auto-designed cheap pipelines beat frontier solo for kimi/qwen/gemini at 0.24x-3.5x cost; claude loses (83%), gpt ties at 4x cost",
  "paper_value": "0.24x-3.5x; 83%; 4x",
  "paper_file": "paper/P5_v15.6.tex",
  "verbatim_quote": "at costs ranging from $0.24\\times$ to $3.5\\times$ the frontier-solo price; the remaining two favor frontier solo --- claude on quality (the pipeline reaches 83\\%), gpt-5.6 on cost (quality ties at $4\\times$ the price)",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "files": ["results/study3_economics.json", "results/study3_vs_frontier_solo.json"],
    "note": "range = gemini 0.24x to kimi 3.53x (D-SELF cost ratios); claude quality 82.6% rounds to 83%; gpt ratio 4.04x rounds to 4x; quality% from vs_frontier_solo means"},
  "link_status": "curated-derived"},
 {"mention_id": "PM-C_903",
  "claim_text": "Tier price gap 3.1-8x; cheap solo 98% quality at 23% cost = monetization of the gap; token usage comparable (7,670 vs 7,412)",
  "paper_value": "3.1-8x; 98%/23%",
  "paper_file": "paper/P5_v15.6.tex",
  "verbatim_quote": "Because token usage is comparable across tiers, the cheaper solo's advantage --- 98\\% of frontier quality at 23\\% of its cost",
  "dp_id": None, "curation": None,
  "manual_link": {"kind": "derived", "files": ["config/price_vector.json", "results/cost/cost_effectiveness.json"],
    "note": "price ratios 3.1-8x from frozen vector tier pairs; 98%/23% from cell_summary_primary (C-S-N 4.5066/4.5864 qual, 0.0194/0.0835 cost); tokens 7,670 vs 7,412"},
  "link_status": "curated-derived"},
]
_ex3 = {m["mention_id"] for m in pm["mentions"]}
add3 = 0
for nm in NEW3:
    if nm["mention_id"] not in _ex3:
        pm["mentions"].append(nm); add3 += 1
pm["count"] = len(pm["mentions"])
json.dump(pm, open(HERE / "paper-claims.json", "w"), indent=1, ensure_ascii=False)
print(f"added {add3} conclusion mentions (total {pm['count']})")
