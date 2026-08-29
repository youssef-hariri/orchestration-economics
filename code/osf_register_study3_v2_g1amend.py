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
STATE = ROOT / "preregistration/osf_submission/.osf_state_study3_v2_g1amend.json"
PROTOCOL = ROOT / "protocols" / "13-PROTOCOL-STUDY3-DESIGN-AUTHORSHIP.md"
PARENT_NODE = "8pwej"  # 'The Economics of Orchestration' project node

SUMMARY = """G1 GATE CLARIFICATION amendment for Study 3 (Protocol 13 instrument v2),
chained to registrations osf.io/9ukjz (v1) and osf.io/bwc93 (v2 instrument
amendment). Filed BEFORE the v2 full run and before any v2 outcome analysis.
Context: the v2 pilot (32 non-qwen tasks attempted; qwen's 8 run in its
discount window UTC 14:00-00:00) showed gpt/gemini/claude at 8/8 completion and
kimi at 6/8, the two misses being (1) a persistent provider content-moderation
block on the kimi-k3 designer call for one problem ('high risk', 3 attempts)
and (2) one design_failed (empty designer output after one repair retry).
Original G1 wording ('schema-valid design rate >= 90% AND execution completion
>= 90% per family, else family reported infeasible') would force dropping the
kimi family over provider-side moderation and a single disclosed design failure
— both of which are phenomena Study 3 is designed to measure, not instrument
defects (design validity was 31/32 = 97%). CLARIFICATION: provider
content-moderation blocks and disclosed design_failed cases count as DISCLOSED
ATTRITION in the participant flow, not as infeasibility; a family remains in
the factorial if completion >= 80% after excluding moderation-blocked tasks
from the denominator base (reported both ways). All other protocol elements
unchanged. Decision trail: D55 -> D56 -> D57."""


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
    url = prov["links"]["upload"] + "?kind=file&name=" + "v2-AMENDED-" + PROTOCOL.name
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
