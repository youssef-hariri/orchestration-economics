#!/usr/bin/env python3
"""Amendment A4 — Wave 1 open coding (inductive, blinded, two independent coders).

Coders: deepseek (deepseek-v4-flash) and zhipu (GLM-5.2) from model_registry judges.
Blinding (A4 sec 2): coders receive ONLY the problem ("interview question") and the
output text ("transcript") — never cell labels, family, or scores.

Prompt design: NO pre-set themes. Codes, definitions and verbatim quotes must emerge
from the text (Braun & Clarke 2006 open coding).

Usage:
  python3 code/qual_a4_code.py --sample runs/qual/sample_wave1.json \
                               --out runs/logs/qual_codes_wave1.jsonl
"""
import argparse
import concurrent.futures
import json
import re
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import judge_v2 as jv  # noqa: E402  (keys, call_judge, registry)

CODER_FAMILIES = ["deepseek", "zhipu"]
MAX_TOKENS = 4096
WORKERS_PER_CODER = 8

PROMPT = """You are a qualitative researcher doing OPEN CODING of an interview transcript. \
You have NO pre-defined themes or codebook: codes must emerge from the text itself.

Context: an AI assistant was asked to solve the business problem below. Its full written \
answer is the "transcript" you must code.

=== INTERVIEW QUESTION (business problem) ===
{problem_text}

=== TRANSCRIPT (the answer to code) ===
{solution_text}

Your task:
1. Produce 8 to 20 codes that capture WHAT THIS TEXT DOES and HOW: wording choices, \
reasoning moves, framing, structure, tone, handling of uncertainty, treatment of the \
business context, and anything surprising.
2. Each code needs: "name" (2-5 words), "definition" (1 sentence), "quote" (a short \
VERBATIM excerpt from the transcript proving the code).
3. Then "reasoning_style": 1-2 sentences on how the text reasons (e.g. deductive, \
case-based, exploratory).
4. Then "structure_notes": 1-2 sentences on how the text is organized.
5. Then "notable": anything unexpected or distinctive about this transcript, or "none".

Rules: quotes must be copied exactly from the transcript; do not invent categories from \
outside knowledge; do not judge quality or give scores.

Return ONLY valid JSON with this exact shape:
{{"codes": [{{"name": "...", "definition": "...", "quote": "..."}}], \
"reasoning_style": "...", "structure_notes": "...", "notable": "..."}}"""


def extract_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.MULTILINE).strip()
    start, depth = t.find("{"), 0
    if start < 0:
        return None
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sample = json.load(open(ROOT / args.sample))["runs"]
    coders = [j for j in jv.judges if j["family"] in CODER_FAMILIES]
    assert len(coders) == len(CODER_FAMILIES), "coder registry mismatch"

    out_path = ROOT / args.out
    done = set()
    if out_path.exists():
        for line in open(out_path):
            if line.strip():
                j = json.loads(line)
                if not j.get("error") and j.get("codes"):
                    done.add((j["runId"], j["coder_family"]))

    tasks = []
    for run in sample:
        prompt = PROMPT.replace("{problem_text}", run["problem_text"]) \
                       .replace("{solution_text}", run["fulltext"])
        for coder in coders:
            if (run["runId"], coder["family"]) not in done:
                tasks.append((run, coder, prompt))

    total = len(sample) * len(coders)
    print(f"qual_a4_code: wave {json.load(open(ROOT / args.sample)).get('wave')} | "
          f"{len(sample)} runs x {len(coders)} coders; {len(tasks)} pending, "
          f"{len(done)} done; max_tokens={MAX_TOKENS}")

    write_lock = threading.Lock()
    counter = {"n": len(done)}
    sems = {c["family"]: threading.Semaphore(WORKERS_PER_CODER) for c in coders}

    def run_task(task, out):
        run, coder, prompt = task
        with sems[coder["family"]]:
            rec = None
            for attempt in range(3):
                try:
                    payload_override = {"max_tokens": MAX_TOKENS, "temperature": 0}
                    text, usage, resolved = _call(coder, prompt, payload_override)
                    parsed = extract_json(text)
                    rec = {
                        "runId": run["runId"], "problemId": run["problemId"],
                        "coder_family": coder["family"], "coder_model": coder["model"],
                        "coder_model_resolved": resolved,
                        "codes": (parsed or {}).get("codes") if parsed else None,
                        "reasoning_style": (parsed or {}).get("reasoning_style") if parsed else None,
                        "structure_notes": (parsed or {}).get("structure_notes") if parsed else None,
                        "notable": (parsed or {}).get("notable") if parsed else None,
                        "raw": text, "usage": usage, "attempt": attempt,
                        "harness": "qual_a4/A4",
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                    if rec["codes"]:
                        break
                except Exception as e:  # noqa: BLE001
                    rec = {"runId": run["runId"], "coder_family": coder["family"],
                           "error": str(e)[:300], "harness": "qual_a4/A4",
                           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    time.sleep(2 ** attempt * 2)
        with write_lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            counter["n"] += 1
            print(f"[{counter['n']}/{total}] {run['runId']} {coder['family']}: "
                  f"{len(rec.get('codes') or [])} codes" if rec.get('codes') else
                  f"[{counter['n']}/{total}] {run['runId']} {coder['family']}: "
                  f"{rec.get('error', 'UNPARSED')}")

    with open(out_path, "a") as out:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=WORKERS_PER_CODER * len(coders)) as pool:
            futs = [pool.submit(run_task, t, out) for t in tasks]
            for f in concurrent.futures.as_completed(futs):
                f.result()
    print(f"done -> {out_path}")


def _call(coder, prompt, overrides):
    """call_judge with A4 overrides (max_tokens 4096, temperature 0)."""
    import urllib.request
    payload = {
        "model": coder["model"],
        "messages": [{"role": "user", "content": prompt}],
    }
    payload.update(coder.get("extra_params", {}))
    payload.update(overrides)
    req = urllib.request.Request(
        coder["endpoint"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {jv.KEYS[coder['env_key']]}",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-qual/1.0"},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
            return (data["choices"][0]["message"]["content"],
                    data.get("usage", {}), data.get("model", coder["model"]))
        except Exception:
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError("unreachable")


if __name__ == "__main__":
    main()
