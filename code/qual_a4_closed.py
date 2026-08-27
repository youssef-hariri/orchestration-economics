#!/usr/bin/env python3
"""Amendment A4.6 — closed re-coding pass for Cohen's kappa.

Freezes a 12-item codebook derived from the A4 synthesis (4 process themes + key
discourse codes observed in Waves 1-2), then both coders (deepseek, zhipu) independently
judge presence/absence on all 50 transcripts (Waves 1+2). Computes per-item and pooled
Cohen's kappa + percent agreement. Temperature 0, blinded (no cell/family/score).

Outputs: runs/logs/qual_closed_wave12.jsonl, results/qual_kappa.json
"""
import concurrent.futures
import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import judge_v2 as jv  # noqa: E402

CODER_FAMILIES = ["deepseek", "zhipu"]
MAX_TOKENS = 2048
WORKERS_PER_CODER = 8

# Analyst-frozen codebook (A4.6), grounded in observed codes from Waves 1-2.
CODEBOOK = [
    {"id": "deductive_framework", "name": "Deductive framework",
     "definition": "The answer builds an explicit named framework or dimension set and derives its recommendations from it."},
    {"id": "conditional_logic", "name": "Conditional logic",
     "definition": "Recommendations are expressed as if/then contingencies, decision rules, or contrasting cases."},
    {"id": "inductive_exploratory", "name": "Inductive / exploratory reasoning",
     "definition": "The text reasons from examples or observations toward principles, or visibly explores options rather than prescribing."},
    {"id": "metaphor", "name": "Metaphorical framing",
     "definition": "A metaphor or analogy is used to frame the problem or solution."},
    {"id": "reflective_opening", "name": "Philosophical / reflective opening",
     "definition": "The answer opens with reflective, philosophical, or reframing language rather than jumping to recommendations."},
    {"id": "rhetorical_questions", "name": "Rhetorical questioning",
     "definition": "Questions are used deliberately to structure or advance the argument."},
    {"id": "cultural_contextualization", "name": "Cultural contextualization",
     "definition": "Recommendations are adapted to specific cultural or local contexts (practices, vocabulary, feedback styles, norms)."},
    {"id": "global_local_balance", "name": "Global-local balance",
     "definition": "The text explicitly balances global consistency against local adaptation."},
    {"id": "collaborative_framing", "name": "Collaborative framing",
     "definition": "Actions are framed as co-creation, teamwork, or empowerment rather than top-down directive."},
    {"id": "staged_implementation", "name": "Staged implementation",
     "definition": "Phased rollout, pilots, gates, or stop rules structure the implementation plan."},
    {"id": "risk_quantification", "name": "Risk quantification",
     "definition": "Risks are explicitly classified, quantified, or placed in mitigation tables."},
    {"id": "authority_citation", "name": "External authority citation",
     "definition": "External authorities, named best practices, or known frameworks are cited by name."},
]

PROMPT = """You are a reliability coder applying a FIXED codebook. Read the transcript \
(an AI assistant's answer to a business problem) and decide, for EACH codebook item, \
whether it is clearly PRESENT (1) or ABSENT (0) in the transcript. Code conservatively: \
if unsure, code 0. Do not judge quality.

=== INTERVIEW QUESTION (business problem) ===
{problem_text}

=== TRANSCRIPT ===
{solution_text}

=== CODEBOOK ===
{codebook}

Return ONLY valid JSON: {{"items": [{{"id": "<codebook id>", "present": 0 or 1}}, ...]}} \
with one entry per codebook item, in order."""


