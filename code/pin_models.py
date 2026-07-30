#!/usr/bin/env python3
"""
pin_models.py — Phase 0 model-pin verification.

Verifies that every model pinned in config/model_registry.json actually exists
on the corresponding provider account, by listing the provider's /models
endpoint with the API keys in .env. Prints a PASS/FAIL table and exits non-zero
on any failure. Never prints API keys.

Run:  python3 code/pin_models.py
Requires: .env in the repo root (git-ignored) with KIMI_API_KEY,
ALIBABA_API_KEY, DEEPSEEK_API_KEY, TOGETHER_API_KEY (and later OPENAI_API_KEY,
ANTHROPIC_API_KEY, GEMINI_API_KEY).

No LLM tokens are consumed: only GET /models listings (free).
See DESIGN-DECISIONS.md D21/D22 and MANIFEST.md Entry 7.
"""

import json
import os
import ssl
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "config", "model_registry.json")


def ssl_context() -> ssl.SSLContext:
    """macOS system Python often lacks CA certs; prefer certifi when present."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def load_env():
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def list_models(endpoint: str, key: str) -> set:
    url = endpoint.rstrip("/") + "/models"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            # Together.ai rejects urllib's default UA with 403
            "User-Agent": "orchestration-economics-pin-models/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30, context=ssl_context()) as r:
        data = json.load(r)
    # OpenAI-style {"data": [...]} vs Together's bare [...]
    models = data["data"] if isinstance(data, dict) else data
    return {m["id"] for m in models}


def main() -> int:
    load_env()
    reg = json.load(open(REGISTRY))
    checks = []  # (label, endpoint, env_key, model_id)

    for family, g in reg["generators"].items():
        if "blocker" in g:
            checks.append((f"generator/{family}", None, None, "SKIP: " + g["blocker"]))
            continue
        for tier in ("frontier", "cheap_sibling"):
            checks.append((f"generator/{family}/{tier}", g["endpoint"], g["env_key"], g[tier]["model"]))
    for j in reg["judges"]:
        checks.append((f"judge/{j['family']}", j["endpoint"], j["env_key"], j["model"]))
    d = reg["designer_A7"]
    checks.append(("designer_A7", d["endpoint"], d["env_key"], d["model"]))
    fb = reg["fallback_family"]
    for tier in ("frontier", "cheap_sibling"):
        checks.append((f"fallback/{fb['family']}/{tier}", fb["endpoint"], fb["env_key"], fb[tier]["model"]))

    cache: dict = {}
    failures = 0
    for label, endpoint, env_key, model in checks:
        if endpoint is None:
            print(f"SKIP  {label:38s} {model}")
            continue
        key = os.environ.get(env_key, "")
        if not key:
            print(f"FAIL  {label:38s} {model}  (missing {env_key})")
            failures += 1
            continue
        if endpoint not in cache:
            try:
                cache[endpoint] = list_models(endpoint, key)
            except Exception as e:  # noqa: BLE001 — report any listing failure
                cache[endpoint] = e
        listing = cache[endpoint]
        if isinstance(listing, Exception):
            print(f"FAIL  {label:38s} {model}  (listing error: {listing})")
            failures += 1
        elif model in listing:
            print(f"PASS  {label:38s} {model}")
        else:
            print(f"FAIL  {label:38s} {model}  (not in account listing)")
            failures += 1

    print(f"\n{'ALL PINNED MODELS VERIFIED' if failures == 0 else str(failures) + ' FAILURES'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
