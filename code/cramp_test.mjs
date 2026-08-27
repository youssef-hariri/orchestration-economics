#!/usr/bin/env node
// D34 c-ramp — concurrency calibration harness (PRODUCTION).
//
// Finds the optimal SWARM_WORKER_CONCURRENCY via top-down bisection. Submits a
// 100-run burst (5 family lanes x 20 hello translations, single-step solo C-S-N
// pipelines), then pulls precise per-run timing from the DB (swarm_runs.
// total_latency_ms) and compares against the c=2 hello-smoke baseline.
//
// PASS criterion (per family, all must hold):
//   - 0 failed/cancelled runs, AND
//   - median per-run latency inflation <= 10% vs the c=2 baseline.
// Latency inflation is a proxy for provider throttling (429 -> AIMD backoff ->
// retry -> longer latency). The optimal concurrency = highest level that PASSES.
//
// Usage:
//   CRAMP_DB_URL=mysql://... node cramp_test.mjs --baseline      # capture c=2 baseline (smoke batches 2-6)
//   CRAMP_DB_URL=mysql://... node cramp_test.mjs --run <level>   # run burst, label with concurrency <level>

import { execFileSync } from "node:child_process";
import { writeFileSync, readFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import mysql from "mysql2/promise";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const MCP_CALL = join(ROOT, "..", "..", "scripts", "mcp-call.mjs");
const LOGDIR = join(ROOT, "runs", "logs");
const BASELINE_PATH = join(LOGDIR, "cramp_baseline.json");
const DB_URL = process.env.CRAMP_DB_URL;

// 5 family lanes: single-step solo C-S-N confirmatory pipelines (one per family).
const FAMILIES = [
  { family: "gpt", projectId: 13 },
  { family: "claude", projectId: 19 },
  { family: "gemini", projectId: 25 },
  { family: "kimi", projectId: 31 },
  { family: "qwen", projectId: 37 },
];
const PID2FAM = Object.fromEntries(FAMILIES.map((f) => [f.projectId, f.family]));
const BASELINE_BATCHIDS = [2, 3, 4, 5, 6]; // c=2 hello-smoke (gpt,claude,gemini,kimi,qwen)

const LANGS = [
  "French", "Spanish", "German", "Yoruba", "Swahili", "Arabic", "Thai",
  "Japanese", "Korean", "Mandarin Chinese", "Hindi", "Bengali", "Portuguese",
  "Russian", "Turkish", "Vietnamese", "Indonesian", "Italian", "Dutch", "Greek",
];
const inputFor = (lang) =>
  `Translate the English word "hello" into ${lang}. Reply with only the translated word, nothing else.`;

function mcp(tool, args) {
  const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
    encoding: "utf8",
    timeout: 120_000,
  });
  const parsed = JSON.parse(out);
  if (parsed.isError) throw new Error(`${tool} failed: ${parsed.content?.[0]?.text}`);
  return JSON.parse(parsed.content[0].text);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const TERMINAL = new Set(["completed", "completed_with_failures", "cancelled"]);

async function pollBatch(batchId, { intervalMs = 4000, timeoutMs = 25 * 60 * 1000 } = {}) {
  const deadline = Date.now() + timeoutMs;
  let status = null;
  while (Date.now() < deadline) {
    status = mcp("batch_status", { batchId });
    process.stdout.write(`\r  batch ${batchId}: ${status.status}  ${status.completedRuns}/${status.totalRuns}  failed=${status.failedRuns}   `);
    if (TERMINAL.has(status.status)) { process.stdout.write("\n"); return status; }
    await sleep(intervalMs);
  }
  process.stdout.write("\n");
  return status ?? { status: "timeout" };
}

function percentile(sortedAsc, p) {
  if (!sortedAsc.length) return null;
  const idx = Math.min(sortedAsc.length - 1, Math.floor((p / 100) * sortedAsc.length));
  return sortedAsc[idx];
}

async function fetchRuns(batchIds) {
  const c = await mysql.createConnection({ uri: DB_URL, connectTimeout: 15000 });
  const ph = batchIds.map(() => "?").join(",");
  const [rows] = await c.execute(
    `SELECT id, batch_id, project_id, status, error, total_tokens_used, total_latency_ms,
            TIMESTAMPDIFF(SECOND, started_at, completed_at) AS wall_s
     FROM swarm_runs WHERE batch_id IN (${ph})`,
    batchIds,
  );
  await c.end();
  return rows;
}

