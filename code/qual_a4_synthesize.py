#!/usr/bin/env python3
"""Amendment A4 — axial coding / synthesis with the Llama-3.3-70B adjudicator.

Inputs: runs/logs/qual_codes_wave1.jsonl (two blinded coders) + sample metadata.
Steps:
  1. Local reliability: per-run code-name agreement between the two coders.
  2. Adjudicator call 1: merge the union of codes into themes/subthemes.
  3. Adjudicator call 2: answer RQ1-RQ4 given themes + group-aggregated observations
     (blinding lifted ONLY here, at synthesis, per A4 sec 2).
Outputs: results/qual_themes.json + results/QUALITATIVE-A4.md
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import judge_v2 as jv  # noqa: E402

ADJUDICATOR_FAMILY = "meta"
MAX_TOKENS = 4096


def load_codes():
    recs = [json.loads(l) for l in open(ROOT / "runs/logs/qual_codes_wave1.jsonl") if l.strip()]
    ok = {}
    for r in recs:
        if r.get("codes"):
            ok.setdefault(r["runId"], {})[r["coder_family"]] = r
    return ok


def reliability(ok):
    """Token overlap of lower-cased code names per run + overall Jaccard."""
    per_run, all_a, all_b = [], set(), set()
    for runId, by_coder in ok.items():
        if len(by_coder) < 2:
            continue
        a = {c["name"].strip().lower() for c in by_coder["deepseek"]["codes"]}
        b = {c["name"].strip().lower() for c in by_coder["zhipu"]["codes"]}
        per_run.append(len(a & b) / max(1, len(a | b)))
        all_a |= a
        all_b |= b
    return {
        "n_runs_coded_by_both": len(per_run),
        "mean_jaccard_code_names": round(sum(per_run) / len(per_run), 3) if per_run else None,
        "union_deepseek": len(all_a), "union_zhipu": len(all_b),
        "union_both": len(all_a | all_b),
        "exact_name_jaccard_overall": round(len(all_a & all_b) / len(all_a | all_b), 3),
        "note": ("open coding uses free wording; semantic overlap is adjudicated "
                 "qualitatively — lexical Jaccard is a floor, not the reliability metric"),
    }


def call_adjudicator(prompt):
    adj = [j for j in jv.judges if j["family"] == ADJUDICATOR_FAMILY][0]
    import urllib.request
    payload = {"model": adj["model"], "messages": [{"role": "user", "content": prompt}],
               "temperature": 0, "max_tokens": MAX_TOKENS}
    payload.update(adj.get("extra_params", {}))
    req = urllib.request.Request(
        adj["endpoint"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {jv.KEYS[adj['env_key']]}",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-qual/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def extract_json(text):
    import re
    t = re.sub(r"```(?:json)?", "", text).strip()
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
                    break
    return None


def main():
    ok = load_codes()
    sample = {r["runId"]: r for r in json.load(open(ROOT / "runs/qual/sample_wave1.json"))["runs"]}
    rel = reliability(ok)

    # ---- union code list for the adjudicator (names + definitions, deduped loosely)
    union = {}
    for runId, by_coder in ok.items():
        for coder, rec in by_coder.items():
            for c in rec["codes"]:
                key = c["name"].strip().lower()
                union.setdefault(key, {"name": c["name"], "definitions": [], "coder_count": {}})
                union[key]["definitions"].append(c.get("definition", "")[:160])
                union[key]["coder_count"][coder] = union[key]["coder_count"].get(coder, 0) + 1
    code_lines = []
    for k, v in sorted(union.items(), key=lambda kv: -sum(kv[1]["coder_count"].values())):
        n_ds = sum(1 for cc in v["coder_count"])
        n_runs = sum(v["coder_count"].values())
        code_lines.append(f"- \"{v['name']}\" [coders:{n_ds}, mentions:{n_runs}] :: "
                          + " | ".join(sorted(set(v["definitions"]))[:2]))
    code_list = "\n".join(code_lines)

    # ---- group-aggregated blinded observations (reasoning/structure/notable)
    group_notes = {}
    for runId, by_coder in ok.items():
        g = sample[runId]["group"]
        for coder, rec in by_coder.items():
            for fld in ("reasoning_style", "structure_notes", "notable"):
                v = (rec.get(fld) or "").strip()
                if v and v.lower() != "none":
                    group_notes.setdefault(g, []).append(f"[{coder}/{runId}] {fld}: {v[:300]}")
    obs_block = "\n\n".join(
        f"### Group {g} (n={len(v)} observations)\n" + "\n".join(v[:40])
        for g, v in sorted(group_notes.items()))

    prompt_themes = f"""You are the adjudicator in a qualitative study using grounded-theory \
