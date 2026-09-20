---
name: research-paper-rigor
description: >-
  Rigorous, verifiable research-paper methodology built on claim-to-evidence
  mapping and frozen data. Use when working on an empirical research paper
  (any domain) that involves experiments, statistics, LLM-assisted workflows,
  or AI-generated analysis, especially when the user asks to verify claims,
  audit numbers against data, prepare a replication package, ensure
  reproducibility for reviewers, maintain a decision log, or write AI-usage
  disclosures. Covers frozen data discipline, per-claim evidence mapping with
  verbatim quotes, self-verifying checkers, versioned paper drafts with
  diff-audits, decision logs, pre-registration hygiene, and business-reader
  framing of statistics. Single-file standalone edition.
---

# Research Paper Rigor — Claim-to-Evidence Methodology (standalone edition)

Battle-tested on a multi-study LLM-economics paper (16 pre-registered protocols, 61 logged decisions, 33k verified datapoints). Goal: **every number printed in the paper must trace to frozen raw data — provably, by a script, not by memory.**

## Core principles (non-negotiable)

1. **Frozen raw data.** Raw run outputs, ledgers, and judgments are never edited after generation. Corrections happen in analysis code, never in data. Every artifact carries seeds, model versions, and timestamps.
2. **No paper-only numbers.** If a statistic appears in the draft, it must exist in a frozen results file (`.json`/`.csv`) produced by a committed script. A number that exists only in the paper is a defect — fix by recomputing + persisting + correcting the draft.
3. **Derivatives are never sources.** Audit reports, summaries, and spreadsheets are derivatives. The evidence chain is: `claim → frozen results file (verbatim excerpt + key path) → analysis script → raw data`. Never seed verification from an audit file.
4. **Every decision is logged.** A numbered decision log (D1, D2, …) records design/statistical decisions with date, rationale, and grounding. Entries are append-only; annotate, never rewrite history.
5. **Versioned drafts with diff-audits.** Each round of edits produces a new versioned file (`v15.5 → v15.6`). After edits, diff against the previous version and confirm only intended regions changed.
6. **Disclose AI involvement honestly.** Silent AI defaults are design decisions. Log oversight episodes (what the AI did, how it was caught, the lesson) in an AI-usage disclosure section.

## The evidence chain

```
paper claim (verbatim sentence, line no.)
   → datapoint (DP-id: value, source file, key path, verbatim excerpt)
   → analysis script (committed, seeded)
   → raw frozen data (ledger / judgments / runs)
```

Nothing in the chain may be a derivative (audit reports, notebooks, memory).
If any link is missing, that is a defect to fix, not a caveat to ignore.

## Workflow

### A. Set up (once per project)
- `DESIGN-DECISIONS.md` — numbered, dated entries: decision, rationale, academic grounding, implementing files.
- `results/` — frozen analysis outputs only (JSON/CSV).
- `code/` — every script that produced a results file, seeded and config-driven.
- Paper drafts versioned: `P5_vX.Y.tex`; compile after each round; keep all versions until final commit.

### B. Build the claim-to-evidence map (two files)

**`datapoints.json`** — canonical registry, built *data-first*: walk every frozen results file; each scalar value becomes `DP-NNNN`. CSVs: one entry per row with the raw line as excerpt. Schema:

```json
{"schema": "datapoints-v1", "generated": "YYYY-MM-DD", "count": 0,
 "datapoints": [
  {"dp_id": "DP-0001", "kind": "json-scalar|csv-row",
   "value": 0.2271,
   "source_file": "results/interim2_analysis.json",
   "key_path": "primary.H1.d", "key_segments": ["primary", "H1", "d"],
   "verbatim_excerpt": "{\"d\": -0.2271, ...}",
   "analysis_script": "code/analyze_main.py"}]}
```

**`paper-claims.json`** — every quantitative claim in the draft. Repeated statements of one number share one DP-id. Schema:

```json
{"schema": "paper-claims-v1", "paper": "paper/DRAFT.tex", "count": 0,
 "mentions": [
  {"mention_id": "PM-S1_001", "claim_text": "H1 interaction ...",
   "paper_value": "d=-0.227, p=0.0145",
   "paper_line": 1150, "verbatim_quote": "The tier × structure ...",
   "dp_id": "DP-0181",
   "link_status": "linked|curated-document|curated-derived|curated-gap",
   "curation": {"kind": "...", "formula": "...", "files": ["..."]}}]}
```

