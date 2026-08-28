#!/usr/bin/env python3
"""OSF registration for Study 3 (Protocol 13, D55).

Registers the 2x5 design-authorship study (designer tier x family, executor fixed
= cheap sibling) as its OWN Open-Ended Registration, branched from the existing
project node (8pwej), with a separate state file so prior memorializations are
never touched. Reads OSF_TOKEN from ./.env. Steps run by subcommand, idempotent
via state. Adapted from osf_register_study2b.py (same API mechanics, incl. the
2026-08-22 execution-log note: no uploader attachments on the draft; the node
storage, incl. the uploaded Protocol 13 file, freezes into the archive).
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.osf.io/v2"
SCHEMA_ID = "5df83f7dd28338001ac0ab0d"  # Open-Ended Registration
STATE = ROOT / "preregistration/osf_submission/.osf_state_study3.json"
PROTOCOL = ROOT / "protocols" / "13-PROTOCOL-STUDY3-DESIGN-AUTHORSHIP.md"
PARENT_NODE = "8pwej"  # 'The Economics of Orchestration' project node

SUMMARY = """Pre-registration of Study 3 (Protocol 13): a 2x5 factorial test of
pipeline DESIGN AUTHORSHIP in 'The Economics of Orchestration'. Research
question: does the quality of the orchestration design itself — who authors it —
determine output quality when the execution pool is held fixed at cheap models?
Arm D-SELF: each family's cheap sibling designs AND executes its own pipeline
(gpt-5.6-luna, claude-haiku-4-5-20251001, gemini flash-lite, kimi-k2.6,
qwen3.7-plus). Arm D-FRONT: the family's frontier model designs; the cheap
sibling executes (gpt-5.6-sol, opus-5, gemini pro-preview, kimi-k3,
qwen3.7-max). Designer output = a pipeline JSON (1-4 named steps with
role/systemPrompt), schema-validated; invalid designs get ONE repair retry,
then are excluded and disclosed (no fixed-pipeline fallback). Fresh design per
repetition. Sampling parameters = provider-enforced defaults (D27 precedent).
Sample: the frozen 19-problem confirmatory bank (D32 rendering rule:
background_context + business_problem, verbatim) x 3 reps x 2 arms x 5 families
= 570 generations; pilot of 40 on the frozen D32 draw (Business_Problem_4/8/16/
19) precedes the full run. Gates: G1 feasibility (>=90% schema-valid designs
AND >=90% completion per family) else family reported as infeasible and
disclosed; G2 stop-rule only if D-FRONT underperforms the frozen human-designed
cheap-team-novelty baseline (C-T-N) by d < -0.30 (design authorship actively
harmful). Judging: frozen blind three-judge panel (deepseek-chat, GLM-5.2,
Llama-3.3-70B) x 3 verbatim variants, judge_v2 pipeline unchanged
(judge_v2-compatible store). Primary contrasts: D-FRONT vs D-SELF (design
authorship effect, paired within family/problem, Holm across families);
D-SELF/D-FRONT vs frozen C-T-N baseline (does model-authored design beat the
human-designed Builder->Critic->Refiner?). Designer tokens count toward arm
cost (D30 precedent); T-EGR cost-effectiveness reported per arm including
design overhead. Scheduling: DeepSeek judging only in off-peak windows (weekend
= off-peak all day Beijing time); qwen generation gated to UTC 14:00-00:00.
Budget <= $40 (pilot ~ $5). This registration timestamp PRECEDES all Study-3
data collection. Lineage: executes and completes pre-registered-but-unexecuted
arm A7 (D30/D31). Decision trail: D55 (DESIGN-DECISIONS.md); MANIFEST Entry 69.
Runner: code/study3_design_run.py (append-only ledger, resumable)."""


def token():
    for line in open(ROOT / ".env"):
        if line.startswith("OSF_TOKEN="):
            return line.split("=", 1)[1].strip()
    sys.exit("no OSF_TOKEN in .env")


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token()}")
    req.add_header("Content-Type", "application/json")
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:600]}")
        raise


def save_state(**kw):
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    st.update(kw)
    STATE.write_text(json.dumps(st, indent=2))
    return st


def load_state():
    return json.loads(STATE.read_text())


def cmd_draft():
    d = call("POST", f"{API}/draft_registrations/", {
        "data": {"type": "draft_registrations",
                 "attributes": {"registration_supplement": "Open-Ended Registration"},
                 "relationships": {
                     "provider": {"data": {"type": "registration-providers", "id": "osf"}},
                     "registration_schema": {"data": {"type": "registration_schemas",
                                                      "id": SCHEMA_ID}},
                     "branched_from": {"data": {"type": "nodes", "id": PARENT_NODE}}}}})["data"]
    save_state(draft_id=d["id"])
    print("draft created:", d["id"])


def cmd_upload():
    st = load_state()
    prov = call("GET", f"{API}/nodes/{PARENT_NODE}/files/")["data"][0]
    url = prov["links"]["upload"] + "?kind=file&name=" + PROTOCOL.name
    req = urllib.request.Request(url, method="PUT", data=PROTOCOL.read_bytes())
    req.add_header("Authorization", f"Bearer {token()}")
    with urllib.request.urlopen(req) as r:
        res = json.load(r)["data"]
    save_state(file_id=res["id"])
    print("uploaded:", PROTOCOL.name, res["id"])


def cmd_respond():
    st = load_state()
    call("PATCH", f"{API}/draft_registrations/{st['draft_id']}/", {
        "data": {"type": "draft_registrations", "id": st["draft_id"],
                 "attributes": {"registration_responses": {
                     "summary": SUMMARY, "uploader": []}}}})
    print("responses set (summary; files freeze via storage archive)")


def cmd_submit():
    st = load_state()
    call("PATCH", f"{API}/draft_registrations/{st['draft_id']}/", {
        "data": {"type": "draft_registrations", "id": st["draft_id"],
                 "relationships": {"subjects": {"data": [
                     {"type": "subjects", "id": "584240da54be81056cecaca8"},  # AI & Robotics
                     {"type": "subjects", "id": "584240da54be81056cecab8f"}]}}}})  # Economics
    d = call("POST", f"{API}/registrations/", {
        "data": {"type": "registrations", "attributes": {},
                 "relationships": {"draft_registration": {
                     "data": {"type": "draft_registrations", "id": st["draft_id"]}}}}})["data"]
    save_state(registration_id=d["id"])
    print("SUBMITTED registration:", d["id"])
    print("public url: https://osf.io/" + d["id"])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "draft"
    {"draft": cmd_draft, "upload": cmd_upload, "respond": cmd_respond,
     "submit": cmd_submit}.get(cmd, cmd_draft)()
