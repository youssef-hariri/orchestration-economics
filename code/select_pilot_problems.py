#!/usr/bin/env python3
"""D32 pilot problem selection — deterministic seeded draw.

Rule (pre-registered in DESIGN-DECISIONS.md D32.2): seed 20260731,
random.Random(seed).sample(4) from the 30 main problems sorted by natural
numeric ID order; rejection-resample until the 4 problems span 4 distinct
domains per domain_map.json (coverage only — original-15 domain tags are
operational pending author confirmation). Output frozen in
config/pilot_problems.json.
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20260731

p15 = json.load(open(ROOT / "data/problems/business_problems_15.json"))
d15 = json.load(open(ROOT / "data/problems/business_problems_domain_15.json"))
domain_map = json.load(open(ROOT / "data/problems/domain_map.json"))["map"]

problems = {**p15, **d15}
ids = sorted(problems.keys(), key=lambda k: int(k.rsplit("_", 1)[1]))
assert len(ids) == 30, f"expected 30 main problems, got {len(ids)}"

rng = random.Random(SEED)
attempt = 0
while True:
    attempt += 1
    draw = rng.sample(ids, 4)
    if len({domain_map[i] for i in draw}) == 4:
        break

draw_sorted = sorted(draw, key=lambda k: int(k.rsplit("_", 1)[1]))
out = {
    "_rule": "D32.2: seed 20260731, random.Random(seed).sample(ids_sorted, 4), rejection-resampled until 4 distinct domains; attempt count recorded",
    "seed": SEED,
    "attempts": attempt,
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
print(f"attempts={attempt}")
for i in draw_sorted:
    print(f"{i}  [{domain_map[i]}]  {problems[i]['name']}")
print(f"frozen -> {dest}")
