---
name: research-paper-rigor
description: Rigorous, verifiable research-paper methodology built on claim-to-evidence mapping and frozen data. Use when working on an empirical research paper (any domain) that involves experiments, statistics, LLM-assisted workflows, or AI-generated analysis — especially when the user asks to verify claims, audit numbers against data, prepare a replication package, ensure reproducibility for reviewers, maintain a decision log, or write AI-usage disclosures. Covers: frozen data discipline, per-claim evidence mapping with verbatim quotes, self-verifying checkers, versioned paper drafts with diff-audits, decision logs, pre-registration hygiene, and business-reader framing of statistics.
---

# Research Paper Rigor — Claim-to-Evidence Methodology

Battle-tested on a multi-study LLM-economics paper (16 pre-registered protocols, 61 logged decisions, 33k verified datapoints). Goal: **every number printed in the paper must trace to frozen raw data — provably, by a script, not by memory.**

## Core principles (non-negotiable)

1. **Frozen raw data.** Raw run outputs, ledgers, and judgments are never edited after generation. Corrections happen in analysis code, never in data. Every artifact carries seeds, model versions, and timestamps.
2. **No paper-only numbers.** If a statistic appears in the draft, it must exist in a frozen results file (`.json`/`.csv`) produced by a committed script. A number that exists only in the paper is a defect — fix by recomputing + persisting + correcting the draft.
3. **Derivatives are never sources.** Audit reports, summaries, and spreadsheets are derivatives. The evidence chain is: `claim → frozen results file (verbatim excerpt + key path) → analysis script → raw data`. Never seed verification from an audit file.
4. **Every decision is logged.** A numbered decision log (D1, D2, …) records design/statistical decisions with date, rationale, and grounding. Entries are append-only; annotate, never rewrite history.
5. **Versioned drafts with diff-audits.** Each round of edits produces a new versioned file (`v15.5 → v15.6`). After edits, diff against the previous version and confirm only intended regions changed.
6. **Disclose AI involvement honestly.** Silent AI defaults are design decisions. Log oversight episodes (what the AI did, how it was caught, the lesson) in an AI-usage disclosure section.

## Workflow

### A. Set up (once per project)
- `DESIGN-DECISIONS.md` — numbered, dated entries: decision, rationale, academic grounding, implementing files.
- `results/` — frozen analysis outputs only (JSON/CSV).
- `code/` — every script that produced a results file, seeded and config-driven.
- Paper drafts versioned: `P5_vX.Y.tex`; compile after each round; keep all versions until final commit.

### B. Build the claim-to-evidence map (two files)
1. **`datapoints.json`** — canonical registry, built *data-first*: walk every frozen results file; each scalar value becomes `DP-NNNN` with `{value, source_file, key_path (as segments list), verbatim_excerpt, analysis_script}`. CSVs: one entry per row with the raw line as excerpt.
2. **`paper-claims.json`** — every quantitative claim in the draft: `{mention_id, claim_text, paper_value, paper_line, verbatim_quote (pulled from the draft file itself), dp_id}`. Repeated statements of one number share one DP-id. Link by value match with rounding tolerance (paper values are rounded; match DP value rounded to the paper token's decimals; handle %/proportion ×100).
3. Manually curate what auto-linking cannot resolve, tagged by kind: `document` (structural claims → protocol/config files), `derived` (ratios → formula + component DP-ids), `gap` (number not persisted anywhere → fix it).

### C. Verify with a two-way checker (exit 0 required)
`verify_two_way.py` must check, with zero trust in derivatives:
- **DP direction:** re-read each raw file, navigate the key path, value must equal the DP value (special-case NaN).
- **PM direction:** each mention's dp_id exists; its verbatim quote tokens appear in the current draft.
See `scripts/verify_two_way.py` (adapt paths; keep the checks).

### D. When verification catches a paper-only number
1. Write a small frozen script that recomputes it from raw data using the project's existing conventions (copy loaders verbatim; same seeds).
2. Persist output to `results/`; rerun the map; link the claim.
3. If the recomputed value differs materially from the draft: correct the draft, trace the cascade (every downstream passage that used the old number), record the episode in the decision log, and add it to the AI-disclosure/audit-trail section.
4. Never keep the unreproducible number.

### E. Sweep discipline
- Sweep section by section; verify every statistic against the map before trusting a sentence.
- Watch for: stale counts after scope changes ("twelve protocols" → sixteen), claims contradicted by corrected data elsewhere, table rows inconsistent with their own section text, "registered/executed" status errors in registries.
- Cross-references must point at sections that actually contain the claimed content — grep the target label.

### F. Business-reader framing
Pair every statistic with scale-free terms: quality as % of baseline, cost as % of baseline, effect sizes converted to scale points (d × pooled SD ÷ baseline mean). Each results subsection ends with a concrete, quantified "Strategic Implication" — no vague robustness claims.

## Reference
For the full method narrative, episode examples (silent 4-step cap, objective-level operationalization, unreproducible numbers caught by the map), and JSON schemas, read `references/methodology.md`.

## Scripts
- `scripts/verify_two_way.py` — generic two-way verifier skeleton (adapt `ROOT`, paths).
- `scripts/extract_frozen_prompts.py` — extract prompts from code into `config/prompts/` with a provenance manifest (for LLM-experiment papers).
