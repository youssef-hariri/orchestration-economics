#!/usr/bin/env node
// Phase 0 §6 — granular archival of pilot runs.
//
// Pulls the FULL execution history of every pilot run that has a runId
// (completed AND failed — failed runs keep their partial steps/responses, which
// we need to diagnose the C-T team-cell failures) via the `export_run` MCP tool
// and writes one JSON per run to runs/granular/. Each archive contains:
//   run            — swarm_runs row (status, totals, execution_state, run_params)
//   agentRuns[]    — every step: role, system/user prompt, context_input,
//                    tokens_used, latency_ms, model_used, provider_used
//   agentResponses[] — every response: response_type, full content, metadata
//
// This is the granular cost-accounting + qualitative-analysis source of record
// on the local machine (the platform DB holds the live copy).
//
// Latency-insensitive → concurrent (worker pool). Resumable: existing files are
// skipped. Transient network errors retry with backoff (mirrors pilot_run.mjs).
//
// Usage: node code/archive_runs.mjs

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync, mkdirSync, renameSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const GEN_LOG = join(ROOT, "runs", "logs", "pilot_gen_2026-07-31.json");
const OUT_DIR = join(ROOT, "runs", "granular");
const MCP_CALL = join(ROOT, "..", "..", "scripts", "mcp-call.mjs");

const CONCURRENCY = 8;
const RETRY_BACKOFF_S = [5, 15, 30, 60];

function mcp(tool, args) {
  let lastErr;
  for (let attempt = 0; attempt <= RETRY_BACKOFF_S.length; attempt++) {
    try {
      const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
        encoding: "utf8",
        timeout: 120_000,
        maxBuffer: 64 * 1024 * 1024, // granular payloads can be large
      });
      const parsed = JSON.parse(out);
      if (parsed.isError) throw new Error(`${tool} failed: ${parsed.content?.[0]?.text}`);
      return JSON.parse(parsed.content[0].text);
    } catch (e) {
      lastErr = e;
      const msg = String(e?.message ?? e);
      const transient =
        msg.includes("Command failed") || msg.includes("fetch failed") ||
        msg.includes("ETIMEDOUT") || msg.includes("ECONNRESET") ||
        msg.includes("ECONNREFUSED") || msg.includes("ENOTFOUND") ||
        msg.includes("EAI_AGAIN") || msg.includes("socket hang up");
      if (!transient) throw e;
      if (attempt < RETRY_BACKOFF_S.length) {
        console.error(`  [retry] ${tool} attempt ${attempt + 1} transient (${msg.slice(0, 70)}); sleeping ${RETRY_BACKOFF_S[attempt]}s`);
        execFileSync("sleep", [String(RETRY_BACKOFF_S[attempt])]);
      }
    }
  }
  throw lastErr;
}

const safe = (s) => String(s).replace(/[^a-zA-Z0-9_-]+/g, "_");

async function archiveOne(rec) {
  const file = join(OUT_DIR, `${safe(rec.name)}__${safe(rec.problemId)}__run${rec.runId}.json`);
  if (existsSync(file)) return { rec, status: "skipped" };
  try {
    const data = mcp("export_run", { runId: rec.runId });
    const payload = {
      archivedAtUtc: new Date().toISOString(),
      pilotName: rec.name,
      cell: rec.cell,
      family: rec.family,
      problemId: rec.problemId,
      projectId: rec.projectId,
      runId: rec.runId,
      pilotStatus: rec.status,
      export: data,
    };
    const tmp = `${file}.tmp`;
    writeFileSync(tmp, JSON.stringify(payload, null, 2) + "\n");
    renameSync(tmp, file);
    return { rec, status: "archived", steps: data.agentRuns?.length ?? 0, responses: data.agentResponses?.length ?? 0 };
  } catch (e) {
    return { rec, status: "error", error: String(e?.message ?? e).slice(0, 200) };
  }
}

async function main() {
  mkdirSync(OUT_DIR, { recursive: true });
  const gen = JSON.parse(readFileSync(GEN_LOG, "utf8"));
  const targets = gen.results.filter((r) => Number.isInteger(r.runId));
  console.log(`Archiving ${targets.length} runs (with runId) → ${OUT_DIR} @ concurrency ${CONCURRENCY}`);

  let archived = 0, skipped = 0, errored = 0;
  let i = 0;
  async function worker() {
    while (i < targets.length) {
      const rec = targets[i++];
      const res = await archiveOne(rec);
      if (res.status === "archived") { archived++; console.log(`  archived run ${res.rec.runId} ${res.rec.name} (${res.steps} steps, ${res.responses} responses)`); }
      else if (res.status === "skipped") { skipped++; }
      else { errored++; console.error(`  ERROR run ${res.rec.runId} ${res.rec.name}: ${res.error}`); }
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCY }, worker));
  console.log(`\nDone. archived=${archived} skipped=${skipped} errored=${errored} → ${OUT_DIR}`);
}

main().catch((e) => { console.error(e); process.exit(1); });
