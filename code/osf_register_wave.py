#!/usr/bin/env python3
"""OSF registration for Protocol 12 (confirmatory replication wave).
Reuses node 8pwej from .osf_state.json; uploads protocol + stimulus files,
creates a fresh draft (Open-Ended Registration schema), submits. MUST run
before the first wave generation call (D47 / Protocol 12 §5.1).
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.osf.io/v2"
SCHEMA_ID = "5df83f7dd28338001ac0ab0d"  # Open-Ended Registration
STATE = ROOT / "preregistration/osf_submission/.osf_state.json"
WAVE_STATE = ROOT / "preregistration/osf_submission/.osf_state_wave.json"

FILES = [
    Path("/Users/youssefhariri/Documents/app 25/DeeWaanAI-Next/protocols/12-PROTOCOL-WAVE-CONFIRMATORY-REPLICATION.md"),
    ROOT / "data/problems/fresh_business_cases_20_wave.json",
    ROOT / "data/problems/fresh_domain_map_wave.json",
]

SUMMARY = """Pre-registration of the CONFIRMATORY REPLICATION WAVE (Protocol 12, 2026-08-23)
for 'The Economics of Orchestration'. Scope: 30 fresh business problems (a second
6-domain x 5 grid; Fresh_Case_1-10 held out-of-sample since 2026-07-30 with zero
generation contact, plus 20 newly authored cases attached) x 10 model families x
the 3 core cells (cheap-solo-neutral, cheap-team-neutral, frontier-solo-neutral;
cheap cells x3 reps, frontier cell x2 reps) = 2,400 generation runs, judged by the
identical frozen blind panel (deepseek-chat, GLM-5.2, Llama-3.3-70B; 3 verbatim
variants) = 21,600 judge calls. This registration is the pre-committed UPGRADE GATE
for the Study-1 exploratory battery (domain contingency of the team effect,
capability-gap mechanism r=-0.978, marketing variance advantage): each exploratory
finding upgrades to a headline claim only if its pre-registered wave test passes at
alpha=.05 with the Study-1 direction; otherwise it remains labeled exploratory.
All hypotheses, models, prices, prompts, and interpretation rules are frozen in the
attached protocol BEFORE any wave data are collected, per Nosek et al. (2018) and
Simons (2014). Registry entries D44-D50 in the project repository document every
design decision with academic grounding. Registration time precedes the first wave
generation call."""


def token():
    for line in open(ROOT / ".env"):
        if line.startswith("OSF_TOKEN="):
            return line.split("=", 1)[1].strip()
    sys.exit("no OSF_TOKEN in .env")


def call(method, url, body=None, raw=False):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token()}")
    req.add_header("Content-Type", "application/json")
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data) as r:
            return r.read() if raw else json.load(r)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:800]}")
        raise


def load_state():
    return json.loads(STATE.read_text())


def save_wave_state(**kw):
    st = json.loads(WAVE_STATE.read_text()) if WAVE_STATE.exists() else {}
    st.update(kw)
    WAVE_STATE.write_text(json.dumps(st, indent=2))
    return st


def main():
    step = sys.argv[1] if len(sys.argv) > 1 else "verify"
    st = load_state()
    node = st["node_id"]

    if step == "verify":
        d = call("GET", f"{API}/users/me/")["data"]
        a = d["attributes"]
        print(f"OK user={a['full_name']} email_confirmed={a.get('email_confirmed')}")
        return

    ws = json.loads(WAVE_STATE.read_text()) if WAVE_STATE.exists() else {}

    if step in ("upload", "all"):
        prov = call("GET", f"{API}/nodes/{node}/files/")["data"][0]
        upload_base = prov["links"]["upload"]
        listing = call("GET", f"{API}/nodes/{node}/files/osfstorage/?page[size]=100")["data"]
        existing = {f["attributes"]["name"] for f in listing}
        uploaded = ws.get("files", {})
        for f in FILES:
            if f.name in uploaded:
                continue
            url = upload_base + "?kind=file&name=" + f.name
            req = urllib.request.Request(url, method="PUT", data=f.read_bytes())
            req.add_header("Authorization", f"Bearer {token()}")
            with urllib.request.urlopen(req) as r:
                res = json.load(r)["data"]
            uploaded[f.name] = res["id"]
            print("uploaded:", f.name, res["id"])
        ws = save_wave_state(files=uploaded)
        if step == "upload":
            return

    if step in ("draft", "all"):
        d = call("POST", f"{API}/draft_registrations/", {
            "data": {"type": "draft_registrations",
                     "attributes": {"registration_supplement": "Open-Ended Registration"},
                     "relationships": {
                         "provider": {"data": {"type": "registration-providers", "id": "osf"}},
                         "registration_schema": {"data": {"type": "registration_schemas",
                                                          "id": SCHEMA_ID}},
                         "branched_from": {"data": {"type": "nodes", "id": node}}}}})["data"]
        ws = save_wave_state(draft_id=d["id"])
        print("draft created:", d["id"])
        if step == "draft":
            return

    if step in ("respond", "all"):
        listing = call("GET", f"{API}/nodes/{node}/files/osfstorage/?page[size]=100")["data"]
        want = {f.name for f in FILES}
        uploader = []
        for f in listing:
            if f["attributes"]["name"] not in want:
                continue
            a, l = f["attributes"], f.get("links", {})
            uploader.append({
                "file_id": "osfstorage/" + f["attributes"]["path"].strip("/"),
                "file_name": a["name"],
                "file_urls": {"download": l.get("download", ""), "html": l.get("html", "")},
                "file_hashes": {"sha256": a["extra"]["hashes"].get("sha256", "")},
            })
        call("PATCH", f"{API}/draft_registrations/{ws['draft_id']}/", {
            "data": {"type": "draft_registrations", "id": ws["draft_id"],
                     "attributes": {"registration_responses": {
                         "summary": SUMMARY, "uploader": uploader}}}})
        print("responses set:", len(uploader), "files attached")
        if step == "respond":
            return

    if step in ("submit", "all"):
        d = call("POST", f"{API}/registrations/", {
            "data": {"type": "registrations",
                     "attributes": {"registration_choice": "immediate",
                                    "included_node_ids": [node]},
                     "relationships": {"draft_registration": {
                         "data": {"type": "draft_registrations", "id": ws["draft_id"]}}}}})["data"]
        save_wave_state(registration_id=d["id"])
        print("SUBMITTED Protocol-12 registration:", d["id"])
        print("public url: https://osf.io/" + d["id"])


if __name__ == "__main__":
    main()
