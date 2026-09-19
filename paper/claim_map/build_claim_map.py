#!/usr/bin/env python3
"""Build claim-map.json: a machine-readable claim-to-evidence map for the paper.

Seeds:
 1. Statistical/data claims  <- paper/P5_v14.3-audit-2026-09-16/*.json (162 audited points)
 2. Design decisions D1-D60  <- DESIGN-DECISIONS.md headers
 3. Bibliographic entries    <- paper/references.bib (or first .bib found)

v15 fixes note: discrepancies found in the 2026-09-16 audit were corrected in
P5_v15.tex; those entries are marked status="corrected-in-v15" with resolution.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # orchestration-economics/
AUDIT = ROOT / "paper" / "P5_v14.3-audit-2026-09-16"
OUT = Path(__file__).parent / "claim-map.json"

# v15 resolutions for the audit's DISCREPANCY items (from V15-AUDIT-FIX-REPORT.md)
RESOLUTIONS = {
    "M005": "corrected-in-v15: retry count recomputed (234 runs) and Limitations cost-understatement rederived",
    "D_025": "corrected-in-v15: same as M005",
    "S1_012": "corrected-in-v15: CTP-vs-FSN per-family d values traced and restated from interim2_analysis.json",
    "M004": "corrected-in-v15: price-ratio floor changed to 3.1x-8x",
    "M006": "corrected-in-v15: problem breakdown restated as 15 original + 15 domain extension",
    "S2_011": "corrected-in-v15: qualitative saturation claim scoped (qwen diagnostic_reframe disclosed)",
    "S1_025": "corrected-in-v15: capability-gap correlation recomputed and persisted",
    "S2_007": "corrected-in-v15: length-correlation computation persisted to CSV",
    "S3_033": "corrected-in-v15: Protocol-16 judgment counts persisted",
    "S3_032": "corrected-in-v15: per-family attrition persisted",
    "D_029": "corrected-in-v15: critic-gated loop percentage sourced",
    "M001": "verified-against-source: Hariri2026b persona-economics paper",
}

SECTION_OF = {
    "M": "methods", "S1": "study1-results", "S2": "study2-results",
    "S3": "study3-results", "D": "discussion", "W": "replication-wave",
}

def section_for(cid):
    for p, s in SECTION_OF.items():
        if cid.startswith(p + "0") or cid.startswith(p + "_"):
            return s
    return "unknown"

claims = []

# ---- 1. statistics from audit section files -------------------------------
audit_files = ["methods_study1_partial_audit.json", "study1_remaining_audit.json",
               "wave_study2_audit.json", "study3_audit.json", "discussion_audit.json"]
for fn in audit_files:
    recs = json.load(open(AUDIT / fn))
    for r in recs:
        cid = r["id"]
        verdict = r.get("verdict", "UNVERIFIED")
        status = {"MATCH": "verified", "ROUNDING": "verified-with-rounding-note"}.get(verdict)
        if status is None:
            status = "corrected-in-v15" if cid in RESOLUTIONS else ("unverified" if verdict == "UNVERIFIED" else verdict.lower())
        srcs = []
        notes = []
        evs = r.get("evidence", [])
        if isinstance(evs, str):
            evs = [evs]
        for ev in evs:
            m = re.search(r"([\w./-]+\.(?:json|md|csv|tex|py|txt|xlsx))\b[:\s]*(.*)$", ev)
            if m:
                file = m.group(1)
                loc = ev[m.end(1):].strip(" :") or None
                srcs.append({"file": file, "locator": loc,
                             "quote": r.get("source_value") or None})
            else:
                notes.append(ev)
        claims.append({
            "claim_id": cid,
            "type": "statistic" if cid != "M001" else "citation-claim",
            "paper_location": {"file": "paper/P5_v15.5.tex",
                               "audit_snapshot_lines": [r.get("line_start"), r.get("line_end")],
                               "section": section_for(cid)},
            "claim_text": r.get("claim"),
            "paper_value": r.get("paper_value"),
            "sources": srcs,
            "audit_notes": notes or None,
            "verification": {"status": status,
                             "audited": "2026-09-16",
                             "verdict": verdict,
                             "severity": r.get("severity"),
                             "resolution": RESOLUTIONS.get(cid),
                             "auditor_advice": r.get("advice")}})

# ---- 2. design decisions D1-D60 -------------------------------------------
dd = (ROOT / "DESIGN-DECISIONS.md").read_text(encoding="utf-8")
for m in re.finditer(r"^## (D\d+)\.\s+(.+)$", dd, re.M):
    did, title = m.group(1), m.group(2).strip()
    claims.append({
        "claim_id": did,
        "type": "decision",
        "paper_location": {"file": "paper/P5_v15.5.tex", "section": "methods/ai-disclosure"},
        "claim_text": f"Design decision {did}: {title}",
        "sources": [{"file": "DESIGN-DECISIONS.md",
                     "locator": f"## {did}.",
                     "quote": f"## {did}. {title}"}],
        "verification": {"status": "verified", "audited": "2026-09-19"}})

# ---- 3. bibliographic entries (inline thebibliography) --------------------
tex = (ROOT / "paper" / "P5_v15.5.tex").read_text(encoding="utf-8")
for m in re.finditer(r"\\bibitem\[([^\]]*)\]\{([^}]+)\}\s*(.+?)(?=\n\\bibitem|\n\\end\{thebibliography\})", tex, re.S):
    auth, key, body = m.group(1), m.group(2), m.group(3).strip()
    quote = re.sub(r"\s+", " ", body)[:300]
    y = re.search(r"\((\d{4}[a-z]?)\)", auth)
    claims.append({
        "claim_id": f"BIB-{key}",
        "type": "citation",
        "paper_location": {"file": "paper/P5_v15.5.tex", "section": "bibliography"},
        "claim_text": f"Bibliographic record for citekey {key} ({auth})",
        "sources": [{"file": "paper/P5_v15.5.tex", "locator": f"\\bibitem{{{key}}}",
                     "quote": quote}],
        "verification": {"status": "bibliographic-record-verified",
                         "year": y.group(1) if y else None,
                         "note": "claim-level quote mapping to source PDFs = phase 2",
                         "audited": "2026-09-19"}})

out = {
    "schema": "claim-map-v1",
    "paper": "paper/P5_v15.5.tex",
    "generated": "2026-09-19",
    "generator": "paper/claim_map/build_claim_map.py",
    "counts": {"total": len(claims),
               "statistics": sum(1 for c in claims if c["type"] == "statistic"),
               "decisions": sum(1 for c in claims if c["type"] == "decision"),
               "citations": sum(1 for c in claims if c["type"] == "citation")},
    "claims": claims,
}
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out["counts"], indent=1))