thematic analysis. Two independent blinded coders open-coded 30 AI-generated business \
answers. Below is the union of their codes (name, how many coders produced it, mentions, \
definitions). Merge them into 5-9 THEMES, each with 2-4 SUBTHEMES. Rules: themes must be \
grounded in the codes given (no outside invention); prefer meaning over wording; note any \
codes you could not place ("residual_codes"). Return ONLY JSON:
{{"themes": [{{"name": "...", "definition": "...", "subthemes": [{{"name": "...", \
"definition": "...", "member_codes": ["..."]}}]}}], "residual_codes": ["..."]}}

=== UNION OF CODES ===
{code_list}"""

    print("calling adjudicator: theme synthesis ...")
    themes_raw = call_adjudicator(prompt_themes)
    themes = extract_json(themes_raw) or {"error": "unparsed", "raw": themes_raw[:2000]}

    prompt_rqs = f"""You are the adjudicator answering the study's research questions. \
The experiment (now revealed): AI model families (claude/gemini/gpt/kimi/qwen) answered \
business problems under conditions C=cheap_sibling team vs F=frontier single, \
S=simple vs T=team structure, N=no persona vs P=persona loaded. Quantitative findings: \
team structure helps cheap_sibling teams more than frontier singles overall (d=-0.23); \
strong for kimi/claude, absent for gpt; personas RAISE Novelty (+0.15) but CUT \
Usefulness (-1.02) and Elaboration (-0.97).

Sampled groups: W1a = top-scoring cheap-team+persona winners (CTP); W1b = top-scoring \
frontier-solo-no-persona baseline (FSN); W1c = gpt/gemini cheap-team+persona runs at the \
family median (CTP, "non-responders").

Answer RQ1-RQ4 strictly from the qualitative material below. Cite group labels and quote \
patterns. Flag uncertainty honestly.

RQ1 Why do persona-loaded cheap teams beat frontier singles on some problems/families?
RQ2 What do winning persona-team outputs do differently (wording/structure/reasoning)?
RQ3 Why is the structure effect strong for kimi/claude but absent for gpt/gemini?
RQ4 Why do personas raise Novelty but cut Usefulness/Elaboration?

Return ONLY JSON: {{"RQ1": "...", "RQ2": "...", "RQ3": "...", "RQ4": "...", \
"confidence": {{"RQ1": "high|medium|low", ...}}}}

=== THEMES (from synthesis) ===
{json.dumps(themes, ensure_ascii=False)[:6000]}

=== BLINDED OBSERVATIONS BY GROUP ===
{obs_block[:14000]}"""

    print("calling adjudicator: RQ synthesis ...")
    rq_raw = call_adjudicator(prompt_rqs)
    rqs = extract_json(rq_raw) or {"error": "unparsed", "raw": rq_raw[:2000]}

    out = {"amendment": "A4", "wave": 1, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "adjudicator": "meta/Llama-3.3-70B", "reliability": rel,
           "n_union_codes": len(union), "themes": themes, "rq_answers": rqs}
    dst = ROOT / "results/qual_themes.json"
    dst.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"saved -> {dst}")

    # ---- markdown report
    md = ["# A4 Qualitative Analysis — Wave 1 (EXPLORATORY)",
          "",
          f"Adjudicator: Llama-3.3-70B | Coders: deepseek-v4-flash + GLM-5.2 (blinded, temp 0)",
          f"Sample: 30 runs (W1a CTP winners 10, W1b FSN baseline 10, W1c gpt/gemini CTP median 10)",
          "",
          "## Reliability (lexical floor)",
          "",
          f"- Runs coded by both: {rel['n_runs_coded_by_both']}",
          f"- Mean per-run Jaccard of code names: {rel['mean_jaccard_code_names']}",
          f"- Overall exact-name Jaccard: {rel['exact_name_jaccard_overall']} "
          f"(deepseek {rel['union_deepseek']} / zhipu {rel['union_zhipu']} / union {rel['union_both']})",
          f"- Note: {rel['note']}",
          "",
          "## Themes (axial synthesis)", ""]
    for t in (themes.get("themes") or []):
        md.append(f"### {t['name']}")
        md.append(f"*{t.get('definition', '')}*")
        for st in t.get("subthemes", []):
            md.append(f"- **{st['name']}** — {st.get('definition', '')} "
                      f"(codes: {', '.join(st.get('member_codes', [])[:8])})")
        md.append("")
    if themes.get("residual_codes"):
        md.append("Residual (unplaced) codes: " + ", ".join(themes["residual_codes"]))
    md += ["", "## Answers to research questions", ""]
    for rq in ("RQ1", "RQ2", "RQ3", "RQ4"):
        conf = (rqs.get("confidence") or {}).get(rq, "?")
        md += [f"### {rq} (confidence: {conf})", "", str(rqs.get(rq, "")), ""]
    md += ["", "---",
           "EXPLORATORY: informs paper discussion only; cannot alter the interim-2 decision."]
    mdd = ROOT / "results/QUALITATIVE-A4.md"
    mdd.write_text("\n".join(md) + "\n")
    print(f"saved -> {mdd}")


if __name__ == "__main__":
    main()
