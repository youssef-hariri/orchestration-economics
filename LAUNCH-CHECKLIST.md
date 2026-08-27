# Main-Run Launch Checklist (Amendment A1 ready)

**Status:** FROZEN AND WAITING for the discount window (author instruction 2026-07-30).
Nothing below may execute until the author says the window is open. Inshaa'Allah, when it opens,
execute in order — every command is pre-validated.

---

## 0. Before any token is spent (author + agent, ~10 min)

- [ ] Author signs Amendment A1 §7 (`DeeWaanAI-Next/protocols/05-AMENDMENT-A1-PILOT-ARTIFACT-CORRECTIONS.md`)
  - decision on A1.5 pilot re-judge: YES / NO / after main run
- [ ] Apply OSF delta (`preregistration/amendment_A1_osf_delta.md`) to the OSF registration; record the OSF link/version in Amendment §7
- [ ] Verify credits on all 5 generation providers + judging providers (DeepSeek, Together):
  - gpt-5.6-sol / gpt-5.6-luna (provider 15), claude-opus-5 / claude-haiku-4-5 (16),
    gemini-3.1-pro-preview / gemini-3.1-flash-lite (14), kimi (12; F-T still routed via Together id 18 per disclosed migration),
    qwen3.7-max / qwen3.7-plus (17)
  - known exhaustion history: Moonshot + Anthropic credits exhausted 2026-08-03 pilot (recharged); verify before launch
- [ ] Confirm D21 window alignment: execution inside 14:00–00:00 UTC (Qwen off-peak discount, avoids DeepSeek surge windows)
- [ ] Keep laptop awake (caffeinate / pmset) for the run duration

## 1. Generation — main run (1,900 runs, c=100)

```bash
cd "research/orchestration-economics"
node code/main_run.mjs --dry-run        # sanity: expect 1900 runs, 19 problems, 40 pipelines
node code/main_run.mjs                  # resumable; safe to kill/restart (D34 per-run files)
```

- Watch log for `TRUNC@SOURCE` lines — expected near-zero; if many appear, STOP and investigate (A1.1 guard).
- On completion verify: `runs/logs/main_run_ledger.json` → `truncatedAtSource` count, `completedNonEmpty`.
- Failure handling: re-run the same command (directory-scan resume); ≥4-failure pairs → exclude + note, same rule as pilot.

## 2. Build the main full-text store

```bash
python3 code/capture_fulltext.py --tag main   # (extend tag param if needed; reads main_run_ledger.json)
```
Expected: `runs/fulltext/main_fulltext.json` with `fulltextLen` > log length wherever applicable; 0 silently capped runs.

## 3. Judging — v2 harness (A1.2: max_tokens 2048, completeness gate)

```bash
python3 code/judge_v2.py --store runs/fulltext/main_fulltext.json --out runs/logs/main_judgments.jsonl
```
- 1,900 solutions × 3 judges × 3 variants = 17,100 calls; resumable; check final line for `INCOMPLETE` count (expect ~0).
- [If A1.5 approved] pilot repair first or after:
  `python3 code/judge_v2.py --store runs/fulltext/pilot_repair_capped.json --out runs/logs/pilot_repair_judgments.jsonl`
  (130 × 9 = 1,170 calls)

## 4. Interim-2 sequential analysis (Protocol 03)

- Reuse `code/sequential_analysis.py` on the main ledger + judgments (update input paths only — analysis plan UNCHANGED).
- Add the A1.4 length sensitivity: primary interaction + log(length)-adjusted version + per-family length–quality r.
- Apply stopping rules R1/R2/R3 mechanically; write `INTERIM2-DECISION.md`.

## 5. Post-run documentation

- MANIFEST entry with executed counts, failures, exclusions, credit spend.
- Paper appendix: pilot artifact story (QUALITATIVE-NOTES.md + Amendment A1) — this is Methods material, not a footnote.

---

## What is already done (do NOT redo)

| Artifact | State |
|---|---|
| 40-pipeline registry (full 8×5 factorial, incl. new F-T projects 49–54) | DONE |
| `code/main_run.mjs` dry-run: 1,900 runs plan validated | DONE |
| `code/judge_v2.py` compile-checked (NOT executed) | DONE |
| `runs/fulltext/pilot_fulltext.json` (371) + `pilot_repair_capped.json` (130) | DONE |
| Amendment A1 + OSF delta + D35–D38 + MANIFEST Entry 17 | DONE |

## Hard rules

1. No generation or judging before author confirms the discount window.
2. Pilot data stay frozen; pilot judgments are never overwritten (repair writes a separate file).
3. Any deviation during launch → stop, document in MANIFEST, treat as a new amendment candidate.
