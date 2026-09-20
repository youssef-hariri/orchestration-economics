#!/usr/bin/env python3
"""Two-way claim-map verifier (generic skeleton — adapt ROOT/paths).

DP direction : re-read each raw results file, navigate the DP's key path,
               value must equal (NaN-safe).
PM direction : each mention's dp_id must exist; its verbatim quote's numeric
               tokens must appear in the current draft file.
Exit 0 only when all checks pass. Never trusts audit reports or summaries.
"""
import json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # project root
MAP = ROOT / "paper" / "claim_map"                   # where the maps live
DRAFT = ROOT / "paper" / "P5_v15.6.tex"              # current draft

dps = {d["dp_id"]: d for d in json.load(open(MAP / "datapoints.json"))["datapoints"]}
pm = json.load(open(MAP / "paper-claims.json"))
tex = DRAFT.read_text(encoding="utf-8")

INDEX = {}
for p in ROOT.rglob("*"):
    if p.is_file() and ".git" not in p.parts:
        INDEX.setdefault(p.name, p)

fail = []

def navigate(obj, segments):
    for part in segments:
        obj = obj[part]
    return obj

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
            fail.append(f'{d["dp_id"]}: csv line not verbatim')
    else:
        try:
            key = str(f) + ":json"
            if key not in cache:
                cache[key] = json.load(open(f))
            v = navigate(cache[key], d.get("key_segments") or [])
            if v == d["value"] or (isinstance(v, float) and isinstance(d["value"], float)
                                   and math.isnan(v) and math.isnan(d["value"])):
                ok_dp += 1
            else:
                fail.append(f'{d["dp_id"]}: value mismatch at {d["key_path"]}')
        except Exception as e:
            fail.append(f'{d["dp_id"]}: path error {d["key_path"]} ({e})')

ok_pm = linked = curated = 0
for m in pm["mentions"]:
    ml = m.get("manual_link")
    if ml:
        curated += 1
        for f in ml.get("files", []):
            if not (ROOT / f).exists():
                fail.append(f'{m["mention_id"]}: curated doc missing {f}')
    if m.get("dp_id"):
        linked += 1
        if m["dp_id"] not in dps:
            fail.append(f'{m["mention_id"]}: dangling dp_id {m["dp_id"]}')
            continue
    q = m.get("verbatim_quote")
    if q:
        toks = re.findall(r"-?\d[\d,]*\.?\d*", q)
        if any(t.replace(",", "") in tex.replace(",", "") for t in toks if len(t) > 1):
            ok_pm += 1
        else:
            fail.append(f'{m["mention_id"]}: quote token not found in draft')

print(f"DP verbatim-verified : {ok_dp}/{len(dps)}")
print(f"PM quotes verified   : {ok_pm}")
print(f"PM linked to DP      : {linked}/{len(pm['mentions'])}")
print(f"PM curated links     : {curated}")
print(f"FAILURES             : {len(fail)}")
for x in fail[:20]:
    print("  " + x)
sys.exit(1 if fail else 0)
