"""Study 3 economics: cost per solution for F-S-N / D-SELF / D-FRONT per family,
plus quality delta (Cohen d on Novelty vs F-S-N) -> decision table.

Cost model (D23): tokens x config/price_vector.json. Study-3 ledger stores real
per-call usage; providers return different usage field names, so we read both
Anthropic-style (input_tokens/output_tokens) and OpenAI-style
(prompt_tokens/completion_tokens). Together-hosted Kimi-K3 is logged as
'moonshotai/Kimi-K3' and mapped to the frozen 'kimi-k3' price entry.
F-S-N runs live in the Study-1/2 main ledger, which stores only
totalTokensUsed; split approximated 15% input / 85% output (labeled in output).

Outputs: results/study3_economics.json + analysis/results/study3_economics.csv
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRICES = json.load(open(ROOT / "config/price_vector.json"))["prices"]

MODEL_ALIAS = {"moonshotai/Kimi-K3": "kimi-k3"}
FSN_SPLIT = 0.15  # input share approximation for main-ledger total tokens


def price(model):
    return PRICES[MODEL_ALIAS.get(model, model)]


def usage_in_out(u):
    if not u:
        return 0, 0
    i = u.get("input_tokens", u.get("prompt_tokens", 0)) or 0
    o = u.get("output_tokens", u.get("completion_tokens", 0)) or 0
    return i, o


def run_cost(rec):
    """Designer cost + sum of executed-step costs for one Study-3 run."""
    cost = 0.0
    di, do = usage_in_out(rec.get("designer_usage"))
    p = price(rec["designer_model"])
    cost += (di * p["input"] + do * p["output"]) / 1e6
    pex = price(rec["executor_model"])
    for s in rec.get("steps", []):
        i, o = usage_in_out(s.get("usage"))
        cost += (i * pex["input"] + o * pex["output"]) / 1e6
    return cost


def main():
    # --- Study 3 arms
    s3 = {"D-SELF": {}, "D-FRONT": {}}
    for line in open(ROOT / "runs/logs/study3_ledger_v2.jsonl"):
        d = json.loads(line)
        if d.get("status") != "completed":
            continue
        s3[d["arm"]].setdefault(d["family"], []).append(run_cost(d))

    # --- F-S-N from main ledger (frontier solo, totals only)
    reg = json.load(open(ROOT / "config/model_registry.json"))["generators"]
    fsn = {}
    for r in json.load(open(ROOT / "runs/logs/main_run_ledger.json"))["results"]:
        if r["status"] != "completed" or r["cell"] != "F-S-N":
            continue
        model = reg[r["family"]]["frontier"]["model"]
        p = price(model)
        t = r["totalTokensUsed"]
        c = (t * FSN_SPLIT * p["input"] + t * (1 - FSN_SPLIT) * p["output"]) / 1e6
        fsn.setdefault(r["family"], []).append(c)

    # --- quality deltas from the frozen Holm table
    dq = {}  # (family, arm) -> d on Novelty vs F-S-N
    with open(ROOT / "analysis/results/study3_vs_fsn_full.csv") as f:
        for row in csv.DictReader(f):
            if row.get("dimension") != "Novelty":
                continue
            dq[(row["family"], row["arm"])] = float(row["d"])

    fams = sorted(fsn)
    rows = []
    for fam in fams:
        fcost = sum(fsn[fam]) / len(fsn[fam])
        row = {"family": fam, "fsn_cost_per_sol": round(fcost, 4),
               "fsn_n": len(fsn[fam])}
        for arm, tag in (("D-SELF", "dself"), ("D-FRONT", "dfront")):
            costs = s3[arm].get(fam, [])
            c = sum(costs) / len(costs) if costs else None
            row[f"{tag}_cost"] = round(c, 4) if c is not None else None
            row[f"{tag}_n"] = len(costs)
            row[f"{tag}_d_quality"] = dq.get((fam, arm))
            row[f"cost_ratio_{tag[1:]}_vs_fsn"] = (round(c / fcost, 2)
                                                   if c is not None else None)
        rows.append(row)

    note = ("cost per completed solution, USD, frozen price vector v2026-08-23-wave; "
            "Study-3 arms use real per-call usage splits (provider usage fields "
            "normalized: input/output_tokens or prompt/completion_tokens; "
            "moonshotai/Kimi-K3 priced as kimi-k3); F-S-N tokens split approximated "
            "15% input / 85% output (main ledger stores totals only); quality = "
            "Cohen d on Novelty vs F-S-N from study3_vs_fsn_full.csv")
    out = {"note": note, "rows": rows}
    with open(ROOT / "results/study3_economics.json", "w") as f:
        json.dump(out, f, indent=2)

    with open(ROOT / "analysis/results/study3_economics.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
