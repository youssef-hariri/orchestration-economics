---
name: research-semantic-map
description: >-
  Semantic claim-to-evidence mapping for research papers: verify that prose
  MEANS what the data says, not just that numbers match. Use when auditing a
  draft for interpretive accuracy — direction flips, stale values, causal
  misattribution, existence-of-analysis gaps — especially in AI-assisted
  research where drafts are edited over many sessions and prose drifts from
  the frozen data. Complements research-paper-rigor (numeric claim map): that
  skill proves every number traces to data; this one proves every risky
  sentence does. Covers the risky-claim taxonomy, full-quote extraction,
  provenance schema with exact source values, discrepancy classes, sweep
  order, and caption coverage.
---

# Research Semantic Map — Meaning-Level Claim Verification

Battle-tested on a multi-study LLM-economics paper where a numeric claim map
(33k datapoints, 0 failures) still missed two real defects: a stale pilot
number quoted as a final result, and a cost-direction inversion in the
introduction. **Value fidelity is necessary but not sufficient — numbers can
match their sources while the prose misstates what they mean.**

## When to use

- A draft exists and claims are being interpreted ("X beats Y", "the cause is
  Z", "we recommend W"), not just reported.
- The paper went through many edit rounds or multiple AI assistants — drift risk.
- Pre-submission audit, reviewer-response verification, or replication-package QA.

Pair with `research-paper-rigor`: build the numeric datapoint map first; this
map reuses its frozen sources and adds the meaning layer.

## The risky-claim taxonomy (what to extract)

Sweep the draft top to bottom (title → abstract → intro → methods → results →
discussion → implications → limitations → conclusion → appendices) and extract
every sentence that is:

1. **Comparison** — "X beats/ties/loses to Y", "A is n× B". *Check: sign and
   magnitude, both values.*
2. **Causal/attributional** — "the gap is execution-driven", "personas raise
   cost". *Check: does the data isolate that cause? Is the direction right?*
3. **Recommendation** — "firms should…", "default to…", "avoid…". *Check: does
   the recommendation follow from a result that survived replication gates?*
4. **Cost/economic** — dollar figures, ratios, percentages of cost/quality.
   *Check: frozen price vector version, base cell, rounding.*
5. **Percentage/ratio restatement** — "98% of quality at 23% of cost".
   *Check: recompute from the two underlying means, not from memory.*
6. **Existence-of-analysis** — "we tested…", "robustness checks confirm…".
   *Check: the analysis actually exists as a frozen artifact, not just prose.*
7. **Replication/transport claims** — "the effect generalizes", "the extremes
   replicate". *Check: the gate table, not the narrative.*

Skip: citations, definitions, pure method descriptions without quantities,
rhetorical framing.

## Schema (per claim)

```json
{
  "id": "SC-<section>-<NNN>",
  "section": "section/subsection as the reader sees it in the PDF",
  "paper_line": 1234,
  "full_quote": "the complete claim sentence, verbatim from the draft",
  "what_it_means": "one plain-language line: what it says AND what could make it wrong",
  "source": [
    {
      "file": "path to the FROZEN raw results file (never an audit/summary)",
      "location": "line range, JSON key path, or table row+column",
      "exact_values": "verbatim value(s) — BOTH sides for comparisons"
    }
  ],
  "code": "script that computed derived numbers; null if read directly",
  "audit": "verified | DISCREPANCY | unverifiable — with a one-line note"
}
```

Rules:
- **Full quotes, never paraphrase.** The quote is the anchor; truncating it
  breaks re-verification.
- **Both sides of a comparison.** "A beats B" requires both A's and B's values.
- **Frozen sources only.** Never seed from audit reports or earlier summaries —
  that circularity is how stale values survive.
- **Code reference when computed.** Percentages, ratios, and effect sizes must
  name the script (or the inline formula) that produced them.
- **No status/pass-fail workflow fields.** The map records evidence; a human or
  a verifier script judges. (Agents cannot self-certify review.)

## Captions are claims too

Every figure and table caption makes claims (values, verdicts, "PASS/FAIL",
"identical across panels"). Add a `captions` array: one entry per caption with
the same source fields plus `covered_by` pointing at the body-claim ID that
carries the same numbers — so a caption never needs independent maintenance.
When a figure is redrawn, its caption must be re-read, not assumed.

## Discrepancy classes (what the sweep is hunting)

| Class | Signature | Real example caught |
|---|---|---|
| **Stale value** | number traces to a pilot/earlier artifact, not the final locked data | "8% gap recovery" quoted from a pilot note; locked data gave −3% |
| **Direction flip** | prose says cost/quality moved one way; ledger says the other | intro said personas "raise cost"; persona cells were actually cheaper |
| **Attribution error** | cause assigned to the wrong stage/factor | "designers iterate more" when the token gap was execution, not design |
| **Existence gap** | analysis claimed but no frozen artifact/script produces it | per-family contrasts "surviving" from an obsolete composite convention |
| **Boundary overreach** | a descriptive/underpowered pattern stated as a finding | domain routing rules from 2–5-problem cells |
| **Replication laundering** | exploratory finding narrated as confirmed | marketing-domain exception that later failed its wave gate |

## Sweep procedure

1. **Read the entire draft** — do not sample. Risky claims hide in abstracts,
   conclusions, and implication sections, not only in results.
2. Extract claims in paper order; assign IDs by section.
3. For each claim, locate the frozen source and copy the exact values. If the
   value cannot be found, that is itself the finding (existence gap) — recompute
   from raw data with the project's fixed conventions and persist the artifact.
4. Check internal consistency: the same quantity stated in two sections must
   agree (abstract vs results vs conclusion vs executive summary).
5. Record every discrepancy with its class; fix the draft; update the map entry
   to reflect the fix (keep the discovery note — it is the audit trail).
6. After any draft edit round, re-verify all quotes verbatim against the new
   file and refresh line numbers. Rerun the numeric claim map too — the two
   maps must always point at the same draft version.

## Output artifacts

- `semantic-claims.json` — the map (human-friendly JSON, paper order).
- Optionally a one-page discrepancy log for the methods/AI-disclosure section:
  what was caught, class, fix. These episodes are themselves evidence for
  honest AI-assisted-research reporting.

## Failure modes to avoid

- **Sampling instead of sweeping.** Partial sweeps find nothing and create
  false confidence.
- **Normalizing quotes loosely.** Verbatim anchoring is what makes the map
  re-checkable by script.
- **Trusting audit files as sources.** They are derivatives; go to raw/frozen.
- **Marking claims "reviewed" by the agent that wrote them.** The map holds
  evidence; judgment belongs to the human or an independent verifier.
