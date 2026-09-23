#!/usr/bin/env python3
"""Extract every frozen prompt used in the experiments from code into
config/prompts/*.md (reader-facing, no code digging). Provenance: each file
records the exact code location it was extracted from. Artifact of the 2026-09-19 data audit."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "prompts"
OUT.mkdir(parents=True, exist_ok=True)
manifest = []

def grab(text, pattern, flags=re.S):
    m = re.search(pattern, text, flags)
    if not m:
        raise SystemExit(f"pattern not found: {pattern[:60]}")
    return m.group(1)

def put(name, body, source, note):
    (OUT / name).write_text(body.strip() + "\n", encoding="utf-8")
    manifest.append({"file": f"config/prompts/{name}", "extracted_from": source, "note": note})
    print("wrote", name)

# ---- Study 1 role prompts (create_pipelines.mjs) ----
js = (ROOT / "code" / "create_pipelines.mjs").read_text()
for role in ("builder", "critic", "refiner"):
    body = grab(js, rf'{role}:\s*\n?\s*"((?:[^"\\]|\\.)*)"')
    put(f"study1_role_{role}.md", body.replace('\\"', '"'),
        "code/create_pipelines.mjs ROLE_PROMPTS",
        f"DeeWaanAI canonical {role} template; persona cells prepend the persona text (persona_role_mapping_congruent)")
solo = grab(js, r'SOLO_NEUTRAL_PROMPT\s*=\s*\n?\s*"((?:[^"\\]|\\.)*)"')
put("study1_solo_neutral.md", solo,
    "code/create_pipelines.mjs SOLO_NEUTRAL_PROMPT",
    "task-only prompt for persona=none cells; frozen at preregistration")

# ---- Study 2 refiner prompt (refine_study2_run.py) ----
py = (ROOT / "code" / "refine_study2_run.py").read_text()
body = grab(py, r'PROMPT = """(.+?)"""')
put("study2_refiner_add_only.md", body,
    "code/refine_study2_run.py PROMPT (tag protocol09-v1)",
    "frozen universal add-only refiner; {problem_text}/{solution_text} substituted per pair")

# ---- Study 3 designer + repair prompts (study3_design_run.py) ----
py = (ROOT / "code" / "study3_design_run.py").read_text()
body = grab(py, r'DESIGN_PROMPT = """(.+?)"""')
put("study3_designer_prompt.md", body,
    "code/study3_design_run.py DESIGN_PROMPT (tag protocol13-v2)",
    "platform-verbatim DeeWaanAI auto-designer prompt (D56-corrected); {problem_text} substituted")
body = grab(py, r'REPAIR_PROMPT = """(.+?)"""')
put("study3_designer_repair_prompt.md", body,
    "code/study3_design_run.py REPAIR_PROMPT",
    "issued once after invalid structured designer output")

# ---- Judge prompts: already frozen as data; copy for one-stop bundle ----
jl = ROOT / "evaluation" / "judge_prompts" / "judge_variations.jsonl"
variants = [json.loads(l) for l in jl.read_text().splitlines() if l.strip()]
for v in variants:
    put(f"judge_variant_{v['id']}.md", v["description"],
        "evaluation/judge_prompts/judge_variations.jsonl",
        "verbatim judge prompt variant (D10); 3 judges x 3 variants per solution")

# ---- Personas: frozen data, copy alongside prompts ----
pers = json.load(open(ROOT / "data" / "personas" / "cultural_personas.json"))
for p in pers:
    put(f"persona_{p['id']}.md", p["description"],
        "data/personas/cultural_personas.json",
        f"verbatim persona (source: {p.get('source')}); assigned role: {p.get('assigned_role_congruent')}")

(OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
print(f"\n{len(manifest)} prompt files extracted -> config/prompts/")
