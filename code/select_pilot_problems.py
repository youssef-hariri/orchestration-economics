#!/usr/bin/env python3
"""Pilot problem selection — N=11 from 30, deterministic seeded draw.

Based on PILOT-POWER-ANALYSIS.md: seed 20260802, random.Random(seed).sample(11)
from the 30 main problems; stratified by domain to ensure coverage.
Output frozen in config/pilot_problems.json.
"""

import json
import random
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
SEED = 20260802

p15 = json.load(open(ROOT / "data/problems/business_problems_15.json"))
d15 = json.load(open(ROOT / "data/problems/business_problems_domain_15.json"))
domain_map = json.load(open(ROOT / "data/problems/domain_map.json"))["map"]

problems = {**p15, **d15}
ids = sorted(problems.keys(), key=lambda k: int(k.rsplit("_", 1)[1]))
assert len(ids) == 30, f"expected 30 main problems, got {len(ids)}"

# Group by domain
domain_groups = {}
for pid in ids:
    dom = domain_map[pid]
    domain_groups.setdefault(dom, []).append(pid)

print(f"Domains: { {k: len(v) for k, v in domain_groups.items()} }")

rng = random.Random(SEED)

# Stratified: ensure at least 1 from each of 6 domains, then random fill to 11
# 6 domains × 1 = 6, remaining 5 random from all
draw = []
for dom, pids in domain_groups.items():
    draw.append(rng.choice(pids))

remaining = [p for p in ids if p not in draw]
draw.extend(rng.sample(remaining, 11 - len(draw)))

# Verify domain coverage
domains_in_draw = Counter(domain_map[p] for p in draw)
print(f"Domain coverage: {dict(domains_in_draw)}")

draw_sorted = sorted(draw, key=lambda k: int(k.rsplit("_", 1)[1]))
out = {
    "_rule": "PILOT-POWER-ANALYSIS: seed 20260802, stratified random sample of 11 from 30 problems (1+ per domain, remainder random)",
    "seed": SEED,
    "pilot_size_N": 11,
    "pilot_problem_ids": draw_sorted,
    "domains": {i: domain_map[i] for i in draw_sorted},
    "problems": {
        i: {
            "name": problems[i]["name"],
            "background_context": problems[i]["background_context"],
            "business_problem": problems[i]["business_problem"],
        }
        for i in draw_sorted
    },
}

dest = ROOT / "config/pilot_problems.json"
dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print(f"\nSelected {len(draw_sorted)} problems:")
for i in draw_sorted:
    print(f"  {i}  [{domain_map[i]}]  {problems[i]['name']}")
print(f"\nfrozen -> {dest}")
