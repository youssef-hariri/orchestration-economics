# Mapping Orchestration Economics — Artifact Index

This folder bundles everything produced by the claim-mapping methodology applied
to the orchestration-economics paper, for use in the upcoming paper about the
mapping method itself. All files are copies; originals remain in their project
locations.

## 1. `claim_map/` — the maps and their pipeline

| File | What it is |
|---|---|
| `datapoints.json` | **Numeric data map.** 33,022 data points (DPs), each linking a research quantity to its raw source file (path, line/field, exact value). |
| `claim-map.json` | Raw extraction of every numeric/verifiable mention in the paper draft. |
| `claim-map.resolved.json` | Each paper mention linked to its DP ID(s); output of the manual-links step. |
| `paper-claims.json` | Verbatim quotes from the draft with their locations (section → quote). |
| `semantic-claims.json` | **Semantic map v5.** 48 claims + 28 figure/table captions, checked for *meaning-level* fidelity (direction, scope, framing) against raw sources — catches errors the numeric map cannot see (e.g., stale values, direction flips). |
| `SEMANTIC-CLAIMS-MAP-DESIGN.md` | Design notes for the semantic map: schema choices, claim types, lessons learned (including the 2026-09-21 audit that motivated it). |

Pipeline (run order):
1. `build_claim_map.py` — extract mentions from the draft
2. `build_datapoints_map.py` — build/refresh the DP registry from raw result files
3. `apply_manual_links.py` — attach curated DP links
4. `verify_two_way.py` — two-way verification (every mention ↔ DP ↔ raw source)
5. `verify_claim_map.py` — auxiliary checks

Last full run: 33,022 DPs, 170 mentions, 155 quotes verified, 0 failures.

## 2. `skills/` — the transferable method

| Path | What it is |
|---|---|
| `research-paper-rigor/SKILL.md` | Numeric claim-map skill: frozen-data discipline, claim-to-evidence mapping, verification loop. |
| `research-paper-rigor/references/methodology.md` | Extended methodology notes for the rigor skill. |
| `research-paper-rigor/scripts/` | Reference implementations (`extract_frozen_prompts.py`, `verify_two_way.py`). |
| `research-semantic-map/SKILL.md` | Semantic claim-map skill: meaning-level verification (direction, scope, attribution, existence-of-analysis). |
| `research-paper-rigor.zip` / `.skill` | Packaged, shareable versions (installed successfully in Qoder/Qwen). |

## 3. `DESIGN-DECISIONS.md`

The D1–D60 decision log of the orchestration-economics project — the governance
backbone the maps rely on: every experiment/design decision with rationale and
date, so claims about *why* something was done are also traceable.

## Key lessons for the map paper

- Numeric maps verify *values*; semantic maps verify *meaning*. Both are needed —
  the 2026-09-21 audit found real errors (stale "8% gap recovery", persona-cost
  misframing) that passed numeric verification.
- Maps must be repointed and re-verified after every draft revision.
- AI assistants can misread the researcher's intent (H1 framing episode) —
  the map makes such drift detectable, but human audit remains the final gate.
