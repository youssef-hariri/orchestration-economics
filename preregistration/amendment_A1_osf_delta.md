# OSF Re-Registration Delta — Amendment A1

**Study:** The Economics of Orchestration (2×2×2 tier × structure × persona factorial)
**Delta date:** 2026-07-30
**Applies to:** the pre-registration document (protocol 01 template, preregistration_v1)
**Timing rule:** this delta is applied to the OSF registration BEFORE the first main-run generation call;
the original registration version remains preserved by OSF's versioning.
**Nature:** measurement-infrastructure correction discovered at the pilot stage (before any main-run data exist).
No hypothesis, design factor, cell, sample-size, or stopping-rule element is altered.

---

## Text to append to the OSF registration (verbatim)

### Amendment A1 (2026-07-30): pilot-stage measurement corrections

During qualitative diagnostics of the completed pilot (371 runs), two measurement-infrastructure
artifacts were identified and corrected before the main run. Pilot data are never pooled into
confirmatory inference (per the pre-registered pilot protocol); these corrections therefore concern
only how main-run data will be collected and scored.

**A1.1 — Full-text judging.**
Original registration: solutions scored by the judge panel as returned by the execution platform.
Amendment: solutions are scored from the complete archived final response (`export_run` archive,
uncapped), because the platform status endpoint was found to cap displayed responses at 16,000
characters; 35.0% of pilot solutions (confounded with team structure) reached that cap. Each run
logs whether the transport layer capped the text (`truncatedAtSource`) and the exact character length
presented to the judges (`fulltextLen`).

**A1.2 — Judge output integrity.**
Original registration: judge temperature 0, 3 judges × 3 verbatim prompt variants, 1–5 scores on five dimensions.
Amendment: judge maximum output tokens raised from 512 to 2,048 (the pilot showed 2.65% of dimension
scores missing because judge justifications overflowed the 512-token budget, concentrated in one judge
and one dimension); any judgment missing one or more of the five dimension scores is automatically
re-attempted up to two additional times; persistent failures are logged and audited, never silently dropped.
The judge models, prompt variants, temperature, blinding, and presentation order are unchanged.

**A1.3 — Audit fields.**
Every generation record logs concurrency level and truncation/length audit fields; every judgment
record logs the judge emission budget and harness version.

**A1.4 — Length sensitivity analysis (addition to the analysis plan).**
In addition to the pre-registered primary model
`quality ~ tier*structure*persona + (1|problem) + (1|family)`,
a pre-specified sensitivity analysis will report the primary tier×structure interaction adjusted for
log(output length), plus family-specific length–quality correlations. The primary confirmatory test
remains the unadjusted pre-registered model; the length-adjusted model is robustness-only.

**A1.5 — Optional pilot repair (conditional, separately approved).**
The 130 pilot solutions scored under the 16,000-character cap may be re-scored from their archived
full texts using the amended judging configuration, solely to produce an artifact-corrected pilot
table for the appendix. The original pilot judgments are retained as the historical record. This
repair consumes judging budget only and does not affect any confirmatory analysis.

**Unchanged:** hypotheses H1–H5/E1; 2×2×2 design; 8 cells; 5 model families and their pinned models;
30 problems; cultural persona pool and role mapping; judge panel composition and prompt variants;
blinding; sequential stopping rules; sample size (19 problems × 40 pipelines × 2–3 reps);
temperature and generation token budget; concurrency regime.

---

## Internal routing note (not for OSF)

- Evidence file: `results/QUALITATIVE-NOTES.md`
- Amendment text: `DeeWaanAI-Next/protocols/05-AMENDMENT-A1-PILOT-ARTIFACT-CORRECTIONS.md`
- Decision register entries: DESIGN-DECISIONS.md D35–D38
- Author sign-off checkboxes: §7 of the amendment document.
