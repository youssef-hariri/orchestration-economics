# Methodology Reference — Claim-to-Evidence Research Papers

Detailed companion to SKILL.md. Load when implementing the method.

## The evidence chain

```
paper claim (verbatim sentence, line no.)
   → datapoint (DP-id: value, source file, key path, verbatim excerpt)
   → analysis script (committed, seeded)
   → raw frozen data (ledger / judgments / runs)
```

Nothing in the chain may be a derivative (audit reports, notebooks, memory).
If any link is missing, that is a defect to fix, not a caveat to ignore.

## Schemas

### datapoints.json
```json
{"schema": "datapoints-v1", "generated": "YYYY-MM-DD", "count": N,
 "datapoints": [
  {"dp_id": "DP-0001", "kind": "json-scalar|csv-row",
   "value": 0.2271,
   "source_file": "results/interim2_analysis.json",
   "key_path": "primary.H1.d", "key_segments": ["primary","H1","d"],
   "verbatim_excerpt": "{\"d\": -0.2271, ...}",
   "analysis_script": "code/analyze_main.py"}]}
```

### paper-claims.json
```json
{"schema": "paper-claims-v1", "paper": "paper/DRAFT.tex", "count": N,
 "mentions": [
  {"mention_id": "PM-S1_001", "claim_text": "H1 interaction ...",
   "paper_value": "d=-0.227, p=0.0145",
   "paper_line": 1150, "verbatim_quote": "The tier × structure ...",
   "dp_id": "DP-0181", "link_status": "linked|curated-document|curated-derived|curated-gap",
   "curation": {"kind": "...", "formula": "...", "files": [...]}}]}
```

## Linking heuristics that work
- Match numbers with rounding tolerance: round the DP value to the paper token's decimal places; also try ×100/÷100 for percent/proportion.
- Search the draft near the claim's expected location first (±150 lines), then whole document.
- JSON key paths containing dots/brackets ("C(tier)[T.F]", "p_below_4.0") must be stored as segment lists, never re-parsed from strings.
- Multi-value claims ("d=-0.227, CI=[...], p=...") link on any token; store all component DPs.
- Expect ~80% auto-link rate; the rest are structural claims (IDs, labels) → `document` links, derived ratios → `derived` links with formulas, and genuine gaps → fix per workflow D.

## Episodes worth emulating (from the orchestration-economics project)
1. **Silent defaults**: the AI capped auto-designed pipelines at 4 steps while the platform allows 7 — invisible because every output complied. Caught by auditing the instrument's rationale against platform source before data collection. Lesson: audit the rationale behind every parameter, not only parameters named in the protocol.
2. **Objective-level operationalization**: the registered H1 tested a pooled 8-cell interaction while the researcher's question was "cheap team+persona vs frontier solo". Both on the record; disclosed via a researcher-intent note. Lesson: audit how the AI operationalizes the question, not just outputs.
3. **Paper-only numbers**: per-family contrasts (d = −0.71, −1.42, −2.17) traced to no frozen file; frozen recomputation gave materially different values in 2 of 5 families and the paper was corrected (incl. cascading recovery percentages and summary-table rows). Lesson: claim-to-evidence tracing, human-audited, is the enforcement mechanism.

## Drafting conventions
- Versioned files: `P5_vX.Y.tex`; bump .1 for qualification/wording rounds, +0.1/+1 for data corrections. Compile 3× (references), confirm 0 undefined refs, diff against previous version and verify only intended regions changed.
- Correction cascades: when a number changes, grep for every downstream passage (abstract, summary tables, discussion, conclusion, exec summary) and reconcile all.
- Registries: keep a protocol table (number, role, status incl. "registered; never executed" and "superseded by") and an arm table; never rename arms mid-paper.

## AI-usage disclosure section (recommended contents)
- Which models did what (ideation/audit/execution vs. code generation), all frozen and logged.
- "No LLM made unsupervised decisions"; all protocols/decisions authored-reviewed-approved by the human.
- Oversight episodes as numbered, dated stories with lessons (see above).
- Pointer to the claim map as the enforcement artifact.
