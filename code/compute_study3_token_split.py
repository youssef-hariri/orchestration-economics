#!/usr/bin/env python3
"""Frozen: Study-3 token split, design stage vs execution stage (D63).
Motivation: paper draft attributed the D-SELF vs D-FRONT token gap
(34.8M vs 24.3M, study3_results.json cost_and_structure) to design-stage
iteration; the ledger shows design usage is near-identical and the gap is
execution-driven. This script persists the split so the corrected claim
traces to frozen data. Loaders follow code/study3_analysis.py conventions.
Output: results/study3_token_split.json"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "runs/logs/study3_ledger_v2.jsonl"

design, repair, execution, n = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
for line in open(LEDGER):
    r = json.loads(line)
    if r.get("status") != "completed":
        continue
    arm = r["arm"]
    n[arm] += 1
    design[arm] += (r.get("designer_usage") or {}).get("total_tokens", 0) or 0
    repair[arm] += (r.get("designer_usage_repair") or {}).get("total_tokens", 0) or 0
    for s in r.get("steps", []):
        execution[arm] += (s.get("usage") or {}).get("total_tokens", 0) or 0

rows = []
for arm in ("D-SELF", "D-FRONT"):
    tot = design[arm] + repair[arm] + execution[arm]
    rows.append({
        "arm": arm,
        "completed_runs": n[arm],
        "design_tokens": design[arm],
        "design_repair_tokens": repair[arm],
        "execution_tokens": execution[arm],
        "total_tokens": tot,
        "pct_design_of_total": round(100 * (design[arm] + repair[arm]) / tot, 2),
    })

out = {
    "study": "study3_token_split",
    "date_utc": "2026-09-21",
    "role": "frozen correction artifact (D63): splits study3_results.json cost_and_structure total_tokens into design vs execution",
    "source_ledger": "runs/logs/study3_ledger_v2.jsonl",
    "conventions": "identical to code/study3_analysis.py (completed runs only; total_tokens per usage record)",
    "rows": rows,
}
out_path = ROOT / "results/study3_token_split.json"
out_path.write_text(json.dumps(out, indent=1) + "\n")
for r in rows:
    print(r["arm"], "design:", r["design_tokens"], "exec:", r["execution_tokens"],
          "total:", r["total_tokens"], f"({r['pct_design_of_total']}% design)")
