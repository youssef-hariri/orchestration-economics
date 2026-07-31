#!/usr/bin/env node
// Phase 0 §6 step 6: PILOT run (D32) — 30 fixed pipelines × 4 pilot problems
// × 1 rep = 120 runs, sequential, inside the D21 execution window
// (14:00–00:00 UTC; caller is responsible for the start time).
//
// Input rendering (D32.3): background_context + "\n\n" + business_problem,
// verbatim, no wrapper. Pilot data are G0 gate measurements only (D31/D32).
//
// Resumable: progress is flushed to the output file after every run; on
// restart, (projectId, problemId) pairs already recorded are skipped.
//
// Output: runs/logs/pilot_gen_2026-07-31.json — per-run status, per-step
// tokens/latency, full final response text (needed for judging), timestamps
// (started_at_utc for the D21 window ledger).

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const REGISTRY = join(ROOT, "pipelines", "fixed", "fixed_pipelines_registry.json");
const PILOT = join(ROOT, "config", "pilot_problems.json");
const MCP_CALL = join(ROOT, "..", "..", "scripts", "mcp-call.mjs");
const STREAM_BASE = "https://deewaanai-production.up.railway.app/api/stream";
const OUT = join(ROOT, "runs", "logs", "pilot_gen_2026-07-31.json");

const POLL_INTERVAL_MS = 5000;
const RUN_TIMEOUT_MS = 8 * 60 * 1000; // kimi teams observed up to ~4.3 min

function mcp(tool, args) {
  const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
    encoding: "utf8",
    timeout: 90_000,
  });
  const parsed = JSON.parse(out);
  if (parsed.isError) throw new Error(`${tool} failed: ${parsed.content?.[0]?.text}`);
  return JSON.parse(parsed.content[0].text);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function streamError(runId) {
  if (!Number.isInteger(runId)) return null;
  let out = "";
  try {
    out = execFileSync("curl", ["-sN", "--max-time", "10", `${STREAM_BASE}/${runId}`], {
      encoding: "utf8",
      timeout: 15_000,
    });
  } catch (e) {
    out = e.stdout ?? ""; // curl exit 28 on --max-time; data already in stdout
  }
  try {
    const line = out.split("\n").find((l) => l.includes("step_error") || l.includes("pipeline_error"));
    if (!line) return null;
    return JSON.parse(line.replace(/^data: /, "")).error ?? null;
  } catch {
    return null;
  }
}

const registry = JSON.parse(readFileSync(REGISTRY, "utf8"));
const pilot = JSON.parse(readFileSync(PILOT, "utf8"));

let summary;
if (existsSync(OUT)) {
  summary = JSON.parse(readFileSync(OUT, "utf8")); // resume
} else {
  summary = {
    purpose: "Phase 0 pilot (D32): 30 pipelines x 4 problems x 1 rep; G0 gate measurement only",
    renderingRule: "D32.3: background_context + '\\n\\n' + business_problem, verbatim",
    pilotProblems: pilot.pilot_problem_ids,
    startedAtUtc: new Date().toISOString(),
    results: [],
  };
}
const done = new Set(summary.results.map((r) => `${r.projectId}:${r.problemId}`));

function flush() {
  writeFileSync(OUT, JSON.stringify(summary, null, 2) + "\n");
}

// Problem-major order: each problem sweeps all 30 pipelines (spreads provider
// load; families alternate rather than hammering one provider 4x in a row).
for (const problemId of pilot.pilot_problem_ids) {
  const p = pilot.problems[problemId];
  const input = `${p.background_context}\n\n${p.business_problem}`;
  for (const entry of registry.created) {
    const key = `${entry.projectId}:${problemId}`;
    if (done.has(key)) continue;
    const def = entry.definition;
    process.stdout.write(`RUN ${problemId} ${def.name} (project ${entry.projectId}) ... `);
    const rec = {
      projectId: entry.projectId,
      name: def.name,
      cell: def._meta.cell,
      family: def._meta.family,
      problemId,
      startedAtUtc: new Date().toISOString(),
    };
    try {
      const { runId } = mcp("run_pipeline", { projectId: entry.projectId, input });
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
        step: s.step,
        agentRole: s.agentRole,
        status: s.status,
        tokensUsed: s.tokensUsed,
        latencyMs: s.latencyMs,
      }));
      if (rec.status === "failed") rec.realError = streamError(runId);
      if (rec.status === "completed") rec.finalResponse = status.finalResponse ?? "";
    } catch (e) {
      rec.status = "error";
      rec.realError = e.message.slice(0, 300);
    }
    rec.finishedAtUtc = new Date().toISOString();
    summary.results.push(rec);
    done.add(key);
    flush();
    console.log(
      `${rec.status}  tokens=${rec.totalTokensUsed ?? "-"}  latency=${rec.totalLatencyMs ?? "-"}ms  runId=${rec.runId ?? "-"}  final=${(rec.finalResponse ?? "").length}ch${rec.realError ? `  ERROR: ${rec.realError}` : ""}`,
    );
  }
}

const completed = summary.results.filter((r) => r.status === "completed" && (r.finalResponse ?? "").length > 0).length;
summary.finishedAtUtc = new Date().toISOString();
summary.completedNonEmpty = completed;
summary.total = summary.results.length;
flush();
console.log(`\n${completed}/${summary.results.length} completed with non-empty output. Log: ${OUT}`);
process.exit(completed === summary.results.length ? 0 : 1);
