#!/bin/bash
# Self-driving Study 3 runner (author-approved 2026-08-29).
# Loops the resumable runner until the plan shows todo 0; all work is
# checkpointed, so any interruption (kill, network, credit) resumes cleanly.
cd "$(dirname "$0")" || exit 1
while true; do
    echo "=== chunk start $(date -u +%FT%TZ) ===" >> runs/logs/study3_driver.log
    out=$(env -u KIMI_API_KEY python3 -u code/study3_design_run.py --pilot 2>&1 | tee -a runs/logs/study3_full.log)
    plan=$(echo "$out" | grep "^Study 3 plan:" | tail -1)
    echo "=== chunk end   $(date -u +%FT%TZ) | $plan" >> runs/logs/study3_driver.log
    if echo "$plan" | grep -q "todo 0"; then
        echo "=== ALL DONE $(date -u +%FT%TZ) ===" >> runs/logs/study3_driver.log
        break
    fi
    sleep 20
done
