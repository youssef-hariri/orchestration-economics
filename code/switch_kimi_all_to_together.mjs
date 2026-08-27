#!/usr/bin/env node
// switch_kimi_all_to_together.mjs — migrate ALL remaining kimi pipelines
// (C-S-N/P, C-T-N/P on kimi-k2.6; F-S-N/P on kimi-k3) from the native Moonshot
// provider (credits exhausted again, 2026-08-04) to Together.ai hosting.
//
// Model identity is preserved — Together catalog verified 2026-08-04 to host
// both pinned versions:
//   kimi-k2.6 -> moonshotai/Kimi-K2.6
//   kimi-k3   -> moonshotai/Kimi-K3
// This extends the disclosed pilot-era F-T migration (switch_kimi_ft_together.mjs)
// to the full kimi family; documented in MANIFEST as a routing-only deviation.
//
// Usage: node code/switch_kimi_all_to_together.mjs [--dry-run]

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.join(HERE, "..");
const WORKSPACE = path.join(REPO, "..", "..");
const MCP_CALL = path.join(WORKSPACE, "scripts", "mcp-call.mjs");
const REGISTRY = path.join(REPO, "pipelines", "fixed", "fixed_pipelines_registry.json");

const TOGETHER_PROVIDER_ID = 18; // Together.ai (get_settings, 2026-08-03)
const MODEL_MAP = {
  "kimi-k2.6": "moonshotai/Kimi-K2.6", // verified in Together catalog 2026-08-04
  "kimi-k3": "moonshotai/Kimi-K3",     // verified in Together catalog + pilot F-T usage
};

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

const registry = JSON.parse(fs.readFileSync(REGISTRY, "utf8"));
const targets = registry.created.filter(
  (p) => p.definition?._meta?.family === "kimi" && p.definition?._meta?.routedVia !== "together.ai",
);
if (targets.length !== 6) throw new Error(`expected 6 non-Together kimi entries, found ${targets.length}`);

const dryRun = process.argv.includes("--dry-run");

for (const entry of targets) {
  const def = entry.definition;
  const toModel = MODEL_MAP[def.defaultModel];
  if (!toModel) throw new Error(`no Together mapping for ${def.defaultModel} (${def.name})`);
  const steps = def.steps.map((s) => ({ ...s, model: toModel }));
  const payload = {
    id: Number(entry.projectId),
    description:
      (def.description || "").split(" | routedVia:")[0] +
      ` | routedVia:together.ai (Moonshot credits exhausted 2026-08-04; model identity preserved)`,
    defaultModel: toModel,
    defaultProviderId: TOGETHER_PROVIDER_ID,
    steps,
  };
  if (dryRun) {
    console.log(`DRY ${def.name} (${def.defaultModel}) -> provider ${TOGETHER_PROVIDER_ID}, model ${toModel}`);
    continue;
  }
  mcp("update_pipeline", payload);
  console.log(`OK  ${def.name} (project ${entry.projectId}) ${def.defaultModel} -> together/${toModel}`);
  def.defaultModel = toModel;
  def.defaultProviderId = TOGETHER_PROVIDER_ID;
  def.steps = steps;
  def.description = payload.description;
  def._meta.routedVia = "together.ai";
  def._meta.nativeProvider = "moonshot (credits exhausted 2026-08-04)";
  entry.updatedAtUtc = new Date().toISOString();
  fs.writeFileSync(REGISTRY, JSON.stringify(registry, null, 2)); // write-through
}

console.log(dryRun ? "\ndry run — nothing changed." : "\nRegistry updated.");
