#!/usr/bin/env python3
"""study3_design_run.py — Protocol 13 runner: pipeline design authorship.

Arms (executor is ALWAYS the family's pinned cheap sibling):
  D-SELF  — cheap sibling designs the pipeline for the problem, then executes it
  D-FRONT — the family's frontier designs the pipeline, cheap sibling executes it

Discipline:
- One fresh design per (arm, family, problem, rep) — design variance is data (D30 probe logic).
- Designer tokens are charged to arm cost (logged per call; D30 precedent).
- Designs validated against the schema; ONE repair retry with the validator error;
  second failure -> design FAILED, task excluded and disclosed (Protocol 13 §2).
- Append-only JSONL ledger; resume by key scan (completed + non-empty only);
  429 Retry-After honored; 5xx backoff; credit exhaustion -> family skipped, others
  continue (Protocol 12 §5.4 policy); qwen design/execute calls only inside the
  UTC 14:00-00:00 discount window (D21) unless --ignore-window (logged).
- Output store is judge_v2-compatible (runs/study3/study3_store.json) — the frozen
  judge panel scores designed-pipeline solutions unchanged.

Usage:
  python3 code/study3_design_run.py --dry-run
  python3 code/study3_design_run.py --pilot     # 4 problems (D32 draw) x 1 rep
  python3 code/study3_design_run.py             # full: 19 problems x 3 reps
  python3 code/study3_design_run.py --families kimi,qwen --reps 1
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_key(env_key):
    # Local copy of judge_v2.load_key — avoids importing judge_v2 here, whose
    # module-level KEYS would demand judge keys (DeepSeek) at generation time.
    for name in (env_key, "TOGETHER_AI_API_KEY" if env_key == "TOGETHER_API_KEY" else None):
        if name and os.environ.get(name):
            return os.environ[name]
    for env_file in (ROOT / ".env", ROOT.parent.parent / ".env"):
        if not env_file.exists():
            continue
        for line in env_file.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip() == env_key and v.strip():
                return v.strip().strip('"').strip("'")
    sys.exit(f"{env_key} not set (env or .env)")

LEDGER = ROOT / "runs" / "logs" / "study3_ledger_v2.jsonl"
EXHAUSTION = ROOT / "runs" / "logs" / "study3_credit_exhaustion.jsonl"
STORE = ROOT / "runs" / "study3" / "study3_store_v2.json"
DESIGNS_DIR = ROOT / "runs" / "study3" / "designs"
SOLUTIONS_DIR = ROOT / "runs" / "study3" / "solutions"
CKPT_DIR = ROOT / "runs" / "study3" / "checkpoints"
MAX_TOKENS = 8192
WORKERS = 64  # 2026-08-29 author directive: target ~100 calls/min/provider with
              # dynamic adaptation (D34 calibration lineage); Google account
              # upgraded to paid tier. 429 backoff handles throttle; watch and adapt.
PROMPT_TAG = "protocol13-v2"
PROTOCOL_ID = "13"
# Study-3 pilot draw (D55 amendment, 2026-08-28): deterministic seeded draw —
# random.Random(20260828).sample of the 19 confirmatory problems (numeric-sorted),
# rejection-resampled until 4 distinct domains per domain_map.json. Result:
PILOT_PROBLEMS = ["Business_Problem_6", "Business_Problem_8",
                  "Business_Problem_9", "Business_Problem_12"]

# Provider configs: [cheap sibling] and [frontier]. Conventions from
# refine_study2b_run.py (D27 temperatures: provider-enforced defaults; gpt
# rejects explicit temperature and uses max_completion_tokens + low reasoning).
MODELS = {
    "gpt": {
        "cheap": {"model": "gpt-5.6-luna", "endpoint": "https://api.openai.com/v1",
                  "env_key": "OPENAI_API_KEY", "api_format": "openai",
                  "omit_temperature": True, "max_tokens_field": "max_completion_tokens",
                  "reasoning_effort": "low"},
        "frontier": {"model": "gpt-5.6-sol", "endpoint": "https://api.openai.com/v1",
                     "env_key": "OPENAI_API_KEY", "api_format": "openai",
                     "omit_temperature": True, "max_tokens_field": "max_completion_tokens",
                     "reasoning_effort": "low"},
    },
    "claude": {
        "cheap": {"model": "claude-haiku-4-5-20251001",
                  "endpoint": "https://api.anthropic.com/v1",
                  "env_key": "ANTHROPIC_API_KEY", "api_format": "anthropic", "omit_temperature": True},
        "frontier": {"model": "claude-opus-5", "max_tokens": 32768,
                     "endpoint": "https://api.anthropic.com/v1",
                     "env_key": "ANTHROPIC_API_KEY", "api_format": "anthropic", "omit_temperature": True},
    },
    "gemini": {
        "cheap": {"model": "gemini-3.1-flash-lite",
                  "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai",
                  "env_key": "GEMINI_API_KEY", "api_format": "openai"},
        "frontier": {"model": "gemini-3.1-pro-preview",
                     "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai",
                     "env_key": "GEMINI_API_KEY", "api_format": "openai"},
    },
    "kimi": {
        "cheap": {"model": "kimi-k2.6", "endpoint": "https://api.moonshot.ai/v1",
                  "env_key": "KIMI_API_KEY", "api_format": "openai", "omit_temperature": True},
        "frontier": {"model": "moonshotai/Kimi-K3", "endpoint": "https://api.together.ai/v1",
                     "env_key": "TOGETHER_API_KEY", "api_format": "openai", "omit_temperature": True,
                     "extra": {"reasoning_effort": "low"}},  # D58: k3 via Together (author directive 2026-08-29)
    },
    "qwen": {
        "cheap": {"model": "qwen3.7-plus-2026-05-26",
                  "endpoint": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                  "env_key": "ALIBABA_API_KEY", "api_format": "openai",
                  "discount_window_utc": (14, 24)},
        "frontier": {"model": "qwen3.7-max-2026-06-08",
                     "endpoint": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                     "env_key": "ALIBABA_API_KEY", "api_format": "openai",
                     "discount_window_utc": (14, 24)},
    },
}

DESIGN_PROMPT = """You are an expert AI Pipeline Designer. Analyze the user's task and design the optimal multi-agent pipeline.

