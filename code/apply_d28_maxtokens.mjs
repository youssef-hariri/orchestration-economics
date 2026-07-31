#!/usr/bin/env node
// D28: raise maxTokens 2048 -> 8192 on all 30 fixed confirmatory pipelines.
// Trigger: kimi-k2.6/k3 hidden reasoning counts against the completion budget;
// at 2048 the team-cell refiner exhausted the budget on reasoning and returned
// EMPTY visible content (verified: kimi solo at maxTokens=100 -> empty; at
// 8192 -> full 8.5k-char response). Author decision D28 (2026-07-31): uniform
// 8192 across ALL families (models cannot observe the cap; uniformity avoids
// a family-confounded budget difference). Token usage remains the measured
// cost DV regardless of cap.
//
// Idempotent: skips entries already at maxTokens 8192.

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REGISTRY = join(__dirname, "..", "pipelines", "fixed", "fixed_pipelines_registry.json");
const MCP_CALL = join(__dirname, "..", "..", "..", "scripts", "mcp-call.mjs");
const NEW_MAX = 8192;

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
  if (def.steps.every((s) => s.maxTokens === NEW_MAX)) {
    console.log(`SKIP  ${def.name} (project ${entry.projectId}) — already maxTokens=${NEW_MAX}`);
    skipped++;
    continue;
  }
  const newSteps = def.steps.map((s) => ({ ...s, maxTokens: NEW_MAX }));
  const res = mcp("update_pipeline", { id: entry.projectId, steps: newSteps });
  if (res.stepCount !== newSteps.length) {
    throw new Error(`step count mismatch on project ${entry.projectId}: sent ${newSteps.length}, got ${res.stepCount}`);
  }
  def.steps = newSteps;
  def.description = def.description.replace("maxTokens=2048", `maxTokens=${NEW_MAX}`);
  entry.d28AppliedAt = new Date().toISOString();
  console.log(`OK    ${def.name} (project ${entry.projectId}) — ${newSteps.length} step(s) → maxTokens=${NEW_MAX}`);
  updated++;
}

registry.d28 = {
  decision: "D28",
  date: "2026-07-31",
  change: `maxTokens 2048 -> ${NEW_MAX} on all fixed pipelines (uniform across families)`,
  reason: "kimi hidden reasoning exhausts a 2048 completion budget in team cells, yielding empty visible output; uniform raise avoids family-confounded budget difference; cap is unobservable to models",
};
writeFileSync(REGISTRY, JSON.stringify(registry, null, 2) + "\n");
console.log(`\nDone: ${updated} updated, ${skipped} skipped. Registry patched.`);
