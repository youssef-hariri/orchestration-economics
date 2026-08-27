#!/usr/bin/env python3
"""Protocol 10 sec 4 — Wave 2 closed coding (blinded) + Cohen's kappa.

Analyst-frozen 13-item codebook (merged deductive skeleton + Wave-1 observations).
90 texts (30 triples x 3 roles) x 2 coders = 180 calls. temp 0, blinded: the prompt
contains NO role/family/score information.
Outputs: runs/logs/qual2_closed.jsonl, results/qual2_kappa.json,
results/qual2_codebook.json (frozen copy).
"""
import concurrent.futures
import json
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import judge_v2 as jv                # noqa: E402
from qual_a4_closed import call, extract_json  # noqa: E402

CODER_FAMILIES = ["deepseek", "zhipu"]
WORKERS_PER_CODER = 8


def kappa(a, b):
    n = len(a)
    a11 = sum(1 for x, y in zip(a, b) if x == 1 and y == 1)
    a00 = sum(1 for x, y in zip(a, b) if x == 0 and y == 0)
    po = (a11 + a00) / n
    p1a, p1b = sum(a) / n, sum(b) / n
    pe = p1a * p1b + (1 - p1a) * (1 - p1b)
    return ((po - pe) / (1 - pe) if pe < 1 else 1.0), po

# Analyst-frozen codebook (Protocol 10), grounded in Wave-1 features.
CODEBOOK = [
    {"id": "diagnostic_reframe", "rq": "RQ1", "name": "Diagnostic reframing",
     "definition": "The answer decomposes the given problem into distinct sub-problems or streams, or explicitly challenges/reframes the framing the question assumes."},
    {"id": "named_concepts", "rq": "RQ1", "name": "Named analytical concepts",
     "definition": "The text introduces newly named concepts, taxonomies, or named analytical distinctions (beyond citing existing frameworks)."},
    {"id": "assumption_test", "rq": "RQ1", "name": "Assumption testing",
     "definition": "The text explicitly questions a default assumption embedded in the question and offers alternative explanations or tests to discriminate them."},
    {"id": "concise_maxims", "rq": "RQ1", "name": "Concise prescriptive maxims",
     "definition": "Short aphoristic, memorable prescriptive sentences that compress an argument (e.g., one-line rules or slogans used seriously)."},
    {"id": "operational_parameters", "rq": "RQ1", "name": "Concrete operational parameters",
     "definition": "Specific operational parameters such as decision SLAs, budget caps, kill criteria, timeboxes, or pre-approved thresholds tied to a mechanism."},
    {"id": "cultural_localization", "rq": "RQ1", "name": "Cultural localization",
     "definition": "Strategy adapted via local cultural concepts, terms, languages, or norms specific to the target region (not generic global advice)."},
    {"id": "structured_report", "rq": "RQ2", "name": "Structured report format",
     "definition": "Formal report/memo scaffolding: executive summary, TO/FROM/DATE headers, numbered sections with headings."},
    {"id": "external_authority", "rq": "RQ2", "name": "External authority citation",
     "definition": "Named external frameworks, authors, or best-practice authorities are cited (e.g., Hofstede, Culture Map, known models)."},
    {"id": "phased_timeline", "rq": "RQ2", "name": "Phased implementation timeline",
     "definition": "A phased rollout plan with milestones, gates, or go/no-go decision points across months/quarters."},
    {"id": "tables_matrices", "rq": "RQ2", "name": "Tables and matrices",
     "definition": "Comparative tables, matrices, audit checklists, or risk tables organizing content."},
    {"id": "quantified_targets", "rq": "RQ2", "name": "Quantified targets",
     "definition": "Explicit numeric targets or KPI thresholds (percentages, dollar amounts, durations) stated as success criteria."},
    {"id": "granular_ops_detail", "rq": "RQ2", "name": "Granular operational detail",
     "definition": "Week-by-week or day-level implementation granularity: per-shift budgets, dataset sizes, sample sizes, workshop durations, named roles."},
    {"id": "redundancy_bloat", "rq": "RQ2", "name": "Redundancy / boilerplate",
     "definition": "Visible repetition of key phrases, boilerplate advisory language, or padding that goes beyond what the argument requires."},
]

PROMPT = """You are a reliability coder applying a FIXED codebook. Read the answer \
(an anonymized AI response to a business problem; you do not know which system produced it) \
and decide, for EACH codebook item, whether it is clearly PRESENT (1) or ABSENT (0). \
Code conservatively: if unsure, code 0. Do not judge quality.

=== BUSINESS PROBLEM ===
{problem_text}

=== ANSWER ===
{solution_text}

=== CODEBOOK ===
{codebook}

Return ONLY valid JSON: {{"items": [{{"id": "<codebook id>", "present": 0 or 1}}, ...]}} \
with one entry per codebook item, in order."""


