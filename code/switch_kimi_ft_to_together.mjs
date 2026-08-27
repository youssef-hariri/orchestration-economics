#!/usr/bin/env node
// switch_kimi_ft_to_together.mjs — migrate the kimi F-T-N / F-T-P pipelines
// from the native Moonshot provider (credits exhausted) to Together.ai
// hosting moonshotai/Kimi-K3. Model identity is preserved (same model family
// and version, different hosting endpoint); the routing change is documented
// for the paper.
//
// - Updates the 2 kimi F-T pipelines via update_pipeline (defaultProviderId,
//   defaultModel, full step-chain replacement with identical prompts).
// - Updates the fixed registry entries (definition.defaultModel,
//   defaultProviderId, _meta.routedVia).
//
// Usage: node code/switch_kimi_ft_to_together.mjs [--dry-run]

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
const TOGETHER_KIMI_K3 = "moonshotai/Kimi-K3"; // verified in Together model catalog

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
const kimiFt = registry.created.filter(
  (p) => p.definition?._meta?.family === "kimi" && ["F-T-N", "F-T-P"].includes(p.definition?._meta?.cell),
);
if (kimiFt.length !== 2) throw new Error(`expected 2 kimi F-T entries in registry, found ${kimiFt.length}`);

const dryRun = process.argv.includes("--dry-run");

for (const entry of kimiFt) {
  const def = entry.definition;
  // Rebuild the step chain identically, only swapping the model string.
  const steps = def.steps.map((s) => ({ ...s, model: TOGETHER_KIMI_K3 }));
  const payload = {
    id: Number(entry.projectId),
    description:
      (def.description || "").split(" | routedVia:")[0] +
      ` | routedVia:together.ai (Moonshot credits exhausted 2026-08-03; model identity preserved)`,
    defaultModel: TOGETHER_KIMI_K3,
    defaultProviderId: TOGETHER_PROVIDER_ID,
    steps,
  };
  if (dryRun) {
    console.log(`DRY ${def.name} -> provider ${TOGETHER_PROVIDER_ID}, model ${TOGETHER_KIMI_K3}`);
    continue;
  }
  const res = mcp("update_pipeline", payload);
  console.log(`OK  ${def.name} (project ${entry.projectId}) -> together/${TOGETHER_KIMI_K3}`);
  // Archive the routing change in the registry.
  def.defaultModel = TOGETHER_KIMI_K3;
  def.defaultProviderId = TOGETHER_PROVIDER_ID;
  def.steps = steps;
  def.description = payload.description;
  def._meta.routedVia = "together.ai";
  def._meta.nativeProvider = "moonshot (credits exhausted)";
  entry.updatedAtUtc = new Date().toISOString();
  fs.writeFileSync(REGISTRY, JSON.stringify(registry, null, 2)); // write-through
}

console.log(dryRun ? "\ndry run — nothing changed." : "\nRegistry updated.");
