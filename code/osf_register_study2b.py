#!/usr/bin/env python3
"""OSF registration for Study 2b (Protocol 11, re-drafted 2026-08-21, D43).

Registers the 2x5 factorial refinement study (refiner identity x family) as its
OWN Open-Ended Registration, branched from the existing project node (8pwej),
with a separate state file so the Study-1 memorialization is never touched.
Reads OSF_TOKEN from ./.env. Steps run by subcommand, idempotent via state.
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.osf.io/v2"
SCHEMA_ID = "5df83f7dd28338001ac0ab0d"  # Open-Ended Registration
STATE = ROOT / "preregistration/osf_submission/.osf_state_study2b.json"
PROTOCOL = Path("/Users/youssefhariri/Documents/app 25/DeeWaanAI-Next/protocols/"
                "11-PROTOCOL-STUDY2B-REFINER-GPT-GEMINI.md")
PARENT_NODE = "8pwej"  # 'The Economics of Orchestration' project node

SUMMARY = """Pre-registration of Study 2b (Protocol 11, re-drafted 2026-08-21): a 2x5
factorial completion of the refinement stage of 'The Economics of Orchestration'.
Arm U (universal refiner): the frozen deepseek-chat add-only refiner of Study 2
(Protocol 09) is applied to the two remaining families (gpt, gemini), completing
the five-family test of refinement as a model-agnostic process; the Study-2
results for kimi/claude/qwen are reused as-is (identical prompt, judge panel,
aggregation). Arm W (within-family refiner): each of the five families' team
answers (C-T-P) is refined by that family's OWN cheap-sibling model
(gpt-5.6-luna, gemini-3.1-flash-lite, kimi-k2.6, claude-haiku-4-5-20251001,
qwen3.7-plus-2026-05-26), keeping every pipeline model-homogeneous so results
attribute to the team. The refinement prompt is the single controlled variable
shared across arms (byte-identical, verified). Hypotheses: H3.1-U/H3.1-W
(paired refined-vs-frontier superiority, Holm), H3.2 (Novelty protection,
margin -0.10), H3.3 (Usefulness/Elaboration repair), H3.4 (paired
within-family-minus-universal refiner-identity contrast, two-sided, no
pre-committed direction). Gates: G1 feasibility >=95%, G2 pilot superiority
(d>=0.2, CI excluding 0) per family before extension from 20 to 57
pairs/family. Judging: frozen three-judge panel (deepseek-chat, GLM-5.2,
Llama-3.3-70B) x 3 verbatim variants, blind. Scheduling: DeepSeek calls only
UTC 04:00-06:00/10:00-01:00; qwen calls only UTC 14:00-00:00. Budget <= $60.
LOCKED ABDUCTIVE RATIONALE: Study-2 results on three families motivated both
arms; every hypothesis, sample, instrument, gate, and analysis in the attached
protocol was fixed before the first Study-2b call, per Nosek et al. (2018).
This registration timestamp PRECEDES all Study-2b data collection. Decision
trail: D39 -> D41 -> D42 -> D43 (DESIGN-DECISIONS.md)."""


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
    # Summary only. NOTE (execution log 2026-08-22): attaching uploader file
    # objects makes POST /registrations/ reject the submission ("files attached
    # but not part of a component being registered"); the node's osfstorage
    # (incl. the Protocol 11 file) is frozen into the registration archive
    # automatically — same behavior as Study-1 registration mjb8x.
    call("PATCH", f"{API}/draft_registrations/{st['draft_id']}/", {
        "data": {"type": "draft_registrations", "id": st["draft_id"],
                 "attributes": {"registration_responses": {
                     "summary": SUMMARY, "uploader": []}}}})
    print("responses set (summary; files freeze via storage archive)")


def cmd_submit():
    st = load_state()
    # subjects must live on the DRAFT (subjects on the registration POST are ignored)
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
