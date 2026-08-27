#!/usr/bin/env node
// reattach_timeout_runs.mjs — after the main batch, runs that TIMED OUT in our
// 20-min poll may still be finishing (or already finished) on the platform.
// Re-query run_status for every timeout record; if now completed, attach
// status/tokens/steps + full text via export_run (A1.1), rewrite the per-run
// file atomically. Nothing is touched for non-timeout records.
//
// Usage: node code/reattach_timeout_runs.mjs [--dry-run]

import { readFileSync, writeFileSync, readdirSync, renameSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { execFileSync } from "node:child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const RAW_DIR = join(ROOT, "runs", "raw", "main");
const MCP_CALL = join(ROOT, "..", "..", "scripts", "mcp-call.mjs");
const CAP = 16012;
const dryRun = process.argv.includes("--dry-run");

function mcp(tool, args) {
  const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
    encoding: "utf8", timeout: 90_000, maxBuffer: 32 * 1024 * 1024,
  });
  const parsed = JSON.parse(out);
  if (parsed.isError) throw new Error(`${tool} failed: ${parsed.content?.[0]?.text}`);
  return JSON.parse(parsed.content[0].text);
}

const files = readdirSync(RAW_DIR).filter((f) => f.endsWith(".json"));
let reattached = 0, stillRunning = 0, stillFailed = 0, noRunId = 0;
for (const f of files) {
  const path = join(RAW_DIR, f);
  const rec = JSON.parse(readFileSync(path, "utf8"));
  if (rec.status !== "timeout") continue;
  if (!Number.isInteger(rec.runId)) { noRunId++; continue; }
  let status;
  try { status = mcp("run_status", { runId: rec.runId }); }
  catch (e) { console.log(`ERR ${f}: ${String(e?.message ?? e).slice(0, 80)}`); continue; }
  if (status.status === "completed") {
    if (dryRun) { console.log(`DRY reattach ${f} (runId ${rec.runId})`); reattached++; continue; }
    rec.status = "completed";
    rec.totalTokensUsed = status.totalTokensUsed ?? null;
    rec.totalLatencyMs = status.totalLatencyMs ?? null;
    rec.steps = (status.steps ?? []).map((s) => ({
      step: s.step, agentRole: s.agentRole, status: s.status,
      tokensUsed: s.tokensUsed, latencyMs: s.latencyMs,
    }));
    const statusText = status.finalResponse ?? "";
    rec.truncatedAtSource = statusText.length === CAP;
    try {
      const exp = mcp("export_run", { runId: rec.runId });
      const content = (exp?.agentResponses?.[0]?.content) ?? "";
      rec.fulltextLen = content.length;
      rec.finalResponse = content.length >= statusText.length ? content : statusText;
      rec.fulltextSource = content.length >= statusText.length ? "export_run" : "run_status";
      const gfile = join(ROOT, "runs", "granular",
        `${rec.name}__${rec.problemId}__rep${rec.rep}__run${rec.runId}.json`);
      writeFileSync(`${gfile}.tmp`, JSON.stringify({
        archivedAtUtc: new Date().toISOString(), ...rec, export: exp,
      }, null, 2) + "\n");
      renameSync(`${gfile}.tmp`, gfile);
    } catch (e) {
      rec.finalResponse = statusText;
      rec.fulltextSource = "run_status_only";
      rec.archiveError = String(e?.message ?? e).slice(0, 200);
    }
    rec.reattachedAtUtc = new Date().toISOString();
    writeFileSync(`${path}.tmp`, JSON.stringify(rec, null, 2) + "\n");
    renameSync(`${path}.tmp`, path);
    reattached++;
    console.log(`OK  ${rec.cell}/${rec.family}/${rec.problemId}/r${rec.rep} reattached (len=${rec.fulltextLen ?? (rec.finalResponse ?? "").length})`);
  } else if (status.status === "running" || status.status === "queued") {
    stillRunning++;
  } else {
    rec.status = status.status ?? "failed";
    rec.realError = status.error ?? rec.realError ?? null;
    if (!dryRun) {
      rec.recheckedAtUtc = new Date().toISOString();
      writeFileSync(`${path}.tmp`, JSON.stringify(rec, null, 2) + "\n");
      renameSync(`${path}.tmp`, path);
    }
    stillFailed++;
  }
}
console.log(`\nsummary: reattached=${reattached} stillRunning=${stillRunning} stillFailed=${stillFailed} noRunId=${noRunId}`);
