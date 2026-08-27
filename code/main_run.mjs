#!/usr/bin/env node
// main_run.mjs — confirmatory main run (interim-2) runner, Amendment A1 ready.
//
// Scope (pre-registered): 19 main problems (30 − 11 pilot) × 40 pipelines ×
// reps (cheap cells 3 / frontier cells 2, config generation.reps_*) = 1,900 runs,
// concurrent c=100 (D34-calibrated), inside the D21 execution window.
//
// Amendment A1 readiness built in:
//   A1.1 Full-text capture: after completion the full answer is retrieved via
//        export_run (granular archive) — run_status finalResponse is 16,000-char
//        capped (getRunStatus.ts) and the cap truncated 130/371 pilot solutions.
//        Each record logs truncatedAtSource + fulltextLen for audit.
//   D34 writer isolation: ONE file per run under runs/raw/main/ written via
//        temp file + atomic rename; no shared mutable log; resumable by
//        directory scan; ledger assembled post-hoc by merge_main_ledger.
//
// Task order is deterministic and arm-interleaved (seed 42, D17) so any
// interruption cannot confound arms with time.
//
// Usage:
//   node code/main_run.mjs --dry-run      # print plan counts, create nothing
//   node code/main_run.mjs                # execute (discount window only)
//   node code/main_run.mjs --families kimi,claude   # resume only these families

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync, mkdirSync, renameSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const REGISTRY = join(ROOT, "pipelines", "fixed", "fixed_pipelines_registry.json");
const PROBLEMS_30 = join(ROOT, "data", "problems", "business_problems_30.json");
const PILOT_A = join(ROOT, "config", "pilot_problems_phaseA.json");
const MCP_CALL = join(ROOT, "..", "..", "scripts", "mcp-call.mjs");
const STREAM_BASE = "https://deewaanai-production.up.railway.app/api/stream";
const RAW_DIR = join(ROOT, "runs", "raw", "main");

const CONCURRENCY = 100;
const POLL_INTERVAL_MS = 5000;
const RUN_TIMEOUT_MS = 20 * 60 * 1000;
const SEED = 42; // D17 ledger seed
const CAP = 16012; // run_status truncation fingerprint (16000 + marker)

const RETRY_BACKOFF_S = [5, 15, 30, 60];
function mcp(tool, args) {
  let lastErr;
  for (let attempt = 0; attempt <= RETRY_BACKOFF_S.length; attempt++) {
    try {
      const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
        encoding: "utf8", timeout: 90_000, maxBuffer: 32 * 1024 * 1024,
      });
      const parsed = JSON.parse(out);
      if (parsed.isError) throw new Error(`${tool} failed: ${parsed.content?.[0]?.text}`);
      // Transport glitches occasionally return a result with no content array;
      // classify as transient so the retry loop (below) handles it (observed
      // 2026-08-05: "Cannot read properties of undefined (reading '0')").
      if (!parsed.content?.[0]?.text) throw new Error(`${tool}: empty MCP response (transient)`);
      return JSON.parse(parsed.content[0].text);
    } catch (e) {
      lastErr = e;
      const msg = String(e?.message ?? e);
      const transient = ["Command failed", "fetch failed", "ETIMEDOUT", "ECONNRESET",
        "ECONNREFUSED", "ENOTFOUND", "EAI_AGAIN", "socket hang up", "empty MCP response"].some((t) => msg.includes(t));
      if (!transient) throw e;
      if (attempt < RETRY_BACKOFF_S.length) {
        console.error(`  [retry] ${tool} attempt ${attempt + 1} transient; sleeping ${RETRY_BACKOFF_S[attempt]}s`);
        execFileSync("sleep", [String(RETRY_BACKOFF_S[attempt])]);
      }
    }
  }
  throw lastErr;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function streamError(runId) {
  if (!Number.isInteger(runId)) return null;
  let out = "";
  try {
    out = execFileSync("curl", ["-sN", "--max-time", "10", `${STREAM_BASE}/${runId}`], {
      encoding: "utf8", timeout: 15_000,
    });
  } catch (e) { out = e.stdout ?? ""; }
  try {
    const line = out.split("\n").find((l) => l.includes("step_error") || l.includes("pipeline_error"));
    return line ? (JSON.parse(line.replace(/^data: /, "")).error ?? null) : null;
  } catch { return null; }
}

