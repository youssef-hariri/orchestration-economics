#!/usr/bin/env python3
"""One-shot: child-component registration path for Protocol 12.
Node 8pwej is already registered (mjb8x), so new files must live in a fresh
child component; the wave draft is re-pointed at that child and submitted.
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.osf.io/v2"
TOK = [l.split("=", 1)[1].strip() for l in open(ROOT / ".env")
       if l.startswith("OSF_TOKEN=")][0]
ST = ROOT / "preregistration/osf_submission/.osf_state.json"
WS_PATH = ROOT / "preregistration/osf_submission/.osf_state_wave.json"
FILES = [
    Path("/Users/youssefhariri/Documents/app 25/DeeWaanAI-Next/protocols/12-PROTOCOL-WAVE-CONFIRMATORY-REPLICATION.md"),
    ROOT / "data/problems/fresh_business_cases_20_wave.json",
    ROOT / "data/problems/fresh_domain_map_wave.json",
]
SUMMARY = open(ROOT / "code/osf_register_wave.py").read().split('SUMMARY = """')[1].split('"""')[0]


def call(method, url, body=None, raw_bytes=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {TOK}")
    if raw_bytes is not None:
        data = raw_bytes
    elif body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    else:
        data = None
    try:
        with urllib.request.urlopen(req, data) as x:
            return json.load(x)
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:500])
        raise


def main():
    st = json.load(open(ST))
    ws = json.load(open(WS_PATH))

    if "child_node_id" not in ws:
        c = call("POST", f"{API}/nodes/", {
            "data": {"type": "nodes",
                     "attributes": {
                         "title": "Protocol 12 - Confirmatory replication wave",
                         "category": "other",
                         "description": "Pre-registration artifacts for Protocol 12 "
                                        "(confirmatory replication wave, 2026-08-23): "
                                        "protocol text and frozen stimulus set."},
                     "relationships": {"parent": {"data": {"type": "nodes",
                                                            "id": st["node_id"]}}}}})["data"]
        ws["child_node_id"] = c["id"]
        json.dump(ws, open(WS_PATH, "w"), indent=2)
        print("child component:", c["id"])
    child = ws["child_node_id"]

    prov = call("GET", f"{API}/nodes/{child}/files/")["data"][0]
    up = prov["links"]["upload"]
    time.sleep(3)  # storage provisioning eventual consistency on fresh nodes
    listing = call("GET", f"{API}/nodes/{child}/files/osfstorage/?page[size]=20")["data"]
    have = {f["attributes"]["name"] for f in listing}
    for f in FILES:
        if f.name not in have:
            last = None
            for attempt in range(3):
                try:
                    call("PUT", up + f"?kind=file&name={f.name}",
                         raw_bytes=f.read_bytes())
                    print("uploaded to child:", f.name)
                    break
                except urllib.error.HTTPError as e:
                    last = e
                    print(f"upload attempt {attempt + 1} failed, retrying…")
                    time.sleep(5)
            else:
                raise last

    listing = call("GET", f"{API}/nodes/{child}/files/osfstorage/?page[size]=20")["data"]
    uploader = []
    for f in listing:
        a, l = f["attributes"], f.get("links", {})
        uploader.append({
            "file_id": "osfstorage/" + a["path"].strip("/"),
            "file_name": a["name"],
            "file_urls": {"download": l.get("download", ""), "html": l.get("html", "")},
            "file_hashes": {"sha256": a["extra"]["hashes"].get("sha256", "")},
        })

    call("PATCH", f"{API}/draft_registrations/{ws['draft_id']}/", {
        "data": {
            "type": "draft_registrations",
            "id": ws["draft_id"],
            "attributes": {"registration_responses": {
                "uploader": uploader, "summary": SUMMARY}},
            "relationships": {"branched_from": {
                "data": {"type": "nodes", "id": child}}}}})
    print("draft re-pointed to child; uploader files:", len(uploader))

    d = call("POST", f"{API}/registrations/", {
        "data": {
            "type": "registrations",
            "attributes": {"registration_choice": "immediate"},
            "relationships": {"draft_registration": {
                "data": {"type": "draft_registrations", "id": ws["draft_id"]}}}}})["data"]
    ws["registration_id"] = d["id"]
    json.dump(ws, open(WS_PATH, "w"), indent=2)
    print("SUBMITTED:", d["id"], "| https://osf.io/" + d["id"])


if __name__ == "__main__":
    main()