Link by value match with rounding tolerance (paper values are rounded; match DP value rounded to the paper token's decimals; handle %/proportion ×100). Manually curate what auto-linking cannot resolve, tagged by kind: `document` (structural claims → protocol/config files), `derived` (ratios → formula + component DP-ids), `gap` (number not persisted anywhere → fix it).

### C. Verify with a two-way checker (exit 0 required)
The verifier must check, with zero trust in derivatives:
- **DP direction:** re-read each raw file, navigate the key path, value must equal the DP value (special-case NaN).
- **PM direction:** each mention's dp_id exists; its verbatim quote tokens appear in the current draft.

A ready-to-adapt skeleton is included at the end of this file ("Script 1").

### D. When verification catches a paper-only number
1. Write a small frozen script that recomputes it from raw data using the project's existing conventions (copy loaders verbatim; same seeds).
2. Persist output to `results/`; rerun the map; link the claim.
3. If the recomputed value differs materially from the draft: correct the draft, trace the cascade (every downstream passage that used the old number — abstract, summary tables, discussion, conclusion, exec summary), record the episode in the decision log, and add it to the AI-disclosure/audit-trail section.
4. Never keep the unreproducible number.

### E. Sweep discipline
- Sweep section by section; verify every statistic against the map before trusting a sentence.
- Watch for: stale counts after scope changes ("twelve protocols" → sixteen), claims contradicted by corrected data elsewhere, table rows inconsistent with their own section text, "registered/executed" status errors in registries.
- Cross-references must point at sections that actually contain the claimed content — grep the target label.

### F. Business-reader framing
Pair every statistic with scale-free terms: quality as % of baseline, cost as % of baseline, effect sizes converted to scale points (d × pooled SD ÷ baseline mean). Each results subsection ends with a concrete, quantified "Strategic Implication" — no vague robustness claims.

## Linking heuristics that work
- Match numbers with rounding tolerance: round the DP value to the paper token's decimal places; also try ×100/÷100 for percent/proportion.
- Search the draft near the claim's expected location first (±150 lines), then whole document.
- JSON key paths containing dots/brackets ("C(tier)[T.F]", "p_below_4.0") must be stored as segment lists, never re-parsed from strings.
- Multi-value claims ("d=-0.227, CI=[...], p=...") link on any token; store all component DPs.
- Expect ~80% auto-link rate; the rest are structural claims (IDs, labels) → `document` links, derived ratios → `derived` links with formulas, and genuine gaps → fix per workflow D.

## Drafting conventions
- Versioned files: `P5_vX.Y.tex`; bump .1 for qualification/wording rounds, +0.1/+1 for data corrections. Compile 3× (references), confirm 0 undefined refs, diff against previous version and verify only intended regions changed.
- Registries: keep a protocol table (number, role, status incl. "registered; never executed" and "superseded by") and an arm table; never rename arms mid-paper.

## AI-usage disclosure section (recommended contents)
- Which models did what (ideation/audit/execution vs. code generation), all frozen and logged.
- "No LLM made unsupervised decisions"; all protocols/decisions authored-reviewed-approved by the human.
- Oversight episodes as numbered, dated stories with lessons.
- Pointer to the claim map as the enforcement artifact.

## Episodes worth emulating (real cases from the origin project)
1. **Silent defaults**: the AI capped auto-designed pipelines at 4 steps while the platform allows 7 — invisible because every output complied. Caught by auditing the instrument's rationale against platform source before data collection. Lesson: audit the rationale behind every parameter, not only parameters named in the protocol.
2. **Objective-level operationalization**: the registered H1 tested a pooled 8-cell interaction while the researcher's question was "cheap team+persona vs frontier solo". Both on the record; disclosed via a researcher-intent note. Lesson: audit how the AI operationalizes the question, not just outputs.
3. **Paper-only numbers**: per-family contrasts (d = −0.71, −1.42, −2.17) traced to no frozen file; frozen recomputation gave materially different values in 2 of 5 families and the paper was corrected (incl. cascading recovery percentages and summary-table rows). Lesson: claim-to-evidence tracing, human-audited, is the enforcement mechanism.

---

## Script 1 — `verify_two_way.py` (adapt ROOT/paths, keep the checks)

```python
#!/usr/bin/env python3
"""Two-way claim-map verifier. Exit 0 = every datapoint re-verified against
raw data AND every paper claim resolves. ADAPT the paths at the top."""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]        # project root
MAP = ROOT / "paper" / "claim_map"
DRAFT = ROOT / "paper" / "P5_vX.Y.tex"            # current draft

dp = json.loads((MAP / "datapoints.json").read_text())
pm = json.loads((MAP / "paper-claims.json").read_text())
draft = DRAFT.read_text()
fails = []

def get_by_segments(obj, segs):
    for s in segs:
        if isinstance(obj, list):
            obj = obj[int(s)]
        else:
            obj = obj[s]
    return obj

# Direction 1: datapoints re-verified against raw frozen files
for d in dp["datapoints"]:
    src = ROOT / d["source_file"]
    if not src.exists():
        fails.append((d["dp_id"], "missing source " + d["source_file"]))
        continue
    if d["kind"] == "json-scalar":
        data = json.loads(src.read_text())
        try:
            v = get_by_segments(data, d["key_segments"])
        except Exception:
            fails.append((d["dp_id"], "key path not found"))
            continue
        a, b = float(v), float(d["value"])
        if math.isnan(a) and math.isnan(b):
            continue
        if abs(a - b) > 1e-9:
            fails.append((d["dp_id"], f"value mismatch raw={a} map={b}"))
    elif d["kind"] == "csv-row":
        if d["verbatim_excerpt"].strip() not in src.read_text():
            fails.append((d["dp_id"], "csv row not found verbatim"))

# Direction 2: paper claims resolve to DPs and appear in the draft
ids = {d["dp_id"] for d in dp["datapoints"]}
for m in pm["mentions"]:
    if m.get("dp_id") and m["dp_id"] not in ids:
        fails.append((m["mention_id"], "dp_id missing: " + m["dp_id"]))
    q = m.get("verbatim_quote", "")
    if q and q not in draft:
        fails.append((m["mention_id"], "verbatim quote not in draft"))

if fails:
    for f in fails:
        print("FAIL", *f)
    sys.exit(1)
print(f"OK: {dp['count']} datapoints verified, {pm['count']} mentions resolved")
```

## Script 2 — `extract_frozen_prompts.py` (LLM-experiment papers; adapt patterns)

Purpose: reviewers should never dig through code to find the exact prompts that produced results. Extract every frozen prompt into `config/prompts/*.md` with a `MANIFEST.json` recording provenance. Three source patterns: JS/TS string constants, Python triple-quoted constants, JSONL/JSON prompt data. Rules: verbatim extraction only; fail loudly if a pattern is not found (code changed → frozen set untrustworthy); idempotent re-runs.

```python
#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]        # adapt depth
OUT = ROOT / "config" / "prompts"
OUT.mkdir(parents=True, exist_ok=True)
manifest = []

def grab(text, pattern, flags=re.S):
    m = re.search(pattern, text, flags)
    if not m:
        sys.exit(f"FATAL: pattern not found (code changed?): {pattern[:60]}")
    return m.group(1)

def put(name, body, source, note):
    (OUT / name).write_text(body.strip() + "\n", encoding="utf-8")
    manifest.append({"file": f"config/prompts/{name}",
                     "extracted_from": source, "note": note})
    print("wrote", name)

# PATTERN 1 — JS/TS: extract `builder: "..."` from a ROLE_PROMPTS object
# js = (ROOT / "code" / "create_pipelines.mjs").read_text()
# body = grab(js, r'builder:\s*\n?\s*"((?:[^"\\]|\\.)*)"')
# put("role_builder.md", body.replace('\\"', '"'),
#     "code/create_pipelines.mjs ROLE_PROMPTS", "frozen at preregistration")

# PATTERN 2 — Python: extract PROMPT = \"\"\"...\"\"\"
# py = (ROOT / "code" / "refine_run.py").read_text()
# put("refiner_prompt.md", grab(py, r'PROMPT = """(.+?)"""'),
#     "code/refine_run.py PROMPT", "{placeholders} substituted per item")

# PATTERN 3 — JSONL/JSON prompt data: copy verbatim for one-stop bundle
# for line in (ROOT / "evaluation/judge_prompts/judge_variations.jsonl").read_text().splitlines():
#     if line.strip():
#         v = json.loads(line)
#         put(f"judge_variant_{v['id']}.md", v["description"],
#             "evaluation/judge_prompts/judge_variations.jsonl", "verbatim variant")

if not manifest:
    sys.exit("No extraction blocks enabled — adapt the patterns above first.")
(OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
print(f"{len(manifest)} prompt files extracted")
```