// ---------- Plan construction ----------
const registry = JSON.parse(readFileSync(REGISTRY, "utf8"));
const problems = JSON.parse(readFileSync(PROBLEMS_30, "utf8"));
const pilotIds = new Set(JSON.parse(readFileSync(PILOT_A, "utf8")).pilot_problem_ids);
const mainProblemIds = Object.keys(problems).filter((id) => !pilotIds.has(id)).sort();
const cfg = JSON.parse(readFileSync(join(ROOT, "config", "experiment_config.json"), "utf8"));
const repsCheap = cfg.generation.reps_cheap_cells;       // 3
const repsFrontier = cfg.generation.reps_frontier_cells; // 2

if (registry.created.length !== 40) {
  console.error(`WARNING: registry has ${registry.created.length} pipelines; full factorial expects 40 ` +
    `(30 confirmatory + F-T-N/F-T-P for all 5 families). Run code/create_ft_remaining.mjs first if missing.`);
}

const tasks = [];
for (const entry of registry.created) {
  const meta = entry.definition._meta;
  const reps = meta.tier === "frontier" ? repsFrontier : repsCheap;
  for (const problemId of mainProblemIds) {
    for (let rep = 1; rep <= reps; rep++) {
      tasks.push({ entry, problemId, rep, tier: meta.tier, cell: meta.cell, family: meta.family });
    }
  }
}

// Deterministic arm-interleaved order (mulberry32, seed 42 — D17).
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rnd = mulberry32(SEED);
for (let i = tasks.length - 1; i > 0; i--) {
  const j = Math.floor(rnd() * (i + 1));
  [tasks[i], tasks[j]] = [tasks[j], tasks[i]];
}

// Optional family filter for partial resumes (author instruction 2026-08-05:
// run only recharged families; gpt deferred until its account is recharged).
const famArg = process.argv.find((a) => a.startsWith("--families="));
const famIdx = process.argv.indexOf("--families");
const famList = famArg ? famArg.split("=")[1] : (famIdx >= 0 ? process.argv[famIdx + 1] : null);
const FAMILY_FILTER = famList ? new Set(famList.split(",").map((s) => s.trim())) : null;
if (FAMILY_FILTER) {
  const before = tasks.length;
  for (let i = tasks.length - 1; i >= 0; i--) {
    if (!FAMILY_FILTER.has(tasks[i].family)) tasks.splice(i, 1);
  }
  console.log(`Family filter active: ${[...FAMILY_FILTER].join(", ")} (${tasks.length}/${before} tasks)`);
}

if (process.argv.includes("--dry-run")) {
  const byTier = tasks.reduce((a, t) => (a[t.tier] = (a[t.tier] ?? 0) + 1, a), {});
  console.log(`Main run plan: ${tasks.length} runs | problems=${mainProblemIds.length} ` +
    `| pipelines=${registry.created.length} | byTier=${JSON.stringify(byTier)} | c=${CONCURRENCY}`);
  console.log(`First 5 (interleaved, seed ${SEED}):`,
    tasks.slice(0, 5).map((t) => `${t.cell}/${t.family}/${t.problemId}/r${t.rep}`).join(", "));
  process.exit(0);
}

// ---------- Resume by directory scan (D34) ----------
mkdirSync(RAW_DIR, { recursive: true });
const safe = (s) => String(s).replace(/[^a-zA-Z0-9_-]+/g, "_");
const runFile = (t) => join(RAW_DIR, `${safe(t.entry.definition.name)}__${t.problemId}__rep${t.rep}.json`);
// Only COMPLETED runs with NON-EMPTY text count as done — failed/error/paused
// records, and provider edge cases that report "completed" with an empty
// response (observed once on kimi/Together, run 1268), are retried on resume.
const done = new Set(readdirSync(RAW_DIR).filter((f) => f.endsWith(".json")).filter((f) => {
  try {
    const r = JSON.parse(readFileSync(join(RAW_DIR, f), "utf8"));
    return r.status === "completed" && ((r.fulltextLen ?? 0) > 0 || (r.finalResponse ?? "").length > 0);
  } catch { return false; }
}).map((f) => f.replace(/\.json$/, "")));

function flushRecord(t, rec) {
  const file = runFile(t);
  const tmp = `${file}.tmp`;
  writeFileSync(tmp, JSON.stringify(rec, null, 2) + "\n");
  renameSync(tmp, file); // atomic
}