function statsByFamily(rows) {
  const acc = {};
  for (const f of FAMILIES) acc[f.family] = { count: 0, completed: 0, failed: 0, lat: [], wall: [], tokens: 0 };
  for (const r of rows) {
    const fam = PID2FAM[r.project_id];
    if (!fam) continue;
    const s = acc[fam];
    s.count++;
    if (r.status === "completed") s.completed++;
    if (r.status === "failed" || r.status === "cancelled") s.failed++;
    if (r.total_latency_ms != null) s.lat.push(r.total_latency_ms);
    if (r.wall_s != null) s.wall.push(r.wall_s);
    s.tokens += r.total_tokens_used || 0;
  }
  const out = {};
  for (const [fam, s] of Object.entries(acc)) {
    s.lat.sort((a, b) => a - b);
    s.wall.sort((a, b) => a - b);
    out[fam] = {
      count: s.count, completed: s.completed, failed: s.failed, tokens: s.tokens,
      medianLatencyMs: percentile(s.lat, 50),
      p95LatencyMs: percentile(s.lat, 95),
      medianWallS: percentile(s.wall, 50),
    };
  }
  return out;
}

async function baseline() {
  if (!DB_URL) throw new Error("CRAMP_DB_URL required");
  const rows = await fetchRuns(BASELINE_BATCHIDS);
  const stats = statsByFamily(rows);
  mkdirSync(LOGDIR, { recursive: true });
  writeFileSync(BASELINE_PATH, JSON.stringify({ source: "hello-smoke c=2 batches 2-6", stats }, null, 2) + "\n");
  console.log("Baseline (c=2) per-family latency:");
  for (const [fam, s] of Object.entries(stats)) {
    console.log(`  ${fam.padEnd(8)} median=${s.medianLatencyMs}ms  p95=${s.p95LatencyMs}ms  n=${s.count}  failed=${s.failed}`);
  }
  console.log(`saved: ${BASELINE_PATH}`);
}

async function run(level) {
  if (!DB_URL) throw new Error("CRAMP_DB_URL required");
  const baselineStats = JSON.parse(readFileSync(BASELINE_PATH, "utf8")).stats;
  const tag = new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-");
  const inputs = LANGS.map(inputFor);
  console.log(`c-ramp run @ concurrency=${level}: ${FAMILIES.length} families x ${inputs.length} = ${FAMILIES.length * inputs.length} runs`);

  const t0 = Date.now();
  const submitted = [];
  for (const lane of FAMILIES) {
    const res = mcp("run_batch", { projectId: lane.projectId, name: `cramp-c${level}-${lane.family}-${tag}`, inputs });
    console.log(`  submitted ${lane.family} (project ${lane.projectId}): batchId=${res.batchId}`);
    submitted.push({ ...lane, batchId: res.batchId });
  }
  for (const b of submitted) await pollBatch(b.batchId);
  const wallMs = Date.now() - t0;

  const batchIds = submitted.map((b) => b.batchId);
  const rows = await fetchRuns(batchIds);
  const stats = statsByFamily(rows);

  let allPass = true;
  const comparison = {};
  for (const f of FAMILIES) {
    const fam = f.family;
    const s = stats[fam];
    const base = baselineStats[fam]?.medianLatencyMs;
    const inflation = (s.medianLatencyMs != null && base) ? (s.medianLatencyMs - base) / base : null;
    const famPass = s.failed === 0 && inflation != null && inflation <= 0.10;
    if (!famPass) allPass = false;
    comparison[fam] = {
      medianLatencyMs: s.medianLatencyMs, baselineMedianMs: base,
      inflationPct: inflation != null ? +(inflation * 100).toFixed(1) : null,
      p95LatencyMs: s.p95LatencyMs, failed: s.failed, completed: s.completed, pass: famPass,
    };
  }

  const result = {
    date: new Date().toISOString(), concurrency: level, batchIds,
    wallMs, wallS: +(wallMs / 1000).toFixed(1), stats, comparison,
    verdict: allPass ? "PASS" : "FAIL",
  };
  mkdirSync(LOGDIR, { recursive: true });
  const outPath = join(LOGDIR, `cramp_c${level}_${tag}.json`);
  writeFileSync(outPath, JSON.stringify(result, null, 2) + "\n");

  console.log(`\n════════ c-ramp @ ${level} ════════`);
  console.log(`  wall-time: ${result.wallS}s`);
  for (const [fam, c] of Object.entries(comparison)) {
    console.log(`  ${fam.padEnd(8)} median=${c.medianLatencyMs}ms (base ${c.baselineMedianMs}ms, ${c.inflationPct}%)  p95=${c.p95LatencyMs}ms  failed=${c.failed}  ${c.pass ? "PASS" : "FAIL"}`);
  }
  console.log(`  VERDICT @ c=${level}: ${result.verdict}`);
  console.log(`  log: ${outPath}`);
}

const argv = process.argv.slice(2);
if (argv[0] === "--baseline") baseline().catch((e) => { console.error("CRAMP ERROR:", e.message); process.exit(1); });
else if (argv[0] === "--run") run(Number(argv[1])).catch((e) => { console.error("CRAMP ERROR:", e.message); process.exit(1); });
else console.log("usage: CRAMP_DB_URL=mysql://... node cramp_test.mjs --baseline | --run <level>");