TASK: "{problem_text}"

CRITICAL INSTRUCTION: Describe the OUTCOME you want (e.g., "Translate legal contracts from English to Arabic"), NOT the pipeline architecture (e.g., "Create a quality gate that checks..."). The designer will infer the optimal structure. Do NOT prescribe pipeline structure, quality gates, or specific agent arrangements in your task — just state the objective.

Available agent roles:
- builder: Creates initial content/draft
- critic: Reviews and identifies issues
- refiner: Fixes issues based on feedback
- polisher: Final quality check and formatting
- analyst: Analyzes data and produces insights
- strategist: Develops strategies and plans
- expert: Domain-specific expert opinion
- reviewer: General review and feedback

Design rules:
1. Always start with a Builder agent
2. CRITICAL: An IF or WHILE quality gate MUST be placed AFTER the agent it assesses, not before. The agent being assessed must already have produced output before the gate can review it.
   CORRECT: Builder → Refiner → QualityGate(IF, "revise"→Refiner) ✓
   WRONG: Builder → QualityGate(IF) → Refiner ✗ (gate has nothing to assess!)
3. Use "if" steps for decision points. The "revise" keyword should route back to the most recent REFINER or BUILDER step — the agent that can actually fix the content.
4. Use "while" steps for iterative refinement (retry until quality met). Max 3 iterations.
5. Approval (human-in-the-loop) steps are NOT allowed: this pipeline runs fully automated.
6. End with Polisher for user-facing output
7. Keep pipelines under 8 steps
8. Give each agent a descriptive name reflecting its purpose
9. When using "if" or "while" steps, the agent MUST provide full analysis AND the routing keyword on the last line

