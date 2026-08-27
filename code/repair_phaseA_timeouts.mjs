#!/usr/bin/env node
// repair_phaseA_timeouts.mjs — recover the Phase A "timeout" records.
//
// For each record with status "timeout" (runId known):
//   - poll run_status up to WAIT_MIN minutes
//   - completed server-side  -> patch record in place (status/finalResponse/tokens/steps)
//   - failed server-side     -> remove record (runner re-runs the pair)
//   - still running at end   -> remove record (runner re-runs the pair)
// Then clears finishedAtUtc so pilot_run_phaseA.mjs can be relaunched: its
// `done` set is rebuilt from the log, so removed pairs become new tasks and
// patched/kept pairs are skipped.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.join(HERE, "..");
const WORKSPACE = path.join(REPO, "..", "..");
const MCP_CALL = path.join(WORKSPACE, "scripts", "mcp-call.mjs");
const LOG = path.join(REPO, "runs", "logs", "pilot_phaseA_2026-08-03.json");
const WAIT_MIN = 10; // how long to keep polling runs still in flight

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function mcp(tool, args) {
  const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
  });
  const parsed = JSON.parse(out);
  if (parsed.isError) throw new Error(`MCP ${tool} error: ${JSON.stringify(parsed.content)}`);
  if (parsed.structuredContent) return parsed.structuredContent;
  const text = parsed.content?.find((b) => b.type === "text")?.text;
  try { return JSON.parse(text); } catch { return { raw: text ?? out }; }
}

function flush(summary) {
  const tmp = LOG + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(summary, null, 2) + "\n");
  fs.renameSync(tmp, LOG);
}

const summary = JSON.parse(fs.readFileSync(LOG, "utf8"));
const timeouts = summary.results.filter((r) => r.status === "timeout");
console.log(`${timeouts.length} timeout records to repair (polling up to ${WAIT_MIN} min)...`);

const deadline = Date.now() + WAIT_MIN * 60_000;
let patched = 0;
let removed = 0;

for (const rec of timeouts) {
  let status = null;
  while (Date.now() < deadline) {
    try {
      status = mcp("run_status", { runId: rec.runId });
    } catch (e) {
      console.error(`  run ${rec.runId}: run_status error: ${String(e?.message ?? e).slice(0, 120)}; retrying`);
      await sleep(15_000);
      continue;
    }
    if (status.status === "completed" || status.status === "failed") break;
    await sleep(10_000);
  }
  if (status?.status === "completed") {
    rec.status = "completed";
    rec.totalTokensUsed = status.totalTokensUsed ?? null;
    rec.totalLatencyMs = status.totalLatencyMs ?? null;
    rec.steps = (status.steps ?? []).map((s) => ({
      step: s.step, agentRole: s.agentRole, status: s.status,
      tokensUsed: s.tokensUsed, latencyMs: s.latencyMs,
    }));
    rec.finalResponse = status.finalResponse ?? "";
    rec.recoveredAtUtc = new Date().toISOString();
    patched++;
    console.log(`  RECOVERED run ${rec.runId} (${rec.cell}/${rec.family}/${rec.problemId}) tok=${rec.totalTokensUsed}`);
    flush(summary);
  } else {
    // failed or still running at deadline -> drop record, runner re-runs pair
    const i = summary.results.indexOf(rec);
    summary.results.splice(i, 1);
    removed++;
    console.log(`  REMOVED   run ${rec.runId} (${rec.cell}/${rec.family}/${rec.problemId}) server=${status?.status ?? "unknown"} -> will re-run`);
    flush(summary);
  }
}

summary.finishedAtUtc = null; // allow relaunch; runner rewrites it at the end
flush(summary);
console.log(`\nDone: ${patched} recovered, ${removed} removed (will re-run).`);
console.log(`Remaining records: ${summary.results.length}. Relaunch: node code/pilot_run_phaseA.mjs`);
