#!/usr/bin/env python3
"""Build the two-file claim map, data-first (no audit-derived 'quotes').

datapoints.json   : canonical registry, DP-id -> value + source file + JSON key
                    path (or CSV row) + VERBATIM excerpt + analysis script.
paper-claims.json : every audited paper statement -> verbatim sentence pulled
                    from P5_v15.6.tex + DP-id link (by value match).
Decisions/citations carry over from claim-map.json (already primary-sourced).
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / "paper" / "P5_v15.6.tex"
AUDIT = ROOT / "paper" / "P5_v14.3-audit-2026-09-16"
HERE = Path(__file__).parent

SCRIPT_MAP = {  # results file -> analysis script that produced it
    "wave_analysis.json": "code/analyze_wave.py",
    "wave_analysis_minimax_promo.json": "code/analyze_wave.py",
    "interim1_sequential_analysis.json": "code/analyze_main.py",
    "interim2_analysis.json": "code/analyze_main.py",
    "exploratory_analysis.json": "code/analyze_exploratory.py",
    "exploratory_heterogeneity.json": "code/exploratory_heterogeneity.py",
    "persona_heterogeneity.json": "code/exploratory_heterogeneity.py",
    "cross_family.json": "code/cross_family.py",
    "pilot_v2_analysis.json": "code/analyze_pilot_v2.py",
    "cost_effectiveness.json": "code/cost_effectiveness.py",
    "qual2_analysis.json": "code/qual2_analysis.py",
    "qual2_kappa.json": "code/qual2_analysis.py",
    "qual_kappa.json": "code/qual_kappa.py",
    "qual_themes.json": "code/qual_themes.py",
    "qual2_codebook.json": "code/qual2_analysis.py",
}

datapoints, dp_index = [], {}   # (normvalue, basename) -> DP-id

def normnum(x):
    try:
        return round(float(x), 6)
    except (TypeError, ValueError):
        return None

def add_dp(source, key_path, value, excerpt, kind, segments=None):
    dp_id = f"DP-{len(datapoints)+1:04d}"
    datapoints.append({"dp_id": dp_id, "kind": kind, "value": value,
                       "source_file": source, "key_path": key_path, "key_segments": segments,
                       "verbatim_excerpt": excerpt[:400],
                       "analysis_script": SCRIPT_MAP.get(Path(source).name)})
    n = normnum(value)
    if n is not None:
        dp_index.setdefault((n, Path(source).name), dp_id)
    return dp_id

def walk_json(obj, path, source, depth=0, segments=None):
    segments = segments or []
    if isinstance(obj, dict):
        if len(obj) <= 12 and all(not isinstance(v, (dict, list)) for v in obj.values()):
            excerpt = json.dumps(obj, ensure_ascii=False)
            for k, v in obj.items():
                if isinstance(v, (int, float, str)) and not isinstance(v, bool):
                    add_dp(source, f"{path}.{k}" if path else k, v, excerpt, "json-scalar",
                           segments + [k])
        else:
            for k, v in obj.items():
                p = f"{path}.{k}" if path else str(k)
                if isinstance(v, (int, float, str)) and not isinstance(v, bool):
                    add_dp(source, p, v, json.dumps({k: v}, ensure_ascii=False), "json-scalar",
                           segments + [k])
                else:
                    walk_json(v, p, source, depth + 1, segments + [k])
    elif isinstance(obj, list):
        if len(obj) <= 50:
            for i, v in enumerate(obj):
                walk_json(v, f"{path}[{i}]", source, depth + 1, segments + [i])

# ---- 1. JSON results files -------------------------------------------------
for jf in sorted((ROOT / "results").rglob("*.json")):
    rel = str(jf.relative_to(ROOT))
    try:
        walk_json(json.load(open(jf)), "", rel)
    except Exception as e:
        print(f"skip {rel}: {e}", file=sys.stderr)

# ---- 2. CSV stats files (one DP per row; excerpt = raw CSV line) -----------
for cf in sorted((ROOT / "analysis" / "results").glob("*.csv")):
    rel = str(cf.relative_to(ROOT))
    lines = cf.read_text(encoding="utf-8", errors="replace").splitlines()
    rdr = csv.DictReader(lines)
    for i, row in enumerate(rdr):
        raw_line = lines[i + 1] if i + 1 < len(lines) else ""
        add_dp(rel, f"row[{i}]", dict(row), raw_line, "csv-row")

# ---- 3. paper mentions: verbatim sentence from tex, linked to DP -----------
tex = TEX.read_text(encoding="utf-8")
tex_flat_lines = tex.splitlines()
audit_files = ["methods_study1_partial_audit.json", "study1_remaining_audit.json",
               "wave_study2_audit.json", "study3_audit.json", "discussion_audit.json"]

def dec_places(tok):
    return len(tok.split(".")[1]) if "." in tok else 0

def values_match(dp_val, tok):
    """Paper token matches DP value allowing rounding to the token's
    precision, and percent/ proportion (x100) equivalence."""
    try:
        v, t = float(dp_val), float(tok.replace(",", "").rstrip("%"))
    except (TypeError, ValueError):
        return False
    d = dec_places(tok.replace(",", "").rstrip("%"))
    for cand in (v, v * 100, v / 100):
        if round(cand, d) == t:
            return True
    return False

def find_verbatim(paper_value, claim, hint_line):
    """Locate a sentence in the tex containing a distinctive numeric token;
    search near the audit snapshot line first, then the whole document."""
    toks = re.findall(r"-?\d[\d,]*\.?\d*%?", paper_value or "")
    toks += [t for t in re.findall(r"-?\d+\.\d+", claim or "") if t not in toks]
    lines = tex_flat_lines
    lo = max(0, (hint_line or 1) - 150)
    hi = min(len(lines), (hint_line or len(lines)) + 150)
    windows = [(lo, hi)]
    if lo > 0 or hi < len(lines):
        windows.append((0, len(lines)))   # fallback: whole document
    for lo, hi in windows:
        window = " ".join(lines[lo:hi]).replace(",", "")
        found = []
        for tok in dict.fromkeys(toks):
            core = tok.replace(",", "").rstrip("%")
            if not core or len(core) < 2:
                continue
            if re.search(r"(?<![\d.])" + re.escape(core) + r"(?![\d.])", window):
                found.append(tok)
        if found:
            tok = found[0]
            core = tok.replace(",", "").rstrip("%")
            m = re.search(r"(?<![\d.])" + re.escape(core) + r"(?![\d.])", window)
            s = window.rfind(".", 0, m.start()) + 1
            e = window.find(".", m.end()) + 1
            abs_pos = sum(len(l) + 1 for l in lines[:lo]) + m.start()
            line_no = tex[:abs_pos].count("\n") + 1
            return re.sub(r"\s+", " ", window[s:e]).strip()[:500], line_no, found
    return None, None, []

SECTION_HINT = {"S1": ("interim", "exploratory", "persona", "cost", "qual_kappa"),
                "S2": ("refine_study2", "qual2", "cross_family"),
                "S3": ("study3",),
                "W":  ("wave",),
                "M":  ("model_registry", "experiment_config", "interim", "qual"),
                "D":  ("cost", "interim", "wave", "study3", "exploratory")}

def search_dps(toks, base=None, cid=""):
    pref = SECTION_HINT.get(cid.split("_")[0], ())
    def score(dp):
        n = Path(dp["source_file"]).name
        return 0 if any(h in n for h in pref) else 1
    cands = sorted(datapoints, key=score)
    for tok in toks:
        for dp in cands:
            if base and Path(dp["source_file"]).name != base:
                continue
            vals = dp["value"].values() if isinstance(dp["value"], dict) else [dp["value"]]
            if any(values_match(v, tok) for v in vals):
                return dp["dp_id"]
    return None

mentions, linked, unlinked = [], 0, 0
for fn in audit_files:
    for r in json.load(open(AUDIT / fn)):
        quote, line_no, toks = find_verbatim(r.get("paper_value"), r.get("claim"),
                                             r.get("line_start"))
        dp_id = None
        evs = r.get("evidence") if isinstance(r.get("evidence"), list) else [r.get("evidence")]
        bases = [Path(m.group(1)).name for ev in evs
                 if ev and (m := re.search(r"([\w./-]+\.(?:json|csv))", ev))]
        for base in bases or [None]:
            dp_id = search_dps(toks, base, r["id"])
            if dp_id:
                break
        if not dp_id:
            pv = r.get("paper_value") or ""
            if re.search(r"osf\.io|\b[0-9a-z]{5}\b.*operative|zkm8v|jg49x|bwc93", pv, re.I):
                cur = "structural-osf-id — link to protocol file, not a datapoint"
            elif re.search(r"\{C-S-P|arm labels|See Table|codes listed|Domain pattern|families", pv):
                cur = "structural-label — link to config/protocol doc"
            elif re.search(r"%|×|x\b", pv) and "," in pv:
                cur = "derived-value — needs derived-from formula link to multiple DPs"
            else:
                cur = "needs-manual-link"
        else:
            cur = None
        mentions.append({"mention_id": f"PM-{r['id']}", "claim_text": r.get("claim"),
                         "paper_value": r.get("paper_value"),
                         "paper_file": "paper/P5_v15.6.tex",
                         "paper_line": line_no, "verbatim_quote": quote,
                         "dp_id": dp_id, "curation": cur,
                         "link_status": "linked" if dp_id else ("quote-found-unlinked" if quote else "quote-not-found")})
        linked += bool(dp_id)
        unlinked += not dp_id

(HERE / "datapoints.json").write_text(json.dumps(
    {"schema": "datapoints-v1", "generated": "2026-09-19",
     "count": len(datapoints), "datapoints": datapoints}, indent=1, ensure_ascii=False))
(HERE / "paper-claims.json").write_text(json.dumps(
    {"schema": "paper-claims-v1", "generated": "2026-09-19", "paper": str(TEX.relative_to(ROOT)),
     "count": len(mentions), "linked": linked, "unlinked": unlinked,
     "mentions": mentions}, indent=1, ensure_ascii=False))
print(f"datapoints: {len(datapoints)}  mentions: {len(mentions)}  linked: {linked}  unlinked: {unlinked}")
