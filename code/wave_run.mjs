#!/usr/bin/env node
// wave_run.mjs — Protocol 12 confirmatory replication wave runner.
//
// Scope (pre-registered, OSF jg49x): 30 fresh problems x 10 families x
// 3 core cells (C-S-N, C-T-N, F-S-N); cheap cells x3, frontier cell x2
// = 2,400 runs. Registry: pipelines/fixed/wave_pipelines_registry.json
// (created by code/wave_create_pipelines.mjs; wave-only — NEVER touches the
// frozen Study-1 registry).
//
// Inherits all A1 integrity machinery from main_run.mjs: full-text capture
// via export_run, one-file-per-run atomic writes (D34), resume by directory
// scan, deterministic arm-interleaved order (seed 42), truncatedAtSource flag.
//
// Protocol 12 §5 discipline built in:
//   §5.2 window gate — generation ONLY inside UTC 14:00–00:00 (qwen off-peak
//          AND avoids DeepSeek peak windows); runner sleeps until window.
//   §5.4 credit exhaustion — a family whose provider reports credit/balance
//          exhaustion is skipped for its remaining tasks; every other family
//          continues; exhaustion is logged to the ledger + a sidecar file.
//
// Usage:
//   node code/wave_run.mjs --dry-run
//   node code/wave_run.mjs [--families kimi,mistral] [--concurrency 50]
//   node code/wave_run.mjs --ignore-window   # author override (logged)

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync, mkdirSync, renameSync, readdirSync, appendFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const REGISTRY = join(ROOT, "pipelines", "fixed", "wave_pipelines_registry.json");
const PROBLEM_FILES = [
  join(ROOT, "data", "problems", "fresh_business_cases_10.json"),
  join(ROOT, "data", "problems", "fresh_business_cases_20_wave.json"),
];
const MCP_CALL = join(ROOT, "..", "..", "scripts", "mcp-call.mjs");
const STREAM_BASE = "https://deewaanai-production.up.railway.app/api/stream";
const RAW_DIR = join(ROOT, "runs", "raw", "wave");
const LEDGER = join(ROOT, "runs", "logs", "wave_run_ledger.json");
const EXHAUSTION_LOG = join(ROOT, "runs", "logs", "wave_credit_exhaustion.jsonl");
const CONCURRENCY_FILE = join(ROOT, "config", "wave_concurrency.json");

const POLL_INTERVAL_MS = 5000;
const RUN_TIMEOUT_MS = 20 * 60 * 1000;
const SEED = 42; // same deterministic interleaving discipline as Study 1 (D17)
const CAP = 16012;
const RETRY_BACKOFF_S = [5, 15, 30, 60];

const ignoreWindow = process.argv.includes("--ignore-window");
const CONCURRENCY = (() => {
  const i = process.argv.indexOf("--concurrency");
  if (i >= 0) return Number(process.argv[i + 1]);
  return 100;
})();

