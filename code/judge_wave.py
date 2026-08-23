#!/usr/bin/env python3
"""Wave judging harness (Protocol 12, OSF jg49x; D47).

This is a thin, documented wrapper around the FROZEN Study-1 instrument
(code/judge_v2.py) — same 3 judges, same 3 verbatim D10 prompt variants,
same rubric, temperature 0, blinded, seed 20260731, A1.2 full-text +
A1.3 integrity. Nothing in judge_v2.py is modified.

Added responsibilities (wave-specific):
  1. Assemble the full-text store runs/fulltext/wave_fulltext.json from the
     per-run records in runs/raw/wave/ (one file per run, D34), mapping the
     runner's `finalResponse` field to judge_v2's expected `fulltext` key.
  2. Defensive reasoning-trace stripping (D48): MiniMax-M2.x thinking cannot
     be disabled and M3/Inkling/gpt-oss may emit reasoning; any residual
     <think>...</think> or <|channel|>analysis blocks are removed BEFORE judging
     (the platform's export_run already returns visible content only — Kimi-K3
     Study-1 archives verified trace-free — this is belt and braces; every
     stripped document is counted and disclosed).
  3. Delegate judging to judge_v2.py unchanged.

Usage:
  python3 code/judge_wave.py                 # build store, then judge
  python3 code/judge_wave.py --store-only    # only rebuild the store
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "runs" / "raw" / "wave"
STORE = ROOT / "runs" / "fulltext" / "wave_fulltext.json"
OUT = ROOT / "runs" / "logs" / "wave_judgments.jsonl"
JUDGE_V2 = ROOT / "code" / "judge_v2.py"

# Residual reasoning-trace patterns (defensive; platform export normally
# carries visible content only). Patterns assembled from parts so no literal
# tag-like sequence appears in the source (an earlier version lost its
# pattern to tooling that strips tag-shaped text — caught at store build:
# empty regex corrupted every doc; judging had not started).
_THINK_OPEN = "<" + "think" + ">"
_THINK_CLOSE = "<" + "/think" + ">"
THINK_RE = re.compile(re.escape(_THINK_OPEN) + r".*?" + re.escape(_THINK_CLOSE),
                      re.DOTALL | re.IGNORECASE)
CHANNEL_RE = re.compile(r"<\|channel\|>analysis<\|message\|>.*?<\|end\|>", re.DOTALL)


def strip_reasoning(text: str) -> tuple[str, int]:
    n = 0
    t, k = THINK_RE.subn("", text)
    n += k
    t, k = CHANNEL_RE.subn("", t)
    n += k
    return t.strip(), n


def build_store() -> None:
    entries, stripped_docs, skipped = [], 0, {"not_completed": 0, "empty": 0}
    for f in sorted(RAW_DIR.glob("*.json")):
        rec = json.loads(f.read_text())
        if rec.get("status") != "completed":
            skipped["not_completed"] += 1
            continue
        text = (rec.get("finalResponse") or "").strip()
        if not text:
            skipped["empty"] += 1
            continue
        clean, n_strip = strip_reasoning(text)
        if n_strip:
            stripped_docs += 1
        entries.append({
            "runId": rec.get("runId"),
            "problemId": rec["problemId"],
            "status": "completed",
            "fulltext": clean,
            "cell": rec.get("cell"), "family": rec.get("family"),
            "reasoning_blocks_stripped": n_strip,
        })
    if not entries:
        sys.exit("no completed wave runs found in runs/raw/wave/")
    missing_runid = [e["problemId"] for e in entries if e["runId"] is None]
    if missing_runid:
        sys.exit(f"{len(missing_runid)} completed runs lack a runId (e.g. {missing_runid[:3]}); "
                 "judge_v2 keys judgments by runId — fix before judging")
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps({
        "purpose": "wave full-text store for judge_v2.py (Protocol 12; A1.2)",
        "built_from": "runs/raw/wave/*.json finalResponse",
        "n_runs": len(entries),
        "docs_with_reasoning_stripped": stripped_docs,
        "runs": entries,
    }, ensure_ascii=False) + "\n")
    print(f"store: {STORE} ({len(entries)} runs; {stripped_docs} docs had residual reasoning stripped; "
          f"skipped: {skipped})")


def main() -> None:
    build_store()
    if "--store-only" in sys.argv:
        return
    cmd = [sys.executable, str(JUDGE_V2), "--store", str(STORE), "--out", str(OUT)]
    print("delegating to frozen judge_v2.py:", " ".join(cmd))
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
