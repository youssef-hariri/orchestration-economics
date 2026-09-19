#!/usr/bin/env python3
"""Verify claim-map.json: every source file exists and every quote (when it is
a verbatim file quote) appears in the referenced file.
Quotes that are audit-recorded source *summaries* (not verbatim) are reported
as 'summary' and checked only for file existence."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
cm = json.load(open(Path(__file__).parent / "claim-map.json"))

# index repo files by basename for resolving audit-relative paths
INDEX = {}
for p in ROOT.rglob("*"):
    if p.is_file() and ".git" not in p.parts:
        INDEX.setdefault(p.name, []).append(p)

def resolve(rel):
    f = ROOT / rel
    if f.exists():
        return f
    hits = INDEX.get(Path(rel).name, [])
    return hits[0] if hits else None

ok = miss_file = miss_quote = summary = 0
problems = []
for c in cm["claims"]:
    for s in c.get("sources", []):
        f = resolve(s["file"])
        q = s.get("quote")
        if f is None:
            miss_file += 1
            problems.append(f'{c["claim_id"]}: MISSING FILE {s["file"]}')
            continue
        s["resolved_path"] = str(f.relative_to(ROOT))
        if not q:
            summary += 1
            continue
        # verbatim check for decisions/bib quotes; audit quotes are summaries
        if c["type"] in ("decision", "citation"):
            txt = f.read_text(encoding="utf-8", errors="replace")
            import re
            if re.sub(r"\s+", " ", q)[:120] in re.sub(r"\s+", " ", txt):
                ok += 1
            else:
                miss_quote += 1
                problems.append(f'{c["claim_id"]}: QUOTE NOT FOUND in {s["file"]}')
        else:
            summary += 1

print(f'verbatim-verified: {ok}')
print(f'summary-quotes (file existence checked): {summary}')
print(f'missing files: {miss_file}')
print(f'quotes not found: {miss_quote}')
for p in problems[:20]:
    print("  " + p)
out = Path(__file__).parent / "claim-map.resolved.json"
out.write_text(json.dumps(cm, indent=1, ensure_ascii=False))
print(f'resolved map written: {out.name}')
sys.exit(1 if (miss_file or miss_quote) else 0)
