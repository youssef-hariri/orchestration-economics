#!/usr/bin/env python3
"""Select the 2 families for F-T-N/F-T-P per the pre-registered rule:
   'strongest Western frontier by F-S-N Novelty + Kimi V3'.

Reads Phase A judgments (pilot_phaseA_judgments.jsonl) + gen log, filters to
F-S-N solutions, computes mean Novelty per family, picks the strongest Western
family (gpt/claude/gemini), and adds Kimi. Writes selected_families.json.
"""
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
GEN_LOG = ROOT / "runs/logs/pilot_phaseA_2026-08-03.json"
JUDG = ROOT / "runs/logs/pilot_phaseA_judgments.jsonl"
OUT = ROOT / "config/selected_ft_families.json"

WESTERN = ["gpt", "claude", "gemini"]

gen = json.load(open(GEN_LOG))
# runId -> (cell, family)
meta = {}
for r in gen["results"]:
    if r.get("runId") is not None:
        meta[r["runId"]] = (r.get("cell"), r.get("family"))

# Accumulate Novelty scores per family for F-S-N
novelty = defaultdict(list)
with open(JUDG) as f:
    for line in f:
        if not line.strip():
            continue
        j = json.loads(line)
        if "error" in j:
            continue
        run_id = j.get("runId")
        if run_id not in meta:
            continue
        cell, family = meta[run_id]
        if cell != "F-S-N":
            continue
        scores = j.get("scores") or {}
        n = scores.get("Novelty")
        if isinstance(n, (int, float)):
            novelty[family].append(n)

print("F-S-N Novelty by family:")
means = {}
for fam in sorted(novelty):
    vals = novelty[fam]
    m = sum(vals) / len(vals)
    means[fam] = m
    print(f"  {fam:8s} n={len(vals):3d}  mean={m:.3f}")

# Strongest Western frontier by novelty
western_scores = {f: means[f] for f in WESTERN if f in means}
if not western_scores:
    raise SystemExit("No Western F-S-N novelty scores found")
best_western = max(western_scores, key=western_scores.get)

selected = sorted([best_western, "kimi"])
result = {
    "rule": "PREREGISTERED: strongest Western frontier by F-S-N Novelty + Kimi V3",
    "novelty_means": means,
    "best_western": best_western,
    "best_western_novelty": western_scores[best_western],
    "selected_families": selected,
}
with open(OUT, "w") as f:
    json.dump(result, f, indent=2)
print(f"\nBest Western frontier: {best_western} (novelty={western_scores[best_western]:.3f})")
print(f"Selected families for F-T: {selected}")
print(f"Saved to {OUT}")
