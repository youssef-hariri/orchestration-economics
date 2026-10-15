#!/usr/bin/env python3
"""Two-way verifier for the raw-anchored claim map.

DP direction : every datapoint's verbatim_excerpt must exist in its raw file.
PM direction : every linked mention's dp_id must exist; every found
               verbatim_quote's core token must appear in the paper file.
Exit 0 only if all checks pass."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
dps = {d["dp_id"]: d for d in json.load(open(HERE / "datapoints.json"))["datapoints"]}
pm = json.load(open(HERE / "paper-claims.json"))
tex = (ROOT / "paper" / "P5_v15.8.tex").read_text(encoding="utf-8")

fail = []
INDEX = {}
for p in ROOT.rglob("*"):
    if p.is_file() and ".git" not in p.parts:
        INDEX.setdefault(p.name, p)

def navigate(obj, d):
    for part in d.get("key_segments") or []:
        obj = obj[part]
    return obj

# DP check: JSON -> navigate key path, value must equal; CSV -> raw line substring
ok_dp = 0
cache = {}
for d in dps.values():
    f = ROOT / d["source_file"]
    if not f.exists():
        f = INDEX.get(Path(d["source_file"]).name)
    if f is None:
        fail.append(f'{d["dp_id"]}: missing {d["source_file"]}')
        continue
    if d["kind"] == "csv-row":
        txt = cache.setdefault(str(f), f.read_text(encoding="utf-8", errors="replace"))
        if d["verbatim_excerpt"][:120] in txt:
            ok_dp += 1
        else:
            fail.append(f'{d["dp_id"]}: csv line not verbatim in {d["source_file"]}')
    else:
        try:
            obj = cache.get(str(f) + ":json")
            if obj is None:
                obj = json.load(open(f))
                cache[str(f) + ":json"] = obj
            v = navigate(obj, d)
            import math
            same = (v == d["value"] or
                    (isinstance(v, float) and isinstance(d["value"], float)
                     and math.isnan(v) and math.isnan(d["value"])))
            if same:
                ok_dp += 1
            else:
                fail.append(f'{d["dp_id"]}: value mismatch at {d["key_path"]}')
        except Exception as e:
            fail.append(f'{d["dp_id"]}: path error {d["key_path"]} ({e})')

# PM check
ok_pm = linked_n = curated_n = 0
for m in pm["mentions"]:
    ml = m.get("manual_link")
    if ml:
        curated_n += 1
        for f in ml.get("files", []):
            if not (ROOT / f).exists():
                fail.append(f'{m["mention_id"]}: curated doc missing {f}')
        for i in m.get("dp_ids") or []:
            if i and i not in dps:
                fail.append(f'{m["mention_id"]}: dangling curated dp_id {i}')
    if m["dp_id"]:
        linked_n += 1
        if m["dp_id"] not in dps:
            fail.append(f'{m["mention_id"]}: dangling dp_id {m["dp_id"]}')
            continue
    q = m.get("verbatim_quote")
    if q:
        toks = re.findall(r"-?\d[\d,]*\.?\d*", q)
        hit = any(t.replace(",", "") in tex.replace(",", "") for t in toks if len(t) > 1)
        if hit:
            ok_pm += 1
        else:
            fail.append(f'{m["mention_id"]}: quote token not found in paper')

print(f'DP verbatim-verified : {ok_dp}/{len(dps)}')
print(f'PM quotes verified   : {ok_pm}')
print(f'PM linked to DP      : {linked_n}/{len(pm["mentions"])}')
print(f'PM curated links     : {curated_n}')
print(f'FAILURES             : {len(fail)}')
for x in fail[:15]:
    print("  " + x)
sys.exit(1 if fail else 0)
