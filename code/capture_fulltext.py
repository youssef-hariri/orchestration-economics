#!/usr/bin/env python3
"""A1.1 full-text capture (Amendment A1, D35).

Problem found in pilot diagnostics (results/QUALITATIVE-NOTES.md): the platform
run_status MCP tool truncates finalResponse at 16,000 chars
(api/mcp/tools/getRunStatus.ts MAX_RESPONSE_CHARS=16000), and pilot judges
scored the truncated text. Full answers survive in the granular archive
(runs/granular/*.json -> export.agentResponses[0].content).

This script builds the full-text solution store(s) that judge_v2.py consumes:

  1. runs/fulltext/pilot_fulltext.json     ALL 371 pilot runs
     (granular-archive content preferred; log text kept as fallback; each entry
     carries fulltextLen / logLen / cappedAt16012 / source)
  2. runs/fulltext/pilot_repair_capped.json  ONLY the runs that hit the cap
     (input for the optional pilot re-judge, D38 — executed only when the
     author authorizes, inside the discount window)

Run idempotently any time; no judging, no credits.

Main-run mode (after main_run.mjs completes):
  python3 code/capture_fulltext.py --tag main
  reads runs/logs/main_run_ledger.json (+ granular archive) and writes
  runs/fulltext/main_fulltext.json.
"""

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "runs" / "fulltext"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CAP = 16012  # 16000 chars + the 12-char marker "…[truncated]"
TAG = "main" if "--tag" in sys.argv and sys.argv[sys.argv.index("--tag") + 1] == "main" else "pilot"

if TAG == "pilot":
    logs = []
    for f in ["pilot_phaseA_2026-08-03.json", "pilot_phaseB_2026-08-03.json"]:
        logs += json.load(open(ROOT / "runs/logs" / f))["results"]
else:
    ledger_path = ROOT / "runs/logs/main_run_ledger.json"
    if not ledger_path.exists():
        sys.exit("main_run_ledger.json not found — run code/main_run.mjs first")
    logs = json.load(open(ledger_path))["results"]

# Granular archive indexed by runId (full export_run payload).
archive = {}
for path in glob.glob(str(ROOT / "runs/granular" / "*.json")):
    try:
        g = json.load(open(path))
        rid = g.get("runId")
        if rid is not None:
            archive[int(rid)] = g
    except Exception as e:  # noqa: BLE001 - logged, not fatal
        print(f"  [warn] unreadable archive {path}: {e}")

store, capped = {}, {}
n_granular_longer = 0
for r in logs:
    rid = r.get("runId")
    log_text = r.get("finalResponse") or ""
    arch_text = ""
    g = archive.get(rid) if isinstance(rid, int) else None
    if g:
        responses = (g.get("export") or {}).get("agentResponses") or []
        if responses:
            arch_text = responses[0].get("content") or ""
    # Prefer the longer of the two sources (archive is normally the full text).
    if len(arch_text) >= len(log_text):
        text, source = arch_text, "granular_archive"
    else:
        text, source = log_text, "run_log"
    if source == "granular_archive" and len(arch_text) > len(log_text):
        n_granular_longer += 1
    is_capped = len(log_text) == CAP
    entry = {
        "runId": rid,
        "problemId": r["problemId"],
        "cell": r["cell"],
        "family": r["family"],
        "status": r.get("status"),
        "logLen": len(log_text),
        "cappedAt16012": is_capped,
        "fulltextSource": source,
        "fulltextLen": len(text),
        "fulltext": text,
    }
    store[rid] = entry
    if is_capped:
        capped[rid] = entry

all_path = OUT_DIR / f"{TAG}_fulltext.json"
json.dump({"builtFrom": "Amendment A1 item A1.1 (D35)",
           "tag": TAG,
           "capChars": CAP,
           "runs": list(store.values())},
          open(all_path, "w"), ensure_ascii=False)
if TAG == "pilot":
    cap_path = OUT_DIR / "pilot_repair_capped.json"
    json.dump({"builtFrom": "Amendment A1 item A1.1 (D35); re-judge pending author approval (D38)",
               "capChars": CAP,
               "runs": list(capped.values())},
              open(cap_path, "w"), ensure_ascii=False)

still_capped = sum(1 for e in capped.values() if e["fulltextLen"] == CAP)
print(f"[{TAG}] runs captured: {len(store)}")
print(f"[{TAG}] runs at the 16012 cap: {len(capped)}")
if TAG == "pilot":
    print(f"  - recovered to longer full text from archive: {len(capped) - still_capped}")
    print(f"  - still at cap even in archive (genuine model output limit): {still_capped}")
print(f"granular archive longer than run log: {n_granular_longer} runs")
print(f"wrote {all_path.name}" + (" and pilot_repair_capped.json" if TAG == "pilot" else ""))
