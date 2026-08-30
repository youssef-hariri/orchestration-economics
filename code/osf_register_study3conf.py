#!/usr/bin/env python3
"""OSF registration for the Study 3 confirmatory replication (Protocol 16, D59/D60).

Registers the D-SELF-only out-of-sample replication of the Study 3 family-specific
routing rule (30 wave problems, 5 core families) as its OWN Open-Ended Registration,
branched from the project node (8pwej), with a separate state file. Adapted from
osf_register_study3.py (same API mechanics).
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.osf.io/v2"
SCHEMA_ID = "5df83f7dd28338001ac0ab0d"  # Open-Ended Registration
STATE = ROOT / "preregistration/osf_submission/.osf_state_study3conf.json"
PROTOCOL = ROOT / "protocols" / "16-PROTOCOL-STUDY3-CONFIRMATORY.md"
PARENT_NODE = "8pwej"  # 'The Economics of Orchestration' project node

SUMMARY = """Pre-registration of the Study 3 confirmatory replication (Protocol 16)
in 'The Economics of Orchestration'. Study 3 (OSF 9ukjz/bwc93/639eq) found a
family-specific orchestration rule — cheap SELF-designed auto-pipelines beat the
family's frontier-solo flagship for kimi (d=+0.85), qwen (+0.55), gemini (+0.46),
tie gpt (d=-0.07), and lose decisively for claude (d=-3.15) — but on the same 19
problems as Study 1. This protocol tests that pattern out-of-sample on the 30
fresh post-cutoff problems of the Protocol-12 wave (zero overlap with Study 1/3).
SCOPE, pre-declared from Study 3 results: D-SELF arm only (Study 3 Contrast A
found no authorship effect in 4/5 families; the claude exception is an
executor-capability artifact, so D-FRONT is dropped by this decision rule and its
evidence stands from Study 3); comparator = the wave's frozen, already-judged
F-S-N runs on the same 30 problems (no new frontier-solo generation). Design:
1 arm x 5 families (kimi, qwen, gpt, claude, gemini — the replication matches the
claim; no new families) x 30 problems x 3 reps = 450 runs. Instrument identical
to Study 3 v2 (protocol13-v2 platform-verbatim auto-design prompt: free roles,
if/while gates, 1-7 steps, designer temp 0.3, no human-approval steps; one repair
retry, then design_failed disclosed attrition per the D57 rule: family retained if
completion >= 80% excluding provider moderation blocks, reported both ways).
BINDING predictions (Novelty, D-SELF vs wave F-S-N, one-sided alpha=.05): R1 kimi
d>0; R2 qwen d>0; R3 gemini d>0; R4 gpt |d|<0.30 (TOST-style equivalence); R5
claude d<-1.0. Headline 'family moderates orchestration gains' requires R1-R3 and
R5 to pass; R4 guards the gpt tie. No post-hoc relabeling (D44/wave discipline).
Judging: frozen blind three-judge panel (deepseek-chat, GLM-5.2, Llama-3.3-70B)
x 3 verbatim variants, judge_v2 unchanged; DeepSeek judged off-peak. Analysis:
per-family Cohen d on Novelty vs frozen wave F-S-N per-problem means; script
frozen and hash-locked before judging; results ship as JSON + CSV (D54).
Scheduling: qwen generation deferred to its UTC 14:00-00:00 discount window;
kimi designer on Moonshot direct (k3 frontier not needed: no D-FRONT). This
registration timestamp PRECEDES all Protocol-16 data collection. Decision trail:
D59 (Protocols 14/15 superseded), D60 (this protocol); MANIFEST Entry 79.
Runner: code/study3conf_run.py (append-only ledger, resumable)."""


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