def main():
    pack = json.load(open(ROOT / "runs/qual2/triples.json"))
    triples = pack["triples"]
    coders = [j for j in jv.judges if j["family"] in CODER_FAMILIES]
    codebook_text = "\n".join(f"- id={c['id']} | {c['name']}: {c['definition']}" for c in CODEBOOK)
    ids = [c["id"] for c in CODEBOOK]
    (ROOT / "results/qual2_codebook.json").write_text(
        json.dumps({"frozen": "2026-07-30", "protocol": "10", "items": CODEBOOK}, indent=1) + "\n")

    out_path = ROOT / "runs/logs/qual2_closed.jsonl"
    done = set()
    if out_path.exists():
        for line in open(out_path):
            j = json.loads(line)
            if not j.get("error") and j.get("vector") is not None:
                done.add((j["key"], j["coder_family"]))

    tasks = []
    for t in triples:
        for role, text in t["texts"].items():
            key = f"{t['tripleId']}:{role}"
            prompt = (PROMPT.replace("{problem_text}", t["problem_text"][:2000])
                      .replace("{solution_text}", text)
                      .replace("{codebook}", codebook_text))
            for coder in coders:
                if (key, coder["family"]) not in done:
                    tasks.append((key, coder, prompt))
    total = len(triples) * 3 * len(coders)
    print(f"closed coding: {len(triples)} triples x 3 texts x {len(coders)} coders; "
          f"{len(tasks)} pending, {len(done)} done; codebook={len(ids)} items")

    lock = threading.Lock()
    counter = {"n": len(done)}
    sems = {c["family"]: threading.Semaphore(WORKERS_PER_CODER) for c in coders}

    def run_task(task, out):
        key, coder, prompt = task
        with sems[coder["family"]]:
            rec = None
            for attempt in range(3):
                try:
                    text, usage = call(coder, prompt)
                    parsed = extract_json(text)
                    items = (parsed or {}).get("items") or []
                    vec = {i["id"]: int(i.get("present", 0)) for i in items
                           if i.get("id") in ids}
                    rec = {"key": key, "coder_family": coder["family"],
                           "vector": vec if len(vec) == len(ids) else None,
                           "usage": usage, "attempt": attempt,
                           "harness": "qual_study2/closed",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    if rec["vector"] is not None:
                        break
                except Exception as e:  # noqa: BLE001
                    rec = {"key": key, "coder_family": coder["family"],
                           "error": str(e)[:300], "harness": "qual_study2/closed",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    time.sleep(2 ** attempt * 2)
        with lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            counter["n"] += 1
            ok = rec.get("vector") is not None
            print(f"[{counter['n']}/{total}] {key} {coder['family']}: "
                  f"{'OK sum=' + str(sum(rec['vector'].values())) if ok else rec.get('error', 'INCOMPLETE')}")

    with open(out_path, "a") as out:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=WORKERS_PER_CODER * len(coders)) as pool:
            futs = [pool.submit(run_task, t, out) for t in tasks]
            for f in concurrent.futures.as_completed(futs):
                f.result()

    # ---- kappa
    mat = {}
    for line in open(out_path):
        j = json.loads(line)
        if j.get("vector") is not None:
            mat.setdefault(j["key"], {})[j["coder_family"]] = j["vector"]
    pairs = [r for r in mat.values() if len(r) == 2]

    per_item = {}
    all_a, all_b = [], []
    for cid in ids:
        a = [p["deepseek"][cid] for p in pairs]
        b = [p["zhipu"][cid] for p in pairs]
        k, po = kappa(a, b)
        per_item[cid] = {"kappa": round(k, 3), "pct_agree": round(po * 100, 1),
                         "prevalence_ds": round(sum(a) / len(a), 2),
                         "prevalence_zp": round(sum(b) / len(b), 2)}
        all_a += a
        all_b += b
    pooled_k, pooled_po = kappa(all_a, all_b)
    result = {"n_texts": len(pairs), "n_items": len(ids),
              "pooled_kappa": round(pooled_k, 3),
              "pooled_pct_agree": round(pooled_po * 100, 1),
              "per_item": per_item, "threshold": 0.70,
              "items_below_threshold": [c for c, v in per_item.items() if v["kappa"] < 0.70]}
    dst = ROOT / "results/qual2_kappa.json"
    dst.write_text(json.dumps(result, indent=2) + "\n")
    print(f"done -> {out_path} | kappa -> {dst}")
    print(f"POOLED kappa = {result['pooled_kappa']} (agree {result['pooled_pct_agree']}%)")
    for cid in ids:
        v = per_item[cid]
        flag = "LOW" if v["kappa"] < 0.70 else "ok"
        print(f"  {cid:22s} k={v['kappa']:+.3f} agree={v['pct_agree']:5.1f}% [{flag}]")


if __name__ == "__main__":
    main()