function mcp(tool, args) {
  let lastErr;
  for (let attempt = 0; attempt <= RETRY_BACKOFF_S.length; attempt++) {
    try {
      const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
        encoding: "utf8", timeout: 90_000, maxBuffer: 32 * 1024 * 1024,
      });
      const parsed = JSON.parse(out);
      if (parsed.isError) throw new Error(`${tool} failed: ${parsed.content?.[0]?.text}`);
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

// ---------- Discount window gate (Protocol 12 §5.2) ----------
function inDiscountWindowUtc() {
  const h = new Date().getUTCHours();
  return h >= 14; // UTC 14:00–23:59 (qwen off-peak; avoids DeepSeek peaks)
}
async function waitForWindow() {
  if (ignoreWindow) {
    console.warn("WARNING: --ignore-window override active; logged in ledger header.");
    return;
  }
  while (!inDiscountWindowUtc()) {
    const ms = 60_000;
    console.log(`[window] outside UTC 14:00–00:00 discount window; sleeping 60s (${new Date().toISOString()})`);
    await sleep(ms);
  }
}

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
const problems = {};
for (const f of PROBLEM_FILES) {
  const blob = JSON.parse(readFileSync(f, "utf8"));
  for (const [k, v] of Object.entries(blob)) {
    if (k.startsWith("_")) continue;
    if (v && typeof v === "object" && v.business_problem) problems[k] = v;
  }
}
const problemIds = Object.keys(problems).sort();
if (problemIds.length !== 30) {
  throw new Error(`expected 30 wave problems, got ${problemIds.length}`);
}

const cfg = JSON.parse(readFileSync(join(ROOT, "config", "experiment_config.json"), "utf8"));
const repsCheap = cfg.generation.reps_cheap_cells;       // 3
const repsFrontier = cfg.generation.reps_frontier_cells; // 2

// Per-family concurrency caps (RPM ramp output; defaults to global cap).
const famConcurrency = existsSync(CONCURRENCY_FILE)
  ? JSON.parse(readFileSync(CONCURRENCY_FILE, "utf8")) : {};
function makeSemaphore(n) {
  let active = 0; const q = [];
  return async (fn) => {
    if (active >= n) await new Promise((r) => q.push(r));
    active++;
    try { return await fn(); } finally { active--; (q.shift() ?? (() => {}))(); }
  };
}
const famSem = {};
const semFor = (family) => (famSem[family] ??= makeSemaphore(
  Math.max(1, Math.min(famConcurrency[family] ?? CONCURRENCY, CONCURRENCY))));

const tasks = [];
for (const entry of registry.created) {
  const meta = entry.definition._meta;
  const reps = meta.tier === "frontier" ? repsFrontier : repsCheap;
  for (const problemId of problemIds) {
    for (let rep = 1; rep <= reps; rep++) {
      tasks.push({ entry, problemId, rep, tier: meta.tier, cell: meta.cell, family: meta.family });
    }
  }
}

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

// Problem filter (smoke / mini-pilot only; the full wave runs unfiltered).
const probArg = process.argv.find((a) => a.startsWith("--problems="));
const probIdx = process.argv.indexOf("--problems");
const probList = probArg ? probArg.split("=")[1] : (probIdx >= 0 ? process.argv[probIdx + 1] : null);
const PROBLEM_FILTER = probList ? new Set(probList.split(",").map((s) => s.trim())) : null;
if (PROBLEM_FILTER) {
  const before = tasks.length;
  for (let i = tasks.length - 1; i >= 0; i--) {
    if (!PROBLEM_FILTER.has(tasks[i].problemId)) tasks.splice(i, 1);
  }
  console.log(`Problem filter active: ${[...PROBLEM_FILTER].join(", ")} (${tasks.length}/${before} tasks)`);
}

if (process.argv.includes("--dry-run")) {
  const byTier = tasks.reduce((a, t) => (a[t.tier] = (a[t.tier] ?? 0) + 1, a), {});
  const byFam = tasks.reduce((a, t) => (a[t.family] = (a[t.family] ?? 0) + 1, a), {});
  console.log(`Wave plan: ${tasks.length} runs | problems=${problemIds.length} ` +
    `| pipelines=${registry.created.length} | byTier=${JSON.stringify(byTier)} | c=${CONCURRENCY}`);
  console.log(`byFamily=${JSON.stringify(byFam)}`);
  process.exit(0);
}

// ---------- Resume by directory scan (D34) ----------
mkdirSync(RAW_DIR, { recursive: true });
const safe = (s) => String(s).replace(/[^a-zA-Z0-9_.\/-]+/g, "_");
const runFile = (t) => join(RAW_DIR, `${safe(t.entry.definition.name)}__${t.problemId}__rep${t.rep}.json`);
const done = new Set(readdirSync(RAW_DIR).filter((f) => f.endsWith(".json")).filter((f) => {
  try {
    const r = JSON.parse(readFileSync(join(RAW_DIR, f), "utf8"));
    return r.status === "completed" && ((r.fulltextLen ?? 0) > 0 || (r.finalResponse ?? "").length > 0);
  } catch { return false; }
}).map((f) => f.replace(/\.json$/, "")));

// Credit-exhaustion tracking (Protocol 12 §5.4).
const exhausted = new Set();
const CREDIT_MARKERS = ["balance", "insufficient", "credit", "quota_exceeded", "billing"];
function looksLikeCredit(msg) {
  const s = String(msg ?? "").toLowerCase();
  return CREDIT_MARKERS.some((m) => s.includes(m));
}
function markExhausted(family, reason) {
  if (exhausted.has(family)) return;
  exhausted.add(family);
  const line = JSON.stringify({ family, reason: String(reason).slice(0, 400),
    ts: new Date().toISOString(), policy: "Protocol 12 §5.4: skip family, continue others" });
  appendFileSync(EXHAUSTION_LOG, line + "\n");
  console.error(`[credit] family ${family} EXHAUSTED — skipping its remaining tasks: ${reason}`);
}

function flushRecord(t, rec) {
  const file = runFile(t);
  const tmp = `${file}.tmp`;
  writeFileSync(tmp, JSON.stringify(rec, null, 2) + "\n");
  renameSync(tmp, file);
}

async function runOne(t) {
  const key = `${safe(t.entry.definition.name)}__${t.problemId}__rep${t.rep}`;
  if (done.has(key)) return;
  if (exhausted.has(t.family)) {
    flushRecord(t, {
      runKey: key, cell: t.cell, family: t.family, tier: t.tier,
      problemId: t.problemId, rep: t.rep, status: "skipped_credit_exhausted",
      startedAtUtc: new Date().toISOString(), finishedAtUtc: new Date().toISOString(),
    });
    done.add(key);
    return;
  }
  const p = problems[t.problemId];
  const input = `${p.background_context}\n\n${p.business_problem}`; // D32.3 verbatim
  const rec = {
    runKey: key, projectId: t.entry.projectId, name: t.entry.definition.name,
    cell: t.cell, family: t.family, tier: t.tier, problemId: t.problemId, rep: t.rep,
    concurrency: CONCURRENCY, harness: "wave_run/Protocol12",
    startedAtUtc: new Date().toISOString(), in_discount_window: inDiscountWindowUtc(),
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
      if (rec.status === "failed") rec.realError = streamError(runId) ?? status?.error ?? null;
      if (rec.status === "completed") {
        const statusText = status.finalResponse ?? "";
        rec.truncatedAtSource = statusText.length === CAP;
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
    // Credit exhaustion detection (§5.4): paused_credit or failed-with-balance.
    if (rec.status === "paused_credit" ||
        (rec.status === "failed" && looksLikeCredit(rec.realError))) {
      markExhausted(t.family, rec.realError ?? "paused_credit");
    }
  } catch (e) {
    rec.status = "error";
    rec.realError = String(e?.message ?? e).slice(0, 300);
    if (looksLikeCredit(rec.realError)) markExhausted(t.family, rec.realError);
  }
  rec.finishedAtUtc = new Date().toISOString();
  flushRecord(t, rec);
  done.add(key);
  console.log(`${rec.status}  ${rec.cell}/${rec.family}/${t.problemId}/r${t.rep}  ` +
    `tok=${rec.totalTokensUsed ?? "-"} len=${rec.fulltextLen ?? (rec.finalResponse ?? "").length}` +
    `${rec.truncatedAtSource ? " TRUNC@SOURCE" : ""} runId=${rec.runId ?? "-"} ` +
    `[${done.size}/${tasks.length}]${rec.realError ? `  ERROR: ${rec.realError}` : ""}`);
}

console.log(`Wave run: ${tasks.length} runs, problems=${problemIds.length}, c=${CONCURRENCY}` +
  (ignoreWindow ? " (WINDOW OVERRIDE)" : ""));
await waitForWindow();
let idx = 0;
const workers = Array.from({ length: Math.min(CONCURRENCY, tasks.length) }, async () => {
  for (;;) {
    // §5.2 strict window enforcement: a wave that starts inside the window
    // must not keep generating after UTC midnight (qwen off-peak rule).
    if (!ignoreWindow) await waitForWindow();
    // Atomic claim: idx++ in one synchronous expression (the await above can
    // let other workers drain the queue between check and increment).
    const i = idx++;
    if (i >= tasks.length) break;
    const t = tasks[i];
    // §5.4: once a family is marked credit-exhausted, skip its remaining
    // tasks (they are left for a later lane after credits are restored).
    if (exhausted.has(t.family)) continue;
    await semFor(t.family)(() => runOne(t));
  }
});
await Promise.all(workers);

// Post-hoc ledger merge (D34 pattern).
const records = readdirSync(RAW_DIR).filter((f) => f.endsWith(".json"))
  .map((f) => JSON.parse(readFileSync(join(RAW_DIR, f), "utf8")));
writeFileSync(LEDGER, JSON.stringify({
  purpose: "Protocol 12 wave ledger (merged from runs/raw/wave, D34 pattern)",
  protocol: "12-PROTOCOL-WAVE-CONFIRMATORY-REPLICATION.md",
  osf: "jg49x",
  mergedAtUtc: new Date().toISOString(),
  windowOverride: ignoreWindow || undefined,
  familiesExhausted: [...exhausted],
  total: records.length,
  completedNonEmpty: records.filter((r) => r.status === "completed" && (r.finalResponse ?? "").length > 0).length,
  truncatedAtSource: records.filter((r) => r.truncatedAtSource).length,
  results: records,
}, null, 2) + "\n");
console.log(`\nLedger: ${LEDGER} (${records.length} records)`);
