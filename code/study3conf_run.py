#!/usr/bin/env python3
"""Protocol 16 — Study 3 confirmatory replication runner (D-SELF only).

Wraps code/study3_design_run.py (Protocol 13 v2 instrument, D56) with:
- problems: the 30 wave problems (fresh_business_cases_10.json +
  fresh_business_cases_20_wave.json), post-cutoff, zero overlap with Study 1/3
- arm: D-SELF only (pre-registered decision rule, OSF zkm8v §2)
- separate ledger/store/tag so Study 3 data are never touched
- default families exclude qwen (author directive 2026-08-30: deferred to the
  qwen discount window UTC 14:00-00:00; run later with --families qwen)

Resumability: append-only ledger + step-level checkpoints inherited from the
Protocol 13 runner. Keys loaded the same way; run kimi with
`env -u KIMI_API_KEY` so the stale shell var does not shadow the fresh .env key.
"""
import argparse
import json
import random
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import study3_design_run as s3  # noqa: E402

# --- Protocol 16 overrides -------------------------------------------------
s3.LEDGER = ROOT / "runs" / "logs" / "study3conf_ledger.jsonl"
s3.EXHAUSTION = ROOT / "runs" / "logs" / "study3conf_credit_exhaustion.jsonl"
s3.STORE = ROOT / "runs" / "study3conf" / "study3conf_store.json"
s3.PROMPT_TAG = "protocol16"
DEFAULT_FAMILIES = ["kimi", "gpt", "claude", "gemini"]  # qwen deferred (window)
# deterministic pilot draw: random.Random(20260830).sample(sorted(30 wave
# problems), 4) = the 4 below, verified 4 distinct domains
# (hr_organization, product_innovation, strategy_market_entry, finance)
PILOT_PROBLEMS = ["Fresh_Case_10", "Fresh_Case_16", "Fresh_Case_22", "Fresh_Case_12"]


def load_problems():
    """The 30 wave problems, rendered per D32.3 (background + problem, verbatim)."""
    out = {}
    for f in ["fresh_business_cases_10.json", "fresh_business_cases_20_wave.json"]:
        bank = json.loads((ROOT / "data" / "problems" / f).read_text())
        for pid, p in bank.items():
            if isinstance(p, dict):
                out[pid] = f"{p['background_context']}\n\n{p['business_problem']}"
    return out


s3.load_problems = load_problems  # monkeypatch for s3.build_store


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--families", default="")
    ap.add_argument("--reps", type=int, default=0)
    ap.add_argument("--ignore-window", action="store_true")
    ap.add_argument("--build-store", action="store_true")
    args = ap.parse_args()

    if args.build_store:
        s3.build_store()
        return

    problems = load_problems()
    pids = PILOT_PROBLEMS if args.pilot else sorted(problems)
    reps = args.reps or (1 if args.pilot else 3)
    fams = args.families.split(",") if args.families else DEFAULT_FAMILIES
    tasks = [{"arm": "D-SELF", "family": fam, "problem": pid, "rep": r}
             for fam in fams for pid in pids for r in range(1, reps + 1)]
    random.Random(42).shuffle(tasks)  # same interleave seed as Study 3 (D17)

    done, exhausted, terminal = s3.load_ledger()
    todo = [t for t in tasks
            if f"D-SELF__{t['family']}__{t['problem']}__rep{t['rep']}" not in done
            and f"D-SELF__{t['family']}__{t['problem']}__rep{t['rep']}" not in terminal
            and t["family"] not in exhausted]
    print(f"Protocol 16 plan: {len(tasks)} tasks | todo {len(todo)} | "
          f"exhausted families: {sorted(exhausted) or 'none'}"
          + (" (WINDOW OVERRIDE)" if args.ignore_window else ""))
    if args.dry_run:
        print(Counter((t["arm"], t["family"]) for t in tasks))
        return

    keys = {k: s3.load_key(k) for k in
            {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
             "KIMI_API_KEY", "ALIBABA_API_KEY", "TOGETHER_API_KEY"}}
    stats = Counter()
    with ThreadPoolExecutor(max_workers=s3.WORKERS) as ex:
        futs = [ex.submit(s3.run_task, t, problems, keys, args.ignore_window)
                for t in todo]
        for i, f in enumerate(futs, 1):
            res = f.result()
            stats[res] += 1
            if i % 20 == 0 or res in ("failed", "credit_exhausted", "design_failed"):
                print(f"[{i}/{len(todo)}] {res} | totals: {dict(stats)}", flush=True)
    print(f"done: {dict(stats)}")
    s3.build_store()


if __name__ == "__main__":
    main()