def extract_json(text):
    import re
    t = re.sub(r"```(?:json)?", "", text.strip()).strip()
    start, depth = t.find("{"), 0
    for i in range(start, len(t)):
        if t[i] == "{":
            depth += 1
        elif t[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(t[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def call(coder, prompt):
    payload = {"model": coder["model"], "messages": [{"role": "user", "content": prompt}],
               "temperature": 0, "max_tokens": MAX_TOKENS}
    payload.update(coder.get("extra_params", {}))
    req = urllib.request.Request(
        coder["endpoint"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {jv.KEYS[coder['env_key']]}",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-qual/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"], data.get("usage", {})
        except Exception:
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise


def main():
    runs = (json.load(open(ROOT / "runs/qual/sample_wave1.json"))["runs"]
            + json.load(open(ROOT / "runs/qual/sample_wave2.json"))["runs"])
    coders = [j for j in jv.judges if j["family"] in CODER_FAMILIES]
    codebook_text = "\n".join(f"- id={c['id']} | {c['name']}: {c['definition']}" for c in CODEBOOK)
    ids = [c["id"] for c in CODEBOOK]

    out_path = ROOT / "runs/logs/qual_closed_wave12.jsonl"
    done = set()
    if out_path.exists():
        for line in open(out_path):
            j = json.loads(line)
            if not j.get("error") and j.get("vector") is not None:
                done.add((j["runId"], j["coder_family"]))

    tasks = []
    for run in runs:
        prompt = (PROMPT.replace("{problem_text}", run["problem_text"])
                  .replace("{solution_text}", run["fulltext"])
                  .replace("{codebook}", codebook_text))
        for coder in coders:
            if (run["runId"], coder["family"]) not in done:
                tasks.append((run, coder, prompt))

    total = len(runs) * len(coders)
    print(f"closed re-coding: {len(runs)} transcripts x {len(coders)} coders; "
          f"{len(tasks)} pending, {len(done)} done; codebook={len(ids)} items")

    lock = threading.Lock()
    counter = {"n": len(done)}
    sems = {c["family"]: threading.Semaphore(WORKERS_PER_CODER) for c in coders}

    def run_task(task, out):
        run, coder, prompt = task
        with sems[coder["family"]]:
            rec = None
            for attempt in range(3):
                try:
                    text, usage = call(coder, prompt)
                    parsed = extract_json(text)
                    items = (parsed or {}).get("items") or []
                    vec = {i["id"]: int(i.get("present", 0)) for i in items
                           if i.get("id") in ids}
                    rec = {"runId": run["runId"], "coder_family": coder["family"],
                           "vector": vec if len(vec) == len(ids) else None,
                           "n_items": len(vec), "usage": usage, "attempt": attempt,
                           "harness": "qual_a4_closed/A4.6",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    if rec["vector"] is not None:
                        break
                except Exception as e:  # noqa: BLE001
                    rec = {"runId": run["runId"], "coder_family": coder["family"],
                           "error": str(e)[:300], "harness": "qual_a4_closed/A4.6",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    time.sleep(2 ** attempt * 2)
        with lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            counter["n"] += 1
            ok = rec.get("vector") is not None
            print(f"[{counter['n']}/{total}] {run['runId']} {coder['family']}: "
                  f"{'OK' if ok else rec.get('error', 'INCOMPLETE')}"
                  f"{' sum=' + str(sum(rec['vector'].values())) if ok else ''}")

    with open(out_path, "a") as out:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=WORKERS_PER_CODER * len(coders)) as pool:
            futs = [pool.submit(run_task, t, out) for t in tasks]
            for f in concurrent.futures.as_completed(futs):
                f.result()

    # ---- Cohen's kappa per item and pooled
    mat = {}
    for line in open(out_path):
        j = json.loads(line)
        if j.get("vector") is not None:
            mat.setdefault(j["runId"], {})[j["coder_family"]] = j["vector"]
    pairs = [r for r in mat.values() if len(r) == 2]

    def kappa(a, b):
        n = len(a)
        a11 = sum(1 for x, y in zip(a, b) if x == 1 and y == 1)
        a00 = sum(1 for x, y in zip(a, b) if x == 0 and y == 0)
        po = (a11 + a00) / n
        p1a, p1b = sum(a) / n, sum(b) / n
        pe = p1a * p1b + (1 - p1a) * (1 - p1b)
        return ((po - pe) / (1 - pe) if pe < 1 else 1.0), po

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
    result = {"n_transcripts": len(pairs), "n_items": len(ids),
              "pooled_kappa": round(pooled_k, 3),
              "pooled_pct_agree": round(pooled_po * 100, 1),
              "per_item": per_item,
              "threshold": 0.70,
              "items_below_threshold": [c for c, v in per_item.items() if v["kappa"] < 0.70]}
    dst = ROOT / "results/qual_kappa.json"
    dst.write_text(json.dumps(result, indent=2) + "\n")
    print(f"done -> {out_path} | kappa -> {dst}")
    print(f"POOLED kappa = {result['pooled_kappa']} (agree {result['pooled_pct_agree']}%)")
    for cid in ids:
        v = per_item[cid]
        flag = "LOW" if v["kappa"] < 0.70 else "ok"
        print(f"  {cid:26s} k={v['kappa']:+.3f} agree={v['pct_agree']:5.1f}% [{flag}]")


if __name__ == "__main__":
    main()
