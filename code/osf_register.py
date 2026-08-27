#!/usr/bin/env python3
"""OSF registration helper for 'The Economics of Orchestration'.
Reads OSF_TOKEN from ./.env (plain text). Steps run by subcommand.
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.osf.io/v2"


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


def cmd_verify():
    d = call("GET", f"{API}/users/me/")["data"]
    a = d["attributes"]
    print(f"OK user={a['full_name']} id={d['id']} email={a.get('email')} "
          f"email_confirmed={a.get('email_confirmed', 'n/a')}")


def cmd_schemas():
    d = call("GET", f"{API}/providers/registrations/osf/schemas/?page[size]=50")
    for s in d["data"]:
        print(s["id"], "|", s["attributes"]["name"], "| active:", s["attributes"].get("active"))


SCHEMA_ID = "5df83f7dd28338001ac0ab0d"  # Open-Ended Registration
STATE = ROOT / "preregistration/osf_submission/.osf_state.json"
PROTOCOLS = Path("/Users/youssefhariri/Documents/app 25/DeeWaanAI-Next/protocols")
SUBDIR = ROOT / "preregistration/osf_submission"

SUMMARY = """Memorialization of the pre-registration for 'The Economics of Orchestration':
a pre-registered 2x2x2 within-subjects factorial (Tier Cheap/Frontier x Structure
Solo/Team x Persona Neutral/Persona; 8 cells x 5 model families; 19 cross-cultural
business problems; judging panel of 3 LLM judges x 3 verbatim variants, blind),
plus two approved amendments. Amendment A1 (2026-07-30, before the first main-run
generation call) corrected pilot-stage measurement infrastructure (full-text judging,
judge output integrity, audit fields). Amendment A2 (2026-08-05, drafted and approved
while main-run judging was still running, before interim-2 data lock) adds estimation
and robustness layers to the interim-2 analysis (bootstrap CIs, BH-FDR, Type-II ANOVA
with partial eta-squared, Rouder JZS Bayes factors, leave-one-family-out and
leave-one-problem-out sensitivity, sensitivity power) with an integrity clause:
A2 outputs never alter the pre-registered stopping decisions. TIMING DISCLOSURE:
this OSF timestamp post-dates main-run generation; see attached cover document
(00-COVER-AND-TIMING-DISCLOSURE.md) for the honest ordering of events. No amendment
changed hypotheses, design factors, cells, sample plan, or stopping rules."""


def save_state(**kw):
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    st.update(kw)
    STATE.write_text(json.dumps(st, indent=2))
    return st


def load_state():
    return json.loads(STATE.read_text())


def cmd_create_node():
    d = call("POST", f"{API}/nodes/", {
        "data": {"type": "nodes", "attributes": {
            "title": "The Economics of Orchestration",
            "category": "project",
            "description": ("Pre-registration memorialization: 2x2x2 factorial study of "
                            "LLM orchestration economics (tier x structure x persona), "
                            "protocols 01-04 + Amendments A1/A2. See registration.")}}})["data"]
    save_state(node_id=d["id"])
    print("node created:", d["id"])


def cmd_create_draft():
    st = load_state()
    d = call("POST", f"{API}/draft_registrations/", {
        "data": {"type": "draft_registrations",
                 "attributes": {"registration_supplement": "Open-Ended Registration"},
                 "relationships": {
                     "provider": {"data": {"type": "registration-providers", "id": "osf"}},
                     "registration_schema": {"data": {"type": "registration_schemas",
                                                      "id": SCHEMA_ID}},
                     "branched_from": {"data": {"type": "nodes", "id": st["node_id"]}}}}})["data"]
    save_state(draft_id=d["id"])
    print("draft created:", d["id"])


def cmd_upload():
    st = load_state()
    prov = call("GET", f"{API}/nodes/{st['node_id']}/files/")["data"][0]
    upload_base = prov["links"]["upload"]
    files = sorted(SUBDIR.glob("0*.md")) + sorted(PROTOCOLS.glob("0*.md"))
    uploaded = st.get("files", {})
    for f in files:
        if f.name in uploaded:
            continue
        url = upload_base + "?kind=file&name=" + f.name
        req = urllib.request.Request(url, method="PUT", data=f.read_bytes())
        req.add_header("Authorization", f"Bearer {token()}")
        with urllib.request.urlopen(req) as r:
            res = json.load(r)["data"]
        uploaded[f.name] = res["id"]
        print("uploaded:", f.name, res["id"])
    save_state(files=uploaded)


def cmd_respond():
    st = load_state()
    listing = call("GET", f"{API}/nodes/{st['node_id']}/files/osfstorage/?page[size]=20")["data"]
    uploader = []
    for f in listing:
        a, l = f["attributes"], f.get("links", {})
        uploader.append({
            "file_id": "osfstorage/" + f["attributes"]["path"].strip("/"),
            "file_name": a["name"],
            "file_urls": {"download": l.get("download", ""), "html": l.get("html", "")},
            "file_hashes": {"sha256": a["extra"]["hashes"].get("sha256", "")},
        })
    call("PATCH", f"{API}/draft_registrations/{st['draft_id']}/", {
        "data": {"type": "draft_registrations", "id": st["draft_id"],
                 "attributes": {"registration_responses": {
                     "summary": SUMMARY, "uploader": uploader}}}})
    print("responses set:", len(uploader), "file objects attached")


def cmd_submit():
    st = load_state()
    d = call("POST", f"{API}/registrations/", {
        "data": {"type": "registrations", "attributes": {},
                 "relationships": {"draft_registration": {
                     "data": {"type": "draft_registrations", "id": st["draft_id"]}}}}})["data"]
    save_state(registration_id=d["id"])
    print("SUBMITTED registration:", d["id"])
    print("public url: https://osf.io/" + d["id"])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    {"verify": cmd_verify, "schemas": cmd_schemas, "node": cmd_create_node,
     "draft": cmd_create_draft, "upload": cmd_upload, "respond": cmd_respond,
     "submit": cmd_submit}.get(cmd, cmd_verify)()
