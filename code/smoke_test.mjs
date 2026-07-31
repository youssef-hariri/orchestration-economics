#!/usr/bin/env node
// Phase 0 §6 step 4: smoke test — run each of the 30 fixed confirmatory
// pipelines ONCE on a single short smoke problem (NOT from the experimental
// problem set, to avoid contaminating pre-registered stimuli).
//
// For each pipeline: run_pipeline → poll run_status to a terminal state →
// record status, per-step tokens/latency, totals. On failure, fetch the real
// error from the public run event stream (run_status only has a generic msg).
//
// Output: runs/logs/smoke_test_<date>.json (full record) + console table.
// Sequential on purpose (respects provider throttles; this is not a benchmark).

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const REGISTRY = join(ROOT, "pipelines", "fixed", "fixed_pipelines_registry.json");
const MCP_CALL = join(ROOT, "..", "..", "scripts", "mcp-call.mjs");
const STREAM_BASE = "https://deewaanai-production.up.railway.app/api/stream";

// Deliberately NOT one of the 30 experimental problems.
const SMOKE_PROBLEM =
  "SMOKE TEST (not an experimental stimulus): A neighborhood coffee shop has seen a 20% drop in weekday morning sales after a competitor opened nearby. Propose a brief course of action.";

const POLL_INTERVAL_MS = 4000;
const RUN_TIMEOUT_MS = 6 * 60 * 1000; // team pipelines: 3 sequential LLM calls

function mcp(tool, args) {
  const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
    encoding: "utf8",
    timeout: 90_000,
  });
  const parsed = JSON.parse(out);
  if (parsed.isError) throw new Error(`${tool} failed: ${parsed.content?.[0]?.text}`);
  return JSON.parse(parsed.content[0].text);
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function streamError(runId) {
  if (!Number.isInteger(runId)) return null;
  let out = "";
  try {
    out = execFileSync(
      "curl",
      ["-sN", "--max-time", "10", `${STREAM_BASE}/${runId}`],
      { encoding: "utf8", timeout: 15_000 },
    );
  } catch (e) {
    // curl exits 28 on --max-time; the replayed events are already in stdout
    out = e.stdout ?? "";
  }
  try {
    const line = out
      .split("\n")
      .find((l) => l.includes("step_error") || l.includes("pipeline_error"));
    if (!line) return null;
    const evt = JSON.parse(line.replace(/^data: /, ""));
    return evt.error ?? null;
  } catch {
    return null;
  }
}

const registry = JSON.parse(readFileSync(REGISTRY, "utf8"));
const results = [];

for (const entry of registry.created) {
  const def = entry.definition;
  process.stdout.write(`RUN   ${def.name} (project ${entry.projectId}) ... `);
  let rec = { projectId: entry.projectId, name: def.name, cell: def._meta.cell, family: def._meta.family };
  try {
    const { runId } = mcp("run_pipeline", { projectId: entry.projectId, input: SMOKE_PROBLEM });
    rec.runId = runId;
    const deadline = Date.now() + RUN_TIMEOUT_MS;
    let status;
    while (Date.now() < deadline) {
      await sleep(POLL_INTERVAL_MS);
      status = mcp("run_status", { runId });
      if (status.status === "completed" || status.status === "failed") break;
    }
    rec.status = status?.status ?? "timeout";
    rec.totalTokensUsed = status?.totalTokensUsed ?? null;
    rec.totalLatencyMs = status?.totalLatencyMs ?? null;
    rec.steps = (status?.steps ?? []).map((s) => ({
      step: s.step, agentRole: s.agentRole, status: s.status,
      tokensUsed: s.tokensUsed, latencyMs: s.latencyMs,
    }));
    if (rec.status === "failed") rec.realError = streamError(runId);
    if (rec.status === "completed") {
      rec.finalResponseChars = (status.finalResponse ?? "").length;
    }
  } catch (e) {
    rec.status = "error";
    rec.realError = e.message.slice(0, 300);
  }
  const tok = rec.totalTokensUsed ?? "-";
  const lat = rec.totalLatencyMs ?? "-";
  console.log(`${rec.status}  tokens=${tok}  latency=${lat}ms  runId=${rec.runId ?? "-"}${rec.realError ? `  ERROR: ${rec.realError}` : ""}`);
  results.push(rec);
}

const passed = results.filter((r) => r.status === "completed").length;
const summary = {
  date: new Date().toISOString(),
  purpose: "Phase 0 smoke test — 1 non-experimental problem per fixed pipeline, post-D27 (temp=1)",
  smokeProblem: SMOKE_PROBLEM,
  passed,
  failed: results.length - passed,
  results,
};

mkdirSync(join(ROOT, "runs", "logs"), { recursive: true });
const outPath = join(ROOT, "runs", "logs", `smoke_test_${new Date().toISOString().slice(0, 10)}.json`);
writeFileSync(outPath, JSON.stringify(summary, null, 2) + "\n");
console.log(`\n${passed}/${results.length} passed. Log: ${outPath}`);
process.exit(passed === results.length ? 0 : 1);
