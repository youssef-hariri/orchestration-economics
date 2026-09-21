# Semantic Claims Map — Design Seed (for the future claim-map methodology paper)

**Status:** idea captured 2026-09-21, to be ideated and designed later. Do NOT implement yet.

## The lesson that motivates it (Episode 4: semantic vs value fidelity)

The v1 claim map (datapoints.json + paper-claims.json, two-way verifier) enforces
**value fidelity**: every number printed in the paper must equal a frozen value at a
known key path in raw data. It passed 33,022/33,022 datapoints with 0 failures —
yet three substantive defects survived it (D63, 2026-09-21):

1. **Attribution error** — "cheap designers iterate more at the design stage
   (34.8M vs 24.3M tokens)". Both numbers matched frozen data exactly; the
   *label* was wrong (the field is design+execution; design-only is 0.6M vs 0.7M).
   The map checks "is this number real?", not "does this number mean what the
   sentence says?"
2. **Prose–table inconsistency** — decision-rule prose said "2–4× cheaper" while
   the adjacent table said 0.59×/0.24× (= 1.7–4.2×). Verbal ranges in prose are
   not value-registered, so nothing forced prose/table agreement.
3. **Phantom analysis** — "does not survive within-family conditioning" implied a
   formal analysis that was never run (the data is a descriptive, deliberately
   underpowered family×domain breakdown). No numbers → nothing for the map to
   bite on; and the map cannot detect a *missing* analysis.

Earlier episode of the same class: D61 (paper-only d values) was a value-fidelity
failure and the map caught it. D63 is the complementary failure class the map is
blind to: **right numbers, wrong story.**

## Proposal: Advanced Semantic Claims Map (v2 layer on top of v1)

Every comparative/interpretive sentence in the paper gets a semantic claim entry:

```json
{"claim_id": "SC-0001",
 "paper_ref": "paper/DRAFT.tex:1782 (Contrast B paragraph)",
 "verbatim_quote": "Cheap designers iterate more at the design stage ...",
 "claim_type": "attribution | direction | comparison | existence-of-analysis | scope | mechanism",
 "subject_dps": ["DP-XXXX", "DP-YYYY"],        // v1 datapoints the claim is ABOUT
 "predicate": {
   "type": "attribution",
   "asserted_source_field": "designer_usage.total_tokens",
   "actual_source_field": "designer_usage + steps[].usage"
 },
 "check": {
   "kind": "field-lineage | sign | ordering | file-exists-and-contains | manual",
   "script": "code/semantic_checks/sc_0001.py",  // executable where possible
   "expected": "...", "observed": "...", "status": "pass|fail|manual-review"
 }}
```

### Claim types and their checks
- **direction** ("X beats Y", "loses in finance") → sign check on referenced DP(s).
- **comparison / verbal range** ("2–4× cheaper") → recompute from component DPs;
  assert the prose range covers the computed interval; cross-check against the
  nearest table cells (prose–table consistency).
- **attribution** ("at the design stage", "driven by execution") → field-lineage
  check: the DP's key path / computation must match the asserted stage/cause;
  requires each DP to carry a `semantic_label` (what the field *means*, incl.
  composite fields that aggregate several stages).
- **existence-of-analysis** ("under conditioning", "controlling for", "after
  adjustment") → the named analysis must exist as a frozen script + results file
  containing the named terms; else fail as phantom-analysis.
- **scope** ("in all families", "uniformly", "most domains") → enumerate the DP
  set and verify the quantifier (all/most/none) holds.
- **mechanism** ("which explains why…") → links to the evidence element
  (qualitative code, robustness check) that supports the causal reading;
  always `manual-review` status, never auto-pass.

### Design principles (inherit from v1)
- Frozen raw data only; derivatives are never sources.
- Every check executable where possible; `manual-review` is an explicit status,
  not an absence of checking.
- Two-way: every semantic claim resolves; every flagged sentence has an entry.
- Same pipeline: build → apply manual links → verify (exit 0 gate).
- Episodes D61 (value fidelity) and D63 (semantic fidelity) are the paired
  teaching cases for the methodology paper.

### Open design questions (for the ideation session)
- How to auto-detect candidate semantic claims in LaTeX (cue phrases: "driven by",
  "beats", "dominant", "conditioning", "controlling for", "explains", "in all
  families") with acceptable precision/recall?
- Granularity: sentence vs clause?
- How to represent `semantic_label` on v1 datapoints without polluting frozen files
  (sidecar JSON keyed by dp_id)?
- Threshold rules for "verbal range covers computed interval" (rounding slack)?
- Integration with the AI-disclosure section: episodes auto-summarized from
  failed semantic checks?

## Why it matters for the methodology paper
v1 proves number-to-data traceability; v2 (semantic) proves story-to-data
alignment. Together they answer the reviewer's hardest question: "your numbers
are real, but is your prose true?" The paired D61/D63 episodes are the evidence
that both layers are needed and that neither alone is sufficient.
