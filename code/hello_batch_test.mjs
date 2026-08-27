#!/usr/bin/env node
// D34 Stage A — Hello-translation batch smoke test on PRODUCTION.
//
// Validates the Research-Mode batch infrastructure in real-world conditions:
//   run_batch -> queue -> worker -> real LLM call -> batch_status -> export.
// 5 family lanes (single-step solo C-S-N pipelines), 20 hello-translation
// inputs each = 100 independent runs (each run = 1 input, per D34).
// createBatch auto-sets stateless:true, so no cross-input contamination.
//
// Usage:
//   node hello_batch_test.mjs --poll <batchId>          # poll one existing batch
//   node hello_batch_test.mjs --validate                # 5 inputs on gpt lane, poll
//   node hello_batch_test.mjs                           # full 5x20 = 100 run smoke

import { execFileSync } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const MCP_CALL = join(ROOT, "..", "..", "scripts", "mcp-call.mjs");

// 5 family lanes: single-step solo C-S-N confirmatory pipelines (one per family).
const FAMILIES = [
  { family: "gpt", projectId: 13 },
  { family: "claude", projectId: 19 },
  { family: "gemini", projectId: 25 },
  { family: "kimi", projectId: 31 },
  { family: "qwen", projectId: 37 },
];

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

async function pollBatch(batchId, { intervalMs = 4000, timeoutMs = 15 * 60 * 1000 } = {}) {
  const deadline = Date.now() + timeoutMs;
  let status = null;
  while (Date.now() < deadline) {
    status = mcp("batch_status", { batchId });
    const done = `${status.completedRuns}/${status.totalRuns}`;
    process.stdout.write(`\r  batch ${batchId}: ${status.status}  ${done}  failed=${status.failedRuns}   `);
    if (TERMINAL.has(status.status)) { process.stdout.write("\n"); return status; }
    await sleep(intervalMs);
  }
  process.stdout.write("\n");
  return status ?? { status: "timeout" };
}

function summarizeBatch(batchId, label) {
  const status = mcp("batch_status", { batchId });
  let csv = "";
  try { csv = mcp("export_batch_results", { batchId }).csv ?? ""; } catch (e) { csv = `EXPORT ERROR: ${e.message}`; }
  const rows = csv.split("\n").filter(Boolean);
  const dataRows = rows.slice(1);
  const completed = dataRows.filter((r) => r.includes(",completed,")).length;
  // pull a sample final_response (4th quoted field) from the first completed row
  const sample = dataRows.find((r) => r.includes(",completed,")) ?? "";
  const sampleMatch = sample.match(/,"((?:[^"]|"")*)","(?:[^"]|"")*",\d+,\d+$/);
  return {
    label, batchId, status: status.status,
    totalRuns: status.totalRuns, completedRuns: status.completedRuns, failedRuns: status.failedRuns,
    totalTokensUsed: status.totalTokensUsed,
    csvCompletedRows: completed,
    sampleTranslation: sampleMatch ? sampleMatch[1].slice(0, 60) : "(none)",
    perRun: (status.runs ?? []).map((r) => ({ id: r.id, status: r.status, error: r.error })),
  };
}

async function main() {
  const argv = process.argv.slice(2);

  if (argv[0] === "--poll") {
    const batchId = Number(argv[1]);
    const final = await pollBatch(batchId);
    console.log(JSON.stringify(summarizeBatch(batchId, `poll-${batchId}`), null, 2));
    return;
  }

  const validateOnly = argv[0] === "--validate";
  const lanes = validateOnly ? FAMILIES.slice(0, 1) : FAMILIES;
  const inputs = validateOnly ? LANGS.slice(0, 5).map(inputFor) : LANGS.map(inputFor);
  const tag = new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-");

  console.log(`Hello batch smoke (${validateOnly ? "VALIDATION" : "FULL"}): ${lanes.length} lane(s) x ${inputs.length} input(s) = ${lanes.length * inputs.length} runs`);

  // Submit all batches first (they enqueue and drain concurrently per worker concurrency).
  const submitted = [];
  for (const lane of lanes) {
    const res = mcp("run_batch", {
      projectId: lane.projectId,
      name: `hello-smoke-${lane.family}-${tag}`,
      inputs,
    });
    console.log(`  submitted ${lane.family} (project ${lane.projectId}): batchId=${res.batchId} runs=${res.runIds.length}`);
    submitted.push({ ...lane, batchId: res.batchId, runIds: res.runIds });
  }

  // Poll all batches to terminal.
  for (const b of submitted) {
    console.log(`\npolling ${b.family} (batch ${b.batchId})...`);
    await pollBatch(b.batchId);
  }

  // Summarize + export.
  const summaries = submitted.map((b) => summarizeBatch(b.batchId, b.family));
  const totals = summaries.reduce((a, s) => ({
    total: a.total + s.totalRuns, completed: a.completed + s.completedRuns,
    failed: a.failed + s.failedRuns, tokens: a.tokens + (s.totalTokensUsed || 0),
  }), { total: 0, completed: 0, failed: 0, tokens: 0 });

  console.log("\n════════ RESULT ════════");
  for (const s of summaries) {
    console.log(`  ${s.label.padEnd(8)} batch=${s.batchId}  ${s.status.padEnd(22)}  ${s.completedRuns}/${s.totalRuns} ok  failed=${s.failedRuns}  tokens=${s.totalTokensUsed}  sample="${s.sampleTranslation}"`);
  }
  console.log(`  ── TOTAL: ${totals.completed}/${totals.total} completed, ${totals.failed} failed, ${totals.tokens} tokens`);
  const pass = totals.failed === 0 && totals.completed === totals.total;
  console.log(`  ── STAGE A VERDICT: ${pass ? "PASS (0 failures)" : "REVIEW (failures present)"}`);

  mkdirSync(join(ROOT, "runs", "logs"), { recursive: true });
  const outPath = join(ROOT, "runs", "logs", `hello_batch_${tag}.json`);
  writeFileSync(outPath, JSON.stringify({ date: new Date().toISOString(), mode: validateOnly ? "validate" : "full", totals, summaries }, null, 2) + "\n");
  console.log(`  log: ${outPath}`);
}

main().catch((e) => { console.error("HELLO BATCH ERROR:", e.message); process.exit(1); });