For "if" steps: The agent provides a FULL quality assessment with detailed reasoning, then on the VERY LAST LINE outputs ONE keyword from a predefined list (e.g., "pass" or "revise"). The "revise" mapping MUST point to a REFINER or BUILDER agent that exists in the pipeline — never to a non-existent step.
For "while" steps: The agent provides a FULL quality assessment, then on the VERY LAST LINE outputs "retry" (to loop back and improve) or "pass" (to continue). Max 3 iterations. The targetStep MUST point to a REFINER or BUILDER agent.

IMPORTANT: In the explanation, clearly describe the execution flow including which steps may loop or branch. Example: "Builder → Refiner → Quality Check (if revise, loops back to Refiner up to 3x) → Polisher".

OUTPUT FORMAT: STRICT JSON ONLY. No markdown, no explanation outside JSON, no prose. The JSON must contain exactly these three top-level keys: "agents", "pipeline", "explanation".
{{
  "agents": [
    {{ "name": "Display Name", "role": "builder|critic|refiner|polisher|analyst|strategist|expert|reviewer", "systemPrompt": "Detailed prompt...", "description": "What this agent does" }}
  ],
  "pipeline": [
    {{ "name": "Builder", "role": "builder", "type": "agent", "systemPrompt": "..." }},
    {{ "name": "Refiner", "role": "refiner", "type": "agent", "systemPrompt": "You are a content refiner. Improve the previous output based on any quality feedback provided. Fix all issues and produce a polished, improved version." }},
    {{ "name": "Quality Gate", "role": "critic", "type": "if", "systemPrompt": "You are a quality gate. Review the refined output carefully. Provide your FULL assessment — strengths, weaknesses, specific issues. Then on the VERY LAST LINE output EXACTLY ONE of these keywords: pass, revise. The keyword determines pipeline routing.", "ifOptions": ["pass", "revise"], "ifMappings": {{ "pass": 4, "revise": 2 }} }},
    {{ "name": "Polisher", "role": "polisher", "type": "agent", "systemPrompt": "..." }}
  ],
  "explanation": "Why this design was chosen"
}}"""

REPAIR_PROMPT = """That was not valid. Error: {error}

