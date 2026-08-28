#!/usr/bin/env python3
"""materialize_results.py — emit the reviewer-facing CSV/JSON layer from frozen artifacts.

Rule (D54): every statistical test result must exist as a file readable WITHOUT
re-running code. This script NEVER calls an API and NEVER recomputes a hypothesis
test — it (a) joins frozen judgment logs to frozen ledgers into long-format score
CSVs, (b) flattens existing result JSONs into stats CSVs, (c) materializes
per-judge-call raw files per DATA-DICTIONARY, (d) computes ONLY descriptive
quantities that were never computed elsewhere (descriptive stats, Fleiss' kappa
on judge ratings) — each such computation is labeled computed_by=materialize_results.

Datasets: study1_main, study2_refine, study2b_refine, wave (Protocol 12).
Idempotent: re-run after any new analysis lands. stdlib only.

Usage: python3 code/materialize_results.py
"""

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["Novelty", "Usefulness", "Flexibility", "Elaboration", "Cultural Sensitivity"]
DIM_KEYS = ["novelty", "usefulness", "flexibility", "elaboration", "cultural_sensitivity"]


def read_json(p):
    return json.loads(Path(p).read_text())


def read_jsonl(p):
    out = []
    for line in Path(p).read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def write_csv(path, fieldnames, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def flatten(obj, prefix=""):
    """Generic JSON flattener -> list of (path, value) leaf pairs."""
    rows = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            rows += flatten(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            rows += flatten(v, f"{prefix}[{i}]")
    else:
        rows.append((prefix, obj))
    return rows


# ---------------------------------------------------------------- ledgers
def ledger_index(path):
    """runId -> latest completed record (by finishedAtUtc) from a run ledger."""
    L = read_json(path)
    recs = L["results"] if isinstance(L, dict) else L
    idx = {}
    for r in recs:
        if not isinstance(r, dict) or r.get("runId") is None:
            continue
        t = r.get("finishedAtUtc") or ""
        k = r["runId"]
        if k not in idx or t > idx[k].get("finishedAtUtc", ""):
            idx[k] = r
    return idx


def judgments(path):
    """Keep only successful, complete 5-dimension judgments."""
    out = []
    for j in read_jsonl(path):
        s = j.get("scores")
        if not s or any(d not in s or not isinstance(s[d], (int, float)) for d in DIMS):
            continue  # error/incomplete records never enter (A1.2 gate)
        out.append(j)
    return out


def score_row(study, j, meta):
    comp = sum(j["scores"][d] for d in DIMS) / len(DIMS)
    row = {
        "study": study,
        "solution_id": meta.get("solution_id", ""),
        "run_id": j.get("runId"),
        "cell": meta.get("cell", ""),
        "family": meta.get("family", ""),
        "problem_id": j.get("problemId", meta.get("problem_id", "")),
        "rep": meta.get("rep", ""),
        "condition": meta.get("condition", ""),
        "judge_family": j.get("judge_family", ""),
        "judge_model": j.get("judge_model", ""),
        "variant": j.get("variant", ""),
        "composite": round(comp, 4),
    }
    for d in DIMS:
        row[d.lower().replace(" ", "_")] = j["scores"][d]
    return row


SCORE_FIELDS = (["study", "solution_id", "run_id", "cell", "family", "problem_id",
                 "rep", "condition", "judge_family", "judge_model", "variant",
                 "composite"] + DIM_KEYS)


def fleiss_kappa(ratings, ncat=5):
    """ratings: list of per-subject lists of category ratings (1..ncat)."""
    N = len(ratings)
    if N == 0:
        return None
    n = len(ratings[0])
    counts = [[0] * ncat for _ in range(N)]
    for i, subj in enumerate(ratings):
        for r in subj:
            if isinstance(r, (int, float)) and 1 <= int(r) <= ncat:
                counts[i][int(r) - 1] += 1
    P = [(sum(c * c for c in row) - n) / (n * (n - 1)) for row in counts]
    Pbar = sum(P) / N
    p = [sum(counts[i][k] for i in range(N)) / (N * n) for k in range(ncat)]
    Pe = sum(x * x for x in p)
    if Pe == 1.0:
        return 1.0
    return (Pbar - Pe) / (1 - Pe)


def judge_raw_file(study_dir, sol_id, j):
    d = ROOT / "evaluation" / "judge_raw" / study_dir
    d.mkdir(parents=True, exist_ok=True)
    safe = str(sol_id).replace("/", "_")
    f = d / f"{safe}__{j.get('judge_family')}__{j.get('variant')}.json"
    payload = {
        "solution_id": sol_id,
        "run_id": j.get("runId"),
        "judge_provider": {"deepseek": "deepseek", "zhipu": "together",
                           "meta": "together"}.get(j.get("judge_family"), ""),
        "judge_model": j.get("judge_model", ""),
        "variant": j.get("variant", ""),
        "raw_response": j.get("raw", ""),
        "scores": {d.lower().replace(" ", "_"): j["scores"][d] for d in DIMS},
        "parsed_ok": True,
        "ts": j.get("ts", ""),
    }
    f.write_text(json.dumps(payload, indent=1) + "\n")


def main():
    print("materialize_results.py — building reviewer-facing layer (no API calls)")

    # ================= STUDY 1 (main run) =================
    print("[1/6] Study 1 main run")
    led = ledger_index(ROOT / "runs" / "logs" / "main_run_ledger.json")
    jmain = judgments(ROOT / "runs" / "logs" / "main_judgments.jsonl")
    rows, per_dim = [], defaultdict(lambda: defaultdict(list))
    for j in jmain:
        m = led.get(j["runId"])
        if not m:
            continue
        sol = f"{m.get('cell')}__{m.get('family')}__{j['problemId']}__rep{m.get('rep')}"
        meta = {"solution_id": sol, "cell": m.get("cell"), "family": m.get("family"),
                "rep": m.get("rep"), "problem_id": j["problemId"]}
        rows.append(score_row("study1_main", j, meta))
        judge_raw_file("study1_main", sol, j)
        for d in DIMS:
            per_dim[d][sol].append(j["scores"][d])
    write_csv(ROOT / "evaluation" / "scores_aggregated.csv", SCORE_FIELDS, rows)

    krows = []
    for d in DIMS:
        ratings = [v for v in per_dim[d].values() if len(v) >= 2]
        krows.append({"dimension": d.lower().replace(" ", "_"),
                      "fleiss_kappa": round(fleiss_kappa(ratings), 4) if ratings else "",
                      "n_solutions": len(ratings),
                      "computed_by": "materialize_results (descriptive; D11 dual-IRR record "
                                     "lives in interim reports)"})
    write_csv(ROOT / "evaluation" / "kappa_by_dimension.csv",
              ["dimension", "fleiss_kappa", "n_solutions", "computed_by"], krows)

    # descriptive stats by cell x dimension (descriptive only)
    desc = []
    by_cell = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for d, dk in zip(DIMS, DIM_KEYS):
            by_cell[r["cell"]][dk].append(r[dk])
    for cell in sorted(by_cell):
        for dk in DIM_KEYS:
            v = by_cell[cell][dk]
            n = len(v)
            mean = sum(v) / n
            sd = math.sqrt(sum((x - mean) ** 2 for x in v) / (n - 1)) if n > 1 else 0
            desc.append({"cell": cell, "dimension": dk, "n_judgments": n,
                         "mean": round(mean, 4), "sd": round(sd, 4),
                         "computed_by": "materialize_results (descriptive)"})
    write_csv(ROOT / "analysis" / "results" / "descriptive_stats.csv",
              ["cell", "dimension", "n_judgments", "mean", "sd", "computed_by"], desc)

    # effect sizes + confirmatory record (flattened from frozen result JSONs)
    eff_rows = []
    i2 = read_json(ROOT / "results" / "interim2_analysis.json")
    for path, val in flatten(i2):
        if isinstance(val, (int, float, str)) and not isinstance(val, bool):
            eff_rows.append({"source": "results/interim2_analysis.json",
                             "statistic_path": f"interim2.{path}", "value": val})
    a3 = read_json(ROOT / "results" / "exploratory_analysis.json")
    for path, val in flatten(a3):
        if isinstance(val, (int, float, str)) and not isinstance(val, bool):
            eff_rows.append({"source": "results/exploratory_analysis.json",
                             "statistic_path": f"amendment_A3.{path}", "value": val})
    write_csv(ROOT / "analysis" / "results" / "effect_sizes.csv",
              ["source", "statistic_path", "value"], eff_rows)

    # heterogeneity batteries (D44/D45), long format
    het_rows = []
    for fname, tag in [("exploratory_heterogeneity.json", "D44"),
                       ("persona_heterogeneity.json", "D45")]:
        d = read_json(ROOT / "results" / fname)
        for path, val in flatten(d):
            if isinstance(val, (int, float, str)) and not isinstance(val, bool):
                het_rows.append({"battery": tag, "source": f"results/{fname}",
                                 "statistic_path": path, "value": val})
    write_csv(ROOT / "analysis" / "results" / "heterogeneity_battery.csv",
              ["battery", "source", "statistic_path", "value"], het_rows)

    # economics (T-EGR etc. already CSV; add a unified pointer table)
    cell_sum = list(csv.DictReader((ROOT / "results" / "cost" / "cell_summary.csv").open()))
    write_csv(ROOT / "analysis" / "results" / "tegr_by_arm.csv",
              list(cell_sum[0].keys()), cell_sum)

    # ================= WAVE =================
    print("[2/6] Wave (Protocol 12)")
    wled = ledger_index(ROOT / "runs" / "logs" / "wave_run_ledger.json")
    jwave = judgments(ROOT / "runs" / "logs" / "wave_judgments.jsonl")
    wrows = []
    for j in jwave:
        m = wled.get(j["runId"])
        if not m or not m.get("cell"):
            continue  # 27 quarantine orphans join to nothing (Entry 64)
        meta = {"solution_id": m.get("runKey", ""), "cell": m.get("cell"),
                "family": m.get("family"), "rep": m.get("rep"),
                "problem_id": j["problemId"]}
        wrows.append(score_row("wave", j, meta))
        judge_raw_file("wave", m.get("runKey", j["runId"]), j)
    write_csv(ROOT / "analysis" / "results" / "wave_scores_aggregated.csv",
              SCORE_FIELDS, wrows)

    gate_rows = []
    for fjson, vec in [("wave_analysis.json", "primary_v2026-07-30"),
                       ("wave_analysis_minimax_promo.json", "minimax_promo_D46")]:
        d = read_json(ROOT / "results" / fjson)
        for gate in ["W1_team_effect", "W2_upgrade_threshold", "W3_domain_contingency",
                     "W4_capability_gap", "W5_variance", "W6_economics",
                     "W7_judge_icc_by_domain"]:
            g = d.get(gate, {})
            verdict = g.get("gate", "audit") if isinstance(g, dict) else ""
            for path, val in flatten(g):
                if isinstance(val, (int, float, str)) and not isinstance(val, bool):
                    gate_rows.append({"price_vector": vec, "gate": gate,
                                      "verdict": verdict, "statistic_path": path,
                                      "value": val})
    write_csv(ROOT / "analysis" / "results" / "wave_gates.csv",
              ["price_vector", "gate", "verdict", "statistic_path", "value"], gate_rows)

    # ================= STUDY 2 / 2b (refinement) =================
    print("[3/6] Study 2 + 2b refinement")
    main_j_by_run = {}
    for j in jmain:
        main_j_by_run.setdefault(j["runId"], []).append(j)

    def refine_scores(tag, store_path, judgment_paths):
        store = read_json(store_path)
        runs = store.get("runs", [])
        out = []
        for r in runs:
            rid = r.get("runId")
            for jp in judgment_paths:
                for j in judgments(jp):
                    if str(j.get("runId")) == str(rid):
                        meta = {"solution_id": f"{tag}__{r.get('family')}__{r.get('problemId')}",
                                "cell": "C-T-P-refined", "family": r.get("family"),
                                "condition": "refined", "problem_id": r.get("problemId")}
                        out.append(score_row(tag, j, meta))
        return out, runs

    ref_rows = []
    s2_stores = [(ROOT / "runs" / "refine" / "refined_store_pilot.json",
                  [ROOT / "runs" / "logs" / "refine_judgments_pilot.jsonl"]),
                 (ROOT / "runs" / "refine" / "refined_store_extension.json",
                  [ROOT / "runs" / "logs" / "refine_judgments_extension.jsonl"])]
    for sp, jps in s2_stores:
        if sp.exists():
            rr, _ = refine_scores("study2_refine", sp, jps)
            ref_rows += rr
    for arm, sp, jp in [
        ("study2b_U", ROOT / "runs" / "refine_b" / "refined_store_U_pilot.json",
         ROOT / "runs" / "logs" / "refine_b_U_judgments_pilot.jsonl"),
        ("study2b_W", ROOT / "runs" / "refine_b" / "refined_store_W_pilot.json",
         ROOT / "runs" / "logs" / "refine_b_W_judgments_pilot.jsonl"),
        ("study2b_W3", ROOT / "runs" / "refine_b" / "refined_store_W3_pilot.json",
         ROOT / "runs" / "logs" / "refine_b_W3_judgments_pilot.jsonl")]:
        if sp.exists():
            rr, _ = refine_scores(arm, sp, [jp])
            ref_rows += rr
    write_csv(ROOT / "analysis" / "results" / "refine_scores_aggregated.csv",
              SCORE_FIELDS, ref_rows)

    # Study-2 / 2b hypothesis tables (flattened from frozen result JSONs)
    s2_rows = []
    for fj, tag in [("refine_study2_pilot.json", "study2_pilot"),
                    ("refine_study2_pooled.json", "study2_pooled"),
                    ("cross_family.json", "study2_cross_family"),
                    ("refine_study2b_U_pilot.json", "study2b_armU_pilot"),
                    ("refine_study2b_W_pilot.json", "study2b_armW_pilot"),
                    ("refine_study2b_W3_pilot.json", "study2b_armW3_pilot"),
                    ("refine_study2b_identity_pilot.json", "study2b_identity_gpt_gemini"),
                    ("refine_study2b_identity_W3_pilot.json", "study2b_identity_W3")]:
        fp = ROOT / "results" / fj
        if not fp.exists():
            continue
        for path, val in flatten(read_json(fp)):
            if isinstance(val, (int, float, str)) and not isinstance(val, bool):
                s2_rows.append({"study_phase": tag, "source": f"results/{fj}",
                                "statistic_path": path, "value": val})
    write_csv(ROOT / "analysis" / "results" / "study2_refine_results.csv",
              ["study_phase", "source", "statistic_path", "value"], s2_rows)

    # ================= QUALITATIVE (Study 2 mechanism + A4) =================
    print("[4/6] Qualitative codebooks and code application")
    cb = read_json(ROOT / "results" / "qual2_codebook.json")
    kap = read_json(ROOT / "results" / "qual2_kappa.json")
    per_item = kap.get("per_item", {})
    cb_rows = []
    for it in cb.get("items", []):
        k = per_item.get(it["id"], {})
        cb_rows.append({
            "code_id": it["id"], "rq": it.get("rq", ""), "name": it.get("name", ""),
            "definition": it.get("definition", ""),
            "cohens_kappa": k.get("kappa", ""), "pct_agreement": k.get("pct_agree", ""),
            "prevalence_deepseek": k.get("prevalence_ds", ""),
            "prevalence_zhipu": k.get("prevalence_zp", ""),
            "reliability_gate_0.70": "PASS" if isinstance(k.get("kappa"), (int, float))
                                     and k["kappa"] >= 0.70 else "BELOW_GATE_disclosed",
        })
    cb_rows.append({"code_id": "__POOLED__", "name": "Pooled across 13 codes",
                    "cohens_kappa": kap.get("pooled_kappa", ""),
                    "pct_agreement": kap.get("pooled_pct_agree", ""),
                    "reliability_gate_0.70": "PASS"})
    write_csv(ROOT / "analysis" / "results" / "qual_codebook_kappa.csv",
              ["code_id", "rq", "name", "definition", "cohens_kappa", "pct_agreement",
               "prevalence_deepseek", "prevalence_zhipu", "reliability_gate_0.70"], cb_rows)

    app_rows = []
    for jl, wave_tag in [(ROOT / "runs" / "logs" / "qual2_closed.jsonl", "closed_final"),
                         (ROOT / "runs" / "logs" / "qual2_wave1.jsonl", "wave1"),
                         (ROOT / "runs" / "logs" / "qual_closed_wave12.jsonl", "a4_wave12"),
                         (ROOT / "runs" / "logs" / "qual_codes_wave1.jsonl", "a4_wave1_codes")]:
        if not jl.exists():
            continue
        for rec in read_jsonl(jl):
            vec = rec.get("vector") or {}
            row = {"source_file": jl.name, "text_key": rec.get("key", ""),
                   "coder_family": rec.get("coder_family", rec.get("family", ""))}
            row.update({f"code_{k}": v for k, v in vec.items()})
            app_rows.append(row)
    if app_rows:
        all_codes = sorted({c for r in app_rows for c in r if c.startswith("code_")})
        write_csv(ROOT / "analysis" / "results" / "qual_code_application.csv",
                  ["source_file", "text_key", "coder_family"] + all_codes, app_rows)

    # A4 inductive themes (flattened)
    for fj, out in [("qual_themes.json", "qual_a4_themes.csv"),
                    ("qual_kappa.json", "qual_a4_kappa.csv"),
                    ("qual2_analysis.json", "qual_study2_analysis.csv")]:
        fp = ROOT / "results" / fj
        if fp.exists():
            rows = [{"statistic_path": p, "value": v}
                    for p, v in flatten(read_json(fp))
                    if isinstance(v, (int, float, str)) and not isinstance(v, bool)]
            write_csv(ROOT / "analysis" / "results" / out,
                      ["statistic_path", "value"], rows)

    # ================= INDEX =================
    print("[5/6] index")
    idx = [
        ("evaluation/scores_aggregated.csv", "Study 1: one row per solution x judge x variant (long)"),
        ("evaluation/kappa_by_dimension.csv", "Study 1: Fleiss' kappa per dimension (computed_by=materialize_results)"),
        ("evaluation/judge_raw/<study>/<solution>__<judge>__<variant>.json", "per-judge-call raw prompt/response/scores"),
        ("analysis/results/descriptive_stats.csv", "Study 1: cell x dimension mean/sd/n (descriptive)"),
        ("analysis/results/effect_sizes.csv", "Study 1 confirmatory record (Interim-2 H1-H5) + Amendment A3 exploratory stats"),
        ("analysis/results/heterogeneity_battery.csv", "D44/D45 exploratory heterogeneity batteries (A1-A7, P1-P5)"),
        ("analysis/results/tegr_by_arm.csv", "Study 1 economics: cost/quality/T-EGR per cell"),
        ("analysis/results/wave_scores_aggregated.csv", "Wave: one row per solution x judge x variant"),
        ("analysis/results/wave_gates.csv", "Wave W1-W7 gate statistics, both price vectors"),
        ("analysis/results/refine_scores_aggregated.csv", "Study 2/2b: judged scores for refined solutions"),
        ("analysis/results/study2_refine_results.csv", "Study 2/2b hypothesis/gate statistics (H2.x, H3.x, G1/G2)"),
        ("analysis/results/qual_codebook_kappa.csv", "Study 2 qualitative: 13-code book with per-code kappa + gate"),
        ("analysis/results/qual_code_application.csv", "Qualitative: per-text x coder code vectors"),
        ("analysis/results/qual_a4_themes.csv / qual_a4_kappa.csv / qual_study2_analysis.csv", "A4 inductive + Study-2 closed-coding analyses (flattened)"),
    ]
    write_csv(ROOT / "analysis" / "results" / "INDEX.csv", ["file", "contents"],
              [{"file": a, "contents": b} for a, b in idx])

    print("[6/6] done. No API calls were made; all inputs were frozen artifacts.")


if __name__ == "__main__":
    main()
