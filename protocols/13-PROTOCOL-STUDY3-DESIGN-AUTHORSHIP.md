# Protocol 13 — Study 3: Pipeline Design Authorship (Designer Tier × Executor Tier)

**Status: DRAFT — NOT REGISTERED. No generation, judging, or analysis call may be made under
this protocol until (a) author go-ahead, (b) OSF registration timestamped BEFORE first data
collection, (c) registration ID recorded here.**

**Lineage:** executes and completes the pre-registered-but-unexecuted arm A7 (D30, D31),
expanded from a single-designer policy arm to a Designer-Tier × Executor design.
A5/A6/A8 remain unexecuted and will be disclosed as such in the paper (v11).

---

## 1. Research question

Does the *quality of the pipeline design itself* — who authors the orchestration structure —
determine the output quality of a fixed cheap execution pool?

The factorial record (Study 1) held design authorship fixed (human-designed frozen
Builder→Critic→Refiner). A reviewer can attribute cheap-team inferiority to the human-designed
pipeline rather than to cheap-model execution. Study 3 removes that confound.

## 2. Design

**2 (designer tier) × 5 (family) factorial, executor fixed = family's pinned cheap sibling.**

| Arm | Designer | Executor | Construct |
|---|---|---|---|
| D-SELF | family's own cheap sibling (T per D27 precedent) | same cheap sibling | self-orchestration at the cheap end |
| D-FRONT | family's own frontier (pinned registry version) | cheap sibling | downward transfer of design capability |

- Designer receives: problem text (verbatim rendering rule, D32) + the frozen pipeline schema
  (DeeWaanAI `exportPipeline` format: steps, roles, system prompts, temperatures, maxTokens,
  optional if/while configs) + instruction to stay within the platform schema.
- Design output validated programmatically (schema parse + model availability check).
  Invalid designs: one repair retry with the validation error appended; second failure →
  design recorded as FAILED, problem falls back to… (decide before registration: exclude vs
  fixed-pipeline fallback; recommendation: exclude and disclose rate — no silent substitution).
- **Designer tokens are charged to arm cost** (D30 precedent: designer/probe/staffing tokens
  count). Cost reported per arm including design overhead.
- Executor runs the designed pipeline verbatim, model-homogeneous cheap sibling, temp per D27.

**Controls / comparators (no new runs — frozen records):**
- Fixed human-designed C-T-N and C-T-P (Study-1 frozen) — is any designed pipeline better
  than the human default?
- F-S-N (Study-1 frozen) — the standing frontier-solo benchmark.

## 3. Stimuli and sample

- Problems: the 19 confirmatory problems (11 pilot problems excluded, per Study-1 rule).
  Fresh_Case set reserved untouched for any future replication.
- Reps: 3 per arm per family per problem (D5 logic).
- Runs: 2 arms × 5 families × 19 problems × 3 reps = **570 executions** + ≤ 570 design calls.
- Judging: frozen panel (deepseek-chat, GLM-5.2, Llama-3.3-70B) × 3 verbatim variants,
  blinded, temp 0 — `judge_v2.py` unchanged. 570 × 9 = 5,130 judge calls.

## 4. Hypotheses (directions locked pre-registration)

- **H-D1 (primary, directional):** D-FRONT > D-SELF on the composite score.
  Ground: Study-2b refiner-identity result (universal/cross-family refiner beat within-family
  editors; pooled d = −0.348, p = 0.009) — capability transfers through authored structure.
- **H-D2:** designed pipelines (either arm) ≥ frozen human-designed C-T-N — i.e., the human
  default is not a binding ceiling. Two-sided.
- **H-D3 (economic):** D-FRONT remains cheaper per quality point than F-S-N after charging
  design tokens. Reported via T-EGR (D23 frozen price vector).

## 5. Gates (futility/feasibility only, D31 logic; never evidence)

- **G1 (feasibility):** schema-valid design rate ≥ 90% AND execution completion ≥ 90%,
  piloted on 4 problems (D32 deterministic draw rule, new seed recorded) per arm × 5 families.
- **G2 (extension):** pilot must NOT show D-FRONT < C-T-N with d < −0.30 in the negative
  direction (SESOI 0.30) — i.e., stop only on clear futility. Any other outcome → full run.
- Every executed arm is reported regardless of outcome (no file-drawer, D31).

## 6. Analysis plan (locked)

- Primary: LMM `composite ~ arm` with family random effect (single-vc fallback rule per D52
  disclosed-wrapper precedent declared in advance); Welch d + 5,000-resample bootstrap CIs
  (seed 42); Holm within the H-D1 family of tests; BH-FDR for dimension-level secondaries.
- Planned contrasts: D-FRONT vs D-SELF (H-D1); each arm vs frozen C-T-N and C-T-P (H-D2);
  each arm vs frozen F-S-N (descriptive benchmark).
- Economics: tokens × frozen price vector v2026-07-30 + designer tokens; T-EGR; Pareto
  position vs the frozen Study-1 frontier. Discount-window discipline per D21/Protocol-11 §8.
- Robustness: judge LOO, family LOO, mean-vs-median (D13 battery, reduced form).

## 7. Execution discipline

- New ledger `runs/logs/study3_ledger.json`, seed-42 interleaving, idempotent resume (D17/D34).
- Designer raw outputs stored unedited (`*.designer_raw.txt`, DATA-DICTIONARY convention).
- Execution inside UTC 14:00–00:00 window where provider discounts apply.
- Any deviation → stop, MANIFEST entry, amendment candidate (house rule).

## 8. Budget envelope (estimate, verify at registration)

~570 executions (cheap-tier tokens) + ~570 design calls (half frontier) + 5,130 judge calls.
Order of magnitude **≤ $40**. Pilot ≈ $5 inside the envelope.

## 9. Open decisions — RESOLVED 2026-08-28 (implemented in `code/study3_design_run.py`)

1. Invalid-design handling: **exclude-and-disclose after ONE repair retry**. The designer
   response is parsed as JSON; on parse/validation failure the designer is re-prompted once
   with the validation error echoed back. If the retry also fails, the task is marked
   `design_failed` in the ledger, excluded from analysis, and disclosed in the CONSORT-style
   flow. No fixed-pipeline fallback (a fallback would confound authorship with structure).
2. Design granularity: **fresh design per rep** (design × execution both vary; design
   variance becomes measurable rather than a hidden shared component). Cost accepted within
   the ≤ $40 envelope.
3. Designer/executor temperature: **provider-enforced defaults (D27 precedent)** —
   gpt omits `temperature` (uses `max_completion_tokens` + `reasoning_effort=low`); all
   other families use their API defaults. No pinned temperature, so results stay comparable
   to Studies 1–2 conditions.