Output ONLY valid JSON matching the exact format requested (top-level keys
"agents", "pipeline", "explanation"; no "approval" steps; under 8 steps).
No markdown code blocks, no prose, no explanation — just raw JSON."""


def validate_design(text):
    """Return (steps, error). Platform-schema validation (D56):
    steps = pipeline array; each step {name, type: agent|if|while, ...}.
    Free roles accepted (platform does not enforce the role vocabulary).
    No 'approval' steps (fully automated experiment). Under 8 steps total."""
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.lower().startswith("json"):
            t = t[4:]
    try:
        obj = json.loads(t)
    except Exception as e:
        return None, f"JSON parse error: {e}"
    if not isinstance(obj, dict):
        return None, "top-level JSON object required"
    steps = obj.get("pipeline")
    if not isinstance(steps, list) or not steps:
        agents = obj.get("agents")
        if isinstance(agents, list) and agents:
            # platform fallback: sequential pipeline from agents
            steps = [{"name": a.get("name", f"Step{i+1}"), "role": a.get("role", "custom"),
                      "type": "agent", "systemPrompt": a.get("systemPrompt", "")}
                     for i, a in enumerate(agents) if isinstance(a, dict)]
        else:
            return None, "missing 'pipeline' (and no 'agents' to derive it from)"
    if not (1 <= len(steps) <= 7):
        return None, f"need 1-7 steps (platform: under 8); got {len(steps)}"
    for i, s in enumerate(steps):
        if not isinstance(s, dict):
            return None, f"step {i} not an object"
        stype = s.get("type", "agent")
        if stype == "approval":
            return None, f"step {i} is an approval step — not allowed (automated run)"
        if stype not in ("agent", "if", "while"):
            return None, f"step {i} unknown type {stype!r}"
        if not isinstance(s.get("systemPrompt"), str) or not s["systemPrompt"].strip():
            return None, f"step {i} missing systemPrompt"
        s["type"] = stype
        s.setdefault("name", f"Step{i+1}")
        s.setdefault("role", "custom")
    return steps, None


class CreditExhausted(Exception):
    pass


def looks_like_credit(msg):
    m = msg.lower()
    return any(k in m for k in ("credit", "insufficient", "balance", "402",
                                "exceeded_current_quota", "payment required"))


def call(cfg, messages, keys, temperature=None):
    """One chat completion; returns (content, usage). Raises CreditExhausted."""
    if cfg["api_format"] == "anthropic":
        return _call_anthropic(cfg, messages, keys, temperature=temperature)
    payload = {"model": cfg["model"], "messages": messages}
    payload[cfg.get("max_tokens_field", "max_tokens")] = cfg.get("max_tokens", MAX_TOKENS)
    if temperature is not None and not cfg.get("omit_temperature"):
        payload["temperature"] = temperature
    if cfg.get("reasoning_effort"):
        payload["reasoning_effort"] = cfg["reasoning_effort"]
    if cfg.get("extra"):
        payload.update(cfg["extra"])
    req = urllib.request.Request(
        cfg["endpoint"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {keys[cfg['env_key']]}",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-study3/1.0"})
    for attempt in range(7):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"] or "", data.get("usage", {})
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = " | " + e.read().decode()[:300]
            except Exception:
                pass
            if looks_like_credit(f"HTTP {e.code}{body}"):
                raise CreditExhausted(f"HTTP {e.code}{body}")
            if e.code == 429:
                if attempt >= 6:
                    raise RuntimeError(f"HTTP 429 after 7 attempts{body}")
                wait = float(e.headers.get("Retry-After") or 0) or (15 * (attempt + 1))
                time.sleep(min(wait, 120))
                continue
            if attempt < 6 and e.code >= 500:
                time.sleep(2 ** attempt * 2)
                continue
            raise RuntimeError(f"HTTP {e.code}{body}")
        except CreditExhausted:
            raise
        except Exception:
            if attempt < 6:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError("call(): retry loop exhausted")


def _call_anthropic(cfg, messages, keys, temperature=None):
    # Anthropic rejects system-role entries inside messages; hoist to top-level.
    sys_parts = [m["content"] for m in messages if m["role"] == "system"]
    msgs = [m for m in messages if m["role"] != "system"]
    payload = {"model": cfg["model"], "messages": msgs, "max_tokens": cfg.get("max_tokens", MAX_TOKENS)}
    if sys_parts:
        payload["system"] = "\n\n".join(sys_parts)
    if temperature is not None and not cfg.get("omit_temperature"):
        payload["temperature"] = temperature
    req = urllib.request.Request(
        cfg["endpoint"].rstrip("/") + "/messages",
        data=json.dumps(payload).encode(),
        headers={"x-api-key": keys[cfg["env_key"]],
                 "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json",
                 "User-Agent": "orchestration-economics-study3/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
            text = "".join(b.get("text", "") for b in data.get("content", [])
                           if b.get("type") == "text")
            return text, data.get("usage", {})
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = " | " + e.read().decode()[:300]
            except Exception:
                pass
            if looks_like_credit(f"HTTP {e.code}{body}"):
                raise CreditExhausted(f"HTTP {e.code}{body}")
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise RuntimeError(f"HTTP {e.code}{body}")
        except CreditExhausted:
            raise
        except Exception:
            if attempt < 4:
                time.sleep(2 ** attempt * 2)
                continue
            raise


def in_window_utc(start, end):
    h = datetime.now(timezone.utc).hour
    return start <= h < end


def load_ledger():
    done, exhausted = set(), set()
    terminal, fail_count = set(), {}
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            st = r.get("status")
            if st == "completed" and r.get("final_len", 0) > 0:
                done.add(r["key"])
            if st == "credit_exhausted":
                exhausted.add(r["family"])
            if st == "design_failed":
                terminal.add(r["key"])      # protocol: exclude after ONE repair retry
            if st == "failed":
                fail_count[r["key"]] = fail_count.get(r["key"], 0) + 1
    # stop retrying keys that fail 3+ times (e.g. persistent content-moderation
    # blocks); they are disclosed as attrition in the participant flow.
    terminal |= {k for k, n in fail_count.items() if n >= 3}
    # auditable corrections: keys whose terminal status was caused by an
    # instrument bug (fixed since) are voided here with reason+timestamp,
    # so they re-enter the plan. Never deletes ledger history.
    voided_file = ROOT / "runs" / "logs" / "study3_voided.jsonl"
    if voided_file.exists():
        for line in voided_file.read_text().splitlines():
            try:
                v=json.loads(line)
                if "family_credit_restored" in v:
                    exhausted.discard(v["family_credit_restored"])
                else:
                    terminal.discard(v["key"])
            except Exception:
                pass
    return done, exhausted, terminal


def append_ledger(rec):
    with LEDGER.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def load_problems():
    """The 19 confirmatory problems = problems present in the frozen main ledger."""
    led = json.loads((ROOT / "runs" / "logs" / "main_run_ledger.json").read_text())
    ids = sorted({r["problemId"] for r in led["results"] if r.get("problemId")})
    bank = {}
    for f in ["business_problems_15.json", "business_problems_domain_15.json"]:
        bank.update(json.loads((ROOT / "data" / "problems" / f).read_text()))
    out = {}
    for pid in ids:
        p = bank[pid]
        out[pid] = f"{p['background_context']}\n\n{p['business_problem']}"  # D32.3 verbatim
    return out


def run_task(task, problems, keys, ignore_window):
    """One (arm, family, problem, rep): design -> validate -> execute. Ledger-append."""
    arm, family, pid, rep = task["arm"], task["family"], task["problem"], task["rep"]
    key = f"{arm}__{family}__{pid}__rep{rep}"
    rec = {"key": key, "arm": arm, "family": family, "problemId": pid, "rep": rep,
           "prompt_tag": PROMPT_TAG,
           "started_at": datetime.now(timezone.utc).isoformat()}
    cfg_d = MODELS[family]["frontier" if arm == "D-FRONT" else "cheap"]
    cfg_x = MODELS[family]["cheap"]
    w = cfg_d.get("discount_window_utc") or cfg_x.get("discount_window_utc")
    if w and not ignore_window and not in_window_utc(*w):
        rec.update(status="deferred_window")
        append_ledger(rec)
        return "deferred"
    ptext = problems[pid]
    try:
        # 1) design (step-level checkpointing: killed chunks resume mid-task)
        ckpt_file = CKPT_DIR / f"{key}.json"
        ck = {}
        if ckpt_file.exists():
            try:
                ck = json.loads(ckpt_file.read_text())
            except Exception:
                ck = {}
        print(f"  [{key}] design call...", flush=True)
        if ck.get("steps"):
            raw, du, steps = ck["raw"], {}, ck["steps"]
        else:
            # platform autoDesignService uses temperature 0.3 for the design call
            raw, du = call(cfg_d, [{"role": "user",
                                    "content": DESIGN_PROMPT.format(problem_text=ptext)}],
                           keys, temperature=0.3)
        rec["designer_model"] = cfg_d["model"]
        rec["designer_usage"] = du
        steps, err = validate_design(raw)
        if err:
            repair_msgs = [{"role": "user", "content": DESIGN_PROMPT.format(problem_text=ptext)}]
            if raw.strip():  # Moonshot rejects empty assistant messages
                repair_msgs.append({"role": "assistant", "content": raw})
            repair_msgs.append({"role": "user", "content": REPAIR_PROMPT.format(error=err)})
            raw2, du2 = call(cfg_d, repair_msgs, keys,
                             temperature=0.2)  # platform AutoDesign-retry uses 0.2
            rec["designer_usage_repair"] = du2
            steps, err2 = validate_design(raw2)
            if err2:
                rec.update(status="design_failed", error=f"{err} / repair: {err2}",
                           finished_at=datetime.now(timezone.utc).isoformat())
                append_ledger(rec)
                return "design_failed"
            raw = raw2
        DESIGNS_DIR.mkdir(parents=True, exist_ok=True)
        (DESIGNS_DIR / f"{key}.designer_raw.txt").write_text(raw)
        rec["n_steps"] = len(steps)
        ckpt_file.parent.mkdir(parents=True, exist_ok=True)

        # 2) execute pipeline on the cheap sibling (gate-aware; checkpoint each step)
        prior = ck.get("prior", "")
        step_logs = ck.get("step_logs", [])
        pc = ck.get("pc", 0)
        gate_counts = ck.get("gate_counts", {})
        final_agent_name = next((s["name"] for s in reversed(steps)
                                 if s["type"] == "agent"), steps[-1]["name"])

        def save_ckpt():
            ckpt_file.write_text(json.dumps({"raw": raw, "steps": steps, "pc": pc,
                                             "prior": prior, "step_logs": step_logs,
                                             "gate_counts": gate_counts}))

        save_ckpt()
        executed = 0
        while pc < len(steps) and executed < 40:  # hard cap vs runaway loops
            s = steps[pc]
            executed += 1
            user = (f"=== BUSINESS PROBLEM ===\n{ptext}\n\n"
                    + (f"=== PREVIOUS STEP OUTPUTS ===\n{prior}\n\n" if prior else "")
                    + "Produce your step's output now.")
            out, u = call(cfg_x, [{"role": "system", "content": s["systemPrompt"]},
                                  {"role": "user", "content": user}], keys)
            print(f"  [{key}] step {pc+1}/{len(steps)} {s['name']} ({s['type']}, "
                  f"{len(out)} chars)", flush=True)
            step_logs.append({"name": s["name"], "role": s["role"], "type": s["type"],
                              "system_prompt": s["systemPrompt"],
                              "output_len": len(out), "usage": u})
            prior += f"\n\n--- {s['name']} ---\n{out}"

            nxt = pc + 1
            if s["type"] in ("if", "while"):
                last = next((l.strip().lower().strip("*. ")
                             for l in reversed(out.splitlines()) if l.strip()), "")
                gid = f"{pc}:{s['name']}"
                gate_counts[gid] = gate_counts.get(gid, 0)
                if s["type"] == "if":
                    mappings = s.get("ifMappings") or {}
                    tgt = mappings.get(last)
                    step_logs[-1]["gate_keyword"] = last
                    if isinstance(tgt, int) and 1 <= tgt <= len(steps) \
                            and tgt - 1 < pc and gate_counts[gid] < 3:
                        gate_counts[gid] += 1
                        nxt = tgt - 1
                        step_logs[-1]["gate_routed_to"] = steps[nxt]["name"]
                else:  # while
                    step_logs[-1]["gate_keyword"] = last
                    if last.startswith("retry") and gate_counts[gid] < 3:
                        tgt = s.get("targetStep")
                        if isinstance(tgt, int) and 1 <= tgt <= len(steps) and tgt - 1 < pc:
                            gate_counts[gid] += 1
                            nxt = tgt - 1
                        else:  # fallback: re-run the immediately preceding agent step
                            for j in range(pc - 1, -1, -1):
                                if steps[j]["type"] == "agent":
                                    gate_counts[gid] += 1
                                    nxt = j
                                    break
                        if nxt != pc + 1:
                            step_logs[-1]["gate_routed_to"] = steps[nxt]["name"]
            pc = nxt
            save_ckpt()

        ckpt_file.unlink(missing_ok=True)
        rec["gate_counts"] = gate_counts
        rec["executed_steps"] = executed
        final = next((l["output_len"] for l in reversed(step_logs)
                      if l["name"] == final_agent_name), step_logs[-1]["output_len"])
        if final == 0:
            # empty final-agent output (observed: kimi-k2.6 polisher) is a
            # retriable failure, not a completed solution
            rec.update(status="failed", error="empty final agent output",
                       steps=step_logs, gate_counts=gate_counts,
                       finished_at=datetime.now(timezone.utc).isoformat())
            append_ledger(rec)
            ckpt_file.unlink(missing_ok=True)
            return "failed"
        rec.update(status="completed", executor_model=cfg_x["model"],
                   steps=step_logs, final_len=final,
                   finished_at=datetime.now(timezone.utc).isoformat())
        append_ledger(rec)
        # solution text for the judging store: output of the final AGENT step
        sol_file = SOLUTIONS_DIR / f"{key}.txt"
        sol_file.parent.mkdir(parents=True, exist_ok=True)
        sol_file.write_text(prior.split(f"--- {final_agent_name} ---\n")[-1])
        return "completed"
    except CreditExhausted as e:
        rec.update(status="credit_exhausted", error=str(e)[:300],
                   finished_at=datetime.now(timezone.utc).isoformat())
        append_ledger(rec)
        with EXHAUSTION.open("a") as f:
            f.write(json.dumps({"family": family, "reason": str(e)[:300],
                                "ts": datetime.now(timezone.utc).isoformat(),
                                "policy": "skip family, continue others"}) + "\n")
        return "credit_exhausted"
    except Exception as e:
        rec.update(status="failed", error=str(e)[:300],
                   finished_at=datetime.now(timezone.utc).isoformat())
        append_ledger(rec)
        return "failed"


def build_store():
    """Rebuild the judge_v2-compatible store from solutions + ledger (idempotent)."""
    entries = []
    sol_dir = SOLUTIONS_DIR
    if sol_dir.exists():
        for f in sorted(sol_dir.glob("*.txt")):
            key = f.stem
            arm, family, pid, rep = key.split("__")
            entries.append({"runId": key, "problemId": pid,
                            "fulltext": f.read_text(), "status": "completed",
                            "family": family, "arm": arm, "rep": rep})
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps({"protocol": PROTOCOL_ID, "prompt_tag": PROMPT_TAG,
                                 "runs": entries}, indent=1))
    print(f"store: {STORE} ({len(entries)} solutions)")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--families", default="")
    ap.add_argument("--reps", type=int, default=0, help="override rep count")
    ap.add_argument("--ignore-window", action="store_true")
    ap.add_argument("--build-store", action="store_true")
    args = ap.parse_args()

    if args.build_store:
        build_store()
        return

    problems = load_problems()
    pids = PILOT_PROBLEMS if args.pilot else sorted(problems)
    reps = args.reps or (1 if args.pilot else 3)
    fams = args.families.split(",") if args.families else list(MODELS)
    tasks = [{"arm": arm, "family": fam, "problem": pid, "rep": r}
             for arm in ["D-SELF", "D-FRONT"] for fam in fams
             for pid in pids for r in range(1, reps + 1)]
    # deterministic interleave (seed 42, D17)
    import random
    random.Random(42).shuffle(tasks)

    done, exhausted, terminal = load_ledger()
    todo = [t for t in tasks
            if f"{t['arm']}__{t['family']}__{t['problem']}__rep{t['rep']}" not in done
            and f"{t['arm']}__{t['family']}__{t['problem']}__rep{t['rep']}" not in terminal
            and t["family"] not in exhausted]
    print(f"Study 3 plan: {len(tasks)} tasks | done {len(tasks)-len(todo)-sum(1 for t in tasks if t['family'] in exhausted)} | "
          f"todo {len(todo)} | exhausted families: {sorted(exhausted) or 'none'}"
          + (" (WINDOW OVERRIDE)" if args.ignore_window else ""))
    if args.dry_run:
        from collections import Counter
        print(Counter((t["arm"], t["family"]) for t in tasks))
        return

    keys = {k: load_key(k) for k in
            {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
             "KIMI_API_KEY", "ALIBABA_API_KEY", "TOGETHER_API_KEY"}}
    from collections import Counter
    stats = Counter()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(run_task, t, problems, keys, args.ignore_window)
                for t in todo]
        for i, f in enumerate(futs, 1):
            res = f.result()
            stats[res] += 1
            if i % 20 == 0 or res in ("failed", "credit_exhausted", "design_failed"):
                print(f"[{i}/{len(todo)}] {res} | totals: {dict(stats)}")
    print(f"done: {dict(stats)}")
    build_store()


if __name__ == "__main__":
    main()
