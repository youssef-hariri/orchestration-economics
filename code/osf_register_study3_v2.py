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
STATE = ROOT / "preregistration/osf_submission/.osf_state_study3_v2.json"
PROTOCOL = ROOT / "protocols" / "13-PROTOCOL-STUDY3-DESIGN-AUTHORSHIP.md"
PARENT_NODE = "8pwej"  # 'The Economics of Orchestration' project node

SUMMARY = """AMENDMENT registration for Study 3 (Protocol 13, instrument v2, D56),
linked to the original registration osf.io/9ukjz. After the 9ukjz pilot (40/40
tasks, gates G1+G2 passed) and 33 full-run starts — none of it analyzed for
outcomes — human audit of the instrument against the DeeWaanAI platform source
code (api/services/autoDesignService.ts) found that the v1 designer stage
silently diverged from the platform feature under study: (1) a bespoke designer
prompt instead of the platform's verbatim internal auto-design prompt; (2) a
hard 4-step cap vs the platform's 'keep pipelines under 8 steps'; (3) free vs
platform parameters (platform designer temperature 0.3, retry 0.2); (4) the
platform's role vocabulary is suggestive, not enforced. Because the research
question is whether pipeline DESIGN AUTHORSHIP affects quality, the designer
instrument must be the platform's actual one. Instrument v2 therefore uses the
platform-verbatim auto-design prompt with free task-adapted roles, if/while
quality gates (while: max 3 iterations; if-gate revisits capped at 3), 1-7
steps, designer temperature 0.3, and ONE disclosed modification: approval
(human-in-the-loop) steps disallowed (fully automated experiment). Gate
execution is platform-faithful (last-line keyword routing via ifMappings /
targetStep). The judged artifact is the final agent step's output. The 73 v1
runs are archived as superseded pilot-extension data, never pooled into Study 3
results. All other Protocol 13 elements are unchanged: 2x5 factorial (D-SELF:
cheap designs+executes; D-FRONT: frontier designs, cheap executes), 19
confirmatory problems x 3 reps = 570 generations; pilot of 40 (seeded draw
Business_Problem_6/8/9/12) with gates G1 (>=90% valid designs AND >=90%
completion) and G2 (stop only if D-FRONT < frozen C-T-N baseline by d < -0.30);
frozen blind 3-judge panel x 3 variants; primary contrasts D-FRONT vs D-SELF
(Holm across families) and both vs frozen C-T-N; designer tokens counted in arm
cost; DeepSeek judging off-peak; qwen generation UTC 14:00-00:00; budget <= $45.
This amendment registration timestamp PRECEDES all v2 data collection.
Decision trail: D55 -> D56; MANIFEST Entries 69-71."""


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