async function runOne(t) {
  const key = `${safe(t.entry.definition.name)}__${t.problemId}__rep${t.rep}`;
  if (done.has(key)) return;
  const p = problems[t.problemId];
  const input = `${p.background_context}\n\n${p.business_problem}`; // D32.3 rendering rule, verbatim
  const rec = {
    runKey: key, projectId: t.entry.projectId, name: t.entry.definition.name,
    cell: t.cell, family: t.family, tier: t.tier, problemId: t.problemId, rep: t.rep,
    concurrency: CONCURRENCY, harness: "main_run/A1",
    startedAtUtc: new Date().toISOString(),
  };
  try {
    const { runId } = mcp("run_pipeline", { projectId: t.entry.projectId, input });
    rec.runId = runId;
    const deadline = Date.now() + RUN_TIMEOUT_MS;
    let status;
    while (Date.now() < deadline) {
      await sleep(POLL_INTERVAL_MS);
      status = mcp("run_status", { runId });
      if (["completed", "failed"].includes(status.status)) break;
      if (status.status === "paused" || status.status === "paused_credit") {
        rec.status = "paused_credit"; break;
      }
    }
    if (rec.status !== "paused_credit") {
      rec.status = ["completed", "failed"].includes(status?.status) ? status.status : "timeout";
      rec.totalTokensUsed = status?.totalTokensUsed ?? null;
      rec.totalLatencyMs = status?.totalLatencyMs ?? null;
      rec.steps = (status?.steps ?? []).map((s) => ({
        step: s.step, agentRole: s.agentRole, status: s.status,
        tokensUsed: s.tokensUsed, latencyMs: s.latencyMs,
      }));
      if (rec.status === "failed") rec.realError = streamError(runId);
      if (rec.status === "completed") {
        const statusText = status.finalResponse ?? "";
        rec.truncatedAtSource = statusText.length === CAP; // A1.1 audit flag
        // A1.1: full text via export_run (granular archive), never the capped field.
        try {
          const exp = mcp("export_run", { runId });
          const content = (exp?.agentResponses?.[0]?.content) ?? "";
          rec.fulltextLen = content.length;
          rec.finalResponse = content.length >= statusText.length ? content : statusText;
          rec.fulltextSource = content.length >= statusText.length ? "export_run" : "run_status";
          const gfile = join(ROOT, "runs", "granular",
            `${safe(rec.name)}__${t.problemId}__rep${t.rep}__run${runId}.json`);
          writeFileSync(`${gfile}.tmp`, JSON.stringify({
            archivedAtUtc: new Date().toISOString(), ...rec, export: exp,
          }, null, 2) + "\n");
          renameSync(`${gfile}.tmp`, gfile);
        } catch (e) {
          rec.finalResponse = statusText;
          rec.fulltextSource = "run_status_only";
          rec.archiveError = String(e?.message ?? e).slice(0, 200);
        }
      }
    }
  } catch (e) {
    rec.status = "error";
    rec.realError = String(e?.message ?? e).slice(0, 300);
  }
  rec.finishedAtUtc = new Date().toISOString();
  flushRecord(t, rec);
  done.add(key);
  console.log(`${rec.status}  ${rec.cell}/${rec.family}/${t.problemId}/r${t.rep}  ` +
    `tok=${rec.totalTokensUsed ?? "-"} len=${rec.fulltextLen ?? (rec.finalResponse ?? "").length}` +
    `${rec.truncatedAtSource ? " TRUNC@SOURCE" : ""} runId=${rec.runId ?? "-"} ` +
    `[${done.size}/${tasks.length}]${rec.realError ? `  ERROR: ${rec.realError}` : ""}`);
}

console.log(`Main run: ${tasks.length} runs, problems=${mainProblemIds.length}, c=${CONCURRENCY}`);
let idx = 0;
const workers = Array.from({ length: Math.min(CONCURRENCY, tasks.length) }, async () => {
  while (idx < tasks.length) {
    const t = tasks[idx++];
    await runOne(t);
  }
});
await Promise.all(workers);

// Post-hoc ledger merge (D34).
const records = readdirSync(RAW_DIR).filter((f) => f.endsWith(".json"))
  .map((f) => JSON.parse(readFileSync(join(RAW_DIR, f), "utf8")));
const ledgerPath = join(ROOT, "runs", "logs", "main_run_ledger.json");
writeFileSync(ledgerPath, JSON.stringify({
  purpose: "Main run ledger (merged from runs/raw/main, D34)",
  mergedAtUtc: new Date().toISOString(),
  total: records.length,
  completedNonEmpty: records.filter((r) => r.status === "completed" && (r.finalResponse ?? "").length > 0).length,
  truncatedAtSource: records.filter((r) => r.truncatedAtSource).length,
  results: records,
}, null, 2) + "\n");
console.log(`\nLedger: ${ledgerPath} (${records.length} records)`);
