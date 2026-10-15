#!/usr/bin/env python3
"""Generic frozen-prompt extractor for the research-paper-rigor method.

Purpose: reviewers and readers should never have to dig through experiment
code to find the exact prompts that produced the results. This script pulls
every frozen prompt out of source files into reader-facing
`config/prompts/*.md` files, plus a `MANIFEST.json` recording the exact code
location each prompt came from (provenance).

This is a GENERIC skeleton. Adapt the extraction blocks at the bottom to your
own code layout. Three source patterns are covered:

  1. JS/TS template or string constants   (e.g. ROLE_PROMPTS in a .mjs file)
  2. Python triple-quoted constants        (e.g. PROMPT = \"\"\"...\"\"\")
  3. Prompts already frozen as data        (JSONL / JSON files — copied verbatim)

Rules:
  - Extraction is verbatim. Never paraphrase a prompt into the .md file.
  - Every file gets a manifest entry: {file, extracted_from, note}.
  - Re-running must be idempotent (overwrite, same output).
  - If a pattern is not found, FAIL LOUDLY — a missing prompt means the code
    changed and the frozen set is no longer trustworthy.
"""
import json
import re
import sys
from pathlib import Path

# --- ADAPT THESE THREE -------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]   # project root (adjust depth)
OUT = ROOT / "config" / "prompts"
# -----------------------------------------------------------------------------

OUT.mkdir(parents=True, exist_ok=True)
manifest = []


def grab(text: str, pattern: str, flags=re.S) -> str:
    m = re.search(pattern, text, flags)
    if not m:
        sys.exit(f"FATAL: pattern not found (code changed?): {pattern[:60]}")
    return m.group(1)


def put(name: str, body: str, source: str, note: str) -> None:
    (OUT / name).write_text(body.strip() + "\n", encoding="utf-8")
    manifest.append({"file": f"config/prompts/{name}",
                     "extracted_from": source, "note": note})
    print("wrote", name)


# ============================================================================
# PATTERN 1 — JS/TS string constants.
# Example: extract `builder: "..."` entries from a ROLE_PROMPTS object in
# code/create_pipelines.mjs. Adapt the path, variable names, and roles.
# ============================================================================
# js = (ROOT / "code" / "create_pipelines.mjs").read_text()
# for role in ("builder", "critic", "refiner"):
#     body = grab(js, rf'{role}:\s*\n?\s*"((?:[^"\\]|\\.)*)"')
#     put(f"role_{role}.md", body.replace('\\"', '"'),
#         "code/create_pipelines.mjs ROLE_PROMPTS",
#         f"frozen {role} template; frozen at preregistration")

# ============================================================================
# PATTERN 2 — Python triple-quoted constants.
# Example: extract PROMPT = \"\"\"...\"\"\" from code/refine_run.py.
# ============================================================================
# py = (ROOT / "code" / "refine_run.py").read_text()
# body = grab(py, r'PROMPT = """(.+?)"""')
# put("refiner_prompt.md", body,
#     "code/refine_run.py PROMPT",
#     "frozen refiner prompt; {placeholders} substituted per item")

# ============================================================================
# PATTERN 3 — Prompts already frozen as data (JSONL/JSON). Copy verbatim so
# the prompts directory is a one-stop bundle.
# ============================================================================
# jl = ROOT / "evaluation" / "judge_prompts" / "judge_variations.jsonl"
# for line in jl.read_text().splitlines():
#     if not line.strip():
#         continue
#     v = json.loads(line)
#     put(f"judge_variant_{v['id']}.md", v["description"],
#         "evaluation/judge_prompts/judge_variations.jsonl",
#         "verbatim judge prompt variant, frozen as data")

if not manifest:
    sys.exit("No extraction blocks enabled — adapt the patterns above first.")

(OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
print(f"\n{len(manifest)} prompt files extracted -> {OUT.relative_to(ROOT)}/")
