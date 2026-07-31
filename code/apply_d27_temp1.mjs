#!/usr/bin/env node
// D27: set temperature="1" on all 30 fixed confirmatory pipelines.
// Rationale: OpenAI gpt-5.6 and Moonshot kimi APIs enforce temperature=1
// (400 on any other value). Author decision D27 (2026-07-31): apply temp=1
// uniformly across ALL families for cross-family comparability, rather than
// per-family heterogeneous temperatures. Documented deviation from the
// pre-registered generation.temperature=0.7.
//
// Idempotent: safe to re-run; skips entries already at temp "1".

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REGISTRY = join(__dirname, "..", "pipelines", "fixed", "fixed_pipelines_registry.json");
const MCP_CALL = join(__dirname, "..", "..", "..", "scripts", "mcp-call.mjs");

function mcp(tool, args) {
  const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
    encoding: "utf8",
    timeout: 60_000,
  });
  const parsed = JSON.parse(out);
  if (parsed.isError) throw new Error(`${tool} failed: ${parsed.content?.[0]?.text}`);
  return JSON.parse(parsed.content[0].text);
}

const registry = JSON.parse(readFileSync(REGISTRY, "utf8"));
let updated = 0, skipped = 0;

for (const entry of registry.created) {
  const def = entry.definition;
  const already = def.steps.every((s) => s.temperature === "1");
  if (already) {
    console.log(`SKIP  ${def.name} (project ${entry.projectId}) — already temp=1`);
    skipped++;
    continue;
  }
  const newSteps = def.steps.map((s) => ({ ...s, temperature: "1" }));
  const res = mcp("update_pipeline", { id: entry.projectId, steps: newSteps });
  if (res.stepCount !== newSteps.length) {
    throw new Error(`step count mismatch on project ${entry.projectId}: sent ${newSteps.length}, got ${res.stepCount}`);
  }
  // Write-through: keep the registry as the exact record of what is deployed
  def.steps = newSteps;
  def.description = def.description.replace("temp=0.7", "temp=1");
  entry.d27AppliedAt = new Date().toISOString();
  console.log(`OK    ${def.name} (project ${entry.projectId}) — ${newSteps.length} step(s) → temp=1`);
  updated++;
}

registry.d27 = {
  decision: "D27",
  date: "2026-07-31",
  change: "temperature 0.7 -> 1 on all fixed pipelines (uniform across families)",
  reason: "OpenAI gpt-5.6 and Moonshot kimi APIs enforce temperature=1; uniform temp=1 chosen over per-family heterogeneity",
};
writeFileSync(REGISTRY, JSON.stringify(registry, null, 2) + "\n");
console.log(`\nDone: ${updated} updated, ${skipped} skipped. Registry patched.`);
