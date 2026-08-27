#!/usr/bin/env bash
# run_pilot_sequence.sh — orchestrate the full pilot sequence after Phase A.
#
# Phase A (30 pipelines x 11 problems) is launched separately. This script:
#   1. Waits for Phase A generation to finish.
#   2. Judges Phase A outputs (all 330) -> pilot_phaseA_judgments.jsonl.
#   3. Selects the 2 F-T families (strongest Western by F-S-N novelty + Kimi).
#   4. Creates F-T-N / F-T-P pipelines for the selected families.
#   5. Runs Phase B (F-T pipelines x 11 problems).
#   6. Judges Phase B outputs -> pilot_phaseB_judgments.jsonl.
#
# Resumable: each step checks for existing outputs and skips if done.
# Run with: nohup bash code/run_pilot_sequence.sh > runs/logs/sequence.log 2>&1 &

set -euo pipefail
cd "$(dirname "$0")/.."   # research/orchestration-economics

PHASEA_LOG="runs/logs/pilot_phaseA_2026-08-03.json"
EXPECTED_A=330

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

# ---- Step 1: wait for Phase A generation ----
log "Waiting for Phase A generation to complete (expect ${EXPECTED_A} runs)..."
while true; do
  if [ -f "$PHASEA_LOG" ]; then
    n=$(node -e "const s=require('./${PHASEA_LOG}'); console.log(s.results.length)" 2>/dev/null || echo 0)
    finished=$(node -e "const s=require('./${PHASEA_LOG}'); console.log(s.finishedAtUtc?'yes':'no')" 2>/dev/null || echo no)
    if [ "$finished" = "yes" ]; then
      log "Phase A generation complete: ${n} runs."
      break
    fi
    log "  Phase A in progress: ${n}/${EXPECTED_A} runs recorded."
  fi
  sleep 30
done

# ---- Step 2: judge Phase A ----
if [ -f "runs/logs/pilot_phaseA_judgments.jsonl" ]; then
  log "Phase A judgments exist; judge.py is resumable, running to completion."
fi
log "Judging Phase A outputs..."
python3 code/judge_phaseA.py
log "Phase A judging done."

# ---- Step 3: select F-T families ----
log "Selecting F-T families from F-S-N novelty..."
python3 code/select_ft_families.py
log "Family selection done: $(cat config/selected_ft_families.json | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>console.log(JSON.parse(d).selected_families.join(', ')))")"

# ---- Step 4: create F-T pipelines ----
log "Creating F-T-N / F-T-P pipelines..."
node code/create_ft_pipelines.mjs
log "F-T pipeline creation done."

# ---- Step 5: run Phase B ----
log "Running Phase B (F-T pipelines x 11 problems)..."
node code/pilot_run_phaseB.mjs || log "Phase B generation finished with some non-completed runs (see log)."
log "Phase B generation done."

# ---- Step 6: judge Phase B ----
log "Judging Phase B outputs..."
python3 code/judge_phaseB.py
log "Phase B judging done."

log "PILOT SEQUENCE COMPLETE."
log "Phase A: runs/logs/pilot_phaseA_2026-08-03.json + pilot_phaseA_judgments.jsonl"
log "Phase B: runs/logs/pilot_phaseB_2026-08-03.json + pilot_phaseB_judgments.jsonl"
log "Selected F-T families: config/selected_ft_families.json"
