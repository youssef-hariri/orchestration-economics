#!/usr/bin/env node
// create_pipelines.mjs — Phase 0 step 3 (RESEARCH-PAPER-PLAN.md §6).
//
// Deterministically generates the 30 FIXED confirmatory pipelines
// (5 families x {C-S-N, C-S-P, C-T-N, C-T-P, F-S-N, F-S-P}) and creates
// them on production DeeWaanAI via the MCP create_pipeline tool.
//
// Deliberately NOT created here (deferred, with reasons archived below):
//   F-T-N / F-T-P — family pair fixed by preregistered rule AFTER F-S-N
//                   Novelty is known (strongest Western frontier + Kimi).
//   A5 / A8       — bound to the single special-arm cheap family, frozen
//                   at the Phase 0 pilot.
//   A6            — token budget derives from pooled C-T-P median cost
//                   (needs main-run data).
//   A7            — pipelines are designed per problem at run time by the
//                   pinned designer (kimi-k3, temp 0); nothing fixed to
//                   pre-create.
//
// Design constants (preregistered):
//   - model-homogeneous teams; step.model pinned explicitly on every step
//     AND project.defaultModel + project.defaultProviderId set (belt and
//     braces against provider fallback).
//   - generation temp 0.7, max_tokens 2048 (experiment_config.json).
//   - role prompts = DeeWaanAI canonical Builder/Critic/Refiner templates
//     (api/routers/project.ts), verbatim; persona cells prepend the
//     verbatim persona text + a blank line.
//   - congruent mapping: builder=Culture_5, critic=Culture_Expert,
//     refiner=Culture_11; solo persona = Culture_5.
//
// Usage:
//   node code/create_pipelines.mjs --dry-run   # print definitions only
//   node code/create_pipelines.mjs             # create + archive registry
//
// Output: pipelines/fixed/fixed_pipelines_registry.json (record of truth).

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.join(HERE, "..");
const WORKSPACE = path.join(REPO, "..", "..");
const MCP_CALL = path.join(WORKSPACE, "scripts", "mcp-call.mjs");
const REGISTRY = path.join(REPO, "pipelines", "fixed", "fixed_pipelines_registry.json");

const config = JSON.parse(fs.readFileSync(path.join(REPO, "config", "experiment_config.json"), "utf8"));
const personas = JSON.parse(fs.readFileSync(path.join(REPO, "data", "personas", "cultural_personas.json"), "utf8"));
const personaById = Object.fromEntries(personas.map((p) => [p.id, p.description]));

// Production provider ids for this account (verified via get_settings 2026-07-30).
const PROVIDER_IDS = { gpt: 15, claude: 16, gemini: 14, kimi: 12, qwen: 17 };

// DeeWaanAI canonical role templates — verbatim from api/routers/project.ts.
const ROLE_PROMPTS = {
  builder:
    "You are a Builder agent. Create an initial, comprehensive response to the user's request. Focus on completeness and accuracy. Produce a well-structured draft.",
  critic:
    "You are a Critic agent. Review the provided output and identify weaknesses, errors, or areas for improvement. Be specific. End with Overall Assessment: PASS, NEEDS_WORK, or MAJOR_REVISIONS.",
  refiner:
    "You are a Refiner agent. Improve the provided output based on the feedback. Address each criticism systematically. Produce a significantly improved version.",
};

// Neutral solo prompt for persona=none cells (fixed Phase-0 string; frozen at
// preregistration). Task-only, no persona/culture/expertise content, so the
// persona contrast is attributable to the persona text alone.
const SOLO_NEUTRAL_PROMPT =
  "You will be presented with a business problem. Analyze the situation and propose solutions. Provide a complete, well-structured response.";

const GEN = config.generation; // { temperature: 0.7, max_tokens: 2048, ... }
const TEMP = String(GEN.temperature);
const MAXTOK = GEN.max_tokens;
const MAP = config.persona_role_mapping_congruent; // builder/critic/refiner -> persona id

function step(name, role, systemPrompt, model) {
  return { name, role, systemPrompt, stepType: "agent", model, temperature: TEMP, maxTokens: MAXTOK };
}

function soloSteps(model, persona) {
  const prompt = persona ? personaById[MAP.builder] : SOLO_NEUTRAL_PROMPT;
  return [step("Solo", "solo", prompt, model)];
}

function teamSteps(model, persona) {
  return ["builder", "critic", "refiner"].map((role) => {
    const base = ROLE_PROMPTS[role];
    const prompt = persona ? `${personaById[MAP[role]]}\n\n${base}` : base;
    const name = role.charAt(0).toUpperCase() + role.slice(1);
    return step(name, role, prompt, model);
  });
}

const CELLS = [
  { cell: "C-S-N", tier: "cheap", structure: "solo", persona: false },
  { cell: "C-S-P", tier: "cheap", structure: "solo", persona: true },
  { cell: "C-T-N", tier: "cheap", structure: "team", persona: false },
  { cell: "C-T-P", tier: "cheap", structure: "team", persona: true },
  { cell: "F-S-N", tier: "frontier", structure: "solo", persona: false },
  { cell: "F-S-P", tier: "frontier", structure: "solo", persona: true },
];

const definitions = [];
for (const fam of config.tiers.families) {
  const providerId = PROVIDER_IDS[fam.family];
  if (!providerId) throw new Error(`no provider id mapped for family ${fam.family}`);
  for (const c of CELLS) {
    const model = c.tier === "frontier" ? fam.frontier : fam.cheap_sibling;
    const steps = c.structure === "solo" ? soloSteps(model, c.persona) : teamSteps(model, c.persona);
    definitions.push({
      name: `oe-${fam.family}-${c.cell}`,
      description:
        `orchestration-economics fixed confirmatory pipeline | cell=${c.cell} family=${fam.family} ` +
        `provider=${fam.provider} model=${model} temp=${TEMP} maxTokens=${MAXTOK} | ` +
        `config version ${config.version}`,
      defaultModel: model,
      defaultProviderId: providerId,
      steps,
      _meta: { cell: c.cell, family: fam.family, provider: fam.provider, tier: c.tier, structure: c.structure, persona: c.persona },
    });
  }
}

function mcp(tool, args) {
  const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
  });
  const parsed = JSON.parse(out);
  if (parsed.isError) throw new Error(`MCP ${tool} error: ${JSON.stringify(parsed.content)}`);
  // tools/call result: prefer structuredContent, else parse first text block.
  if (parsed.structuredContent) return parsed.structuredContent;
  const text = parsed.content?.find((b) => b.type === "text")?.text;
  try { return JSON.parse(text); } catch { return { raw: text ?? out }; }
}

const dryRun = process.argv.includes("--dry-run");
if (dryRun) {
  console.log(JSON.stringify(definitions, null, 2));
  console.log(`\n${definitions.length} pipeline definitions (dry run — nothing created).`);
  process.exit(0);
}

// Idempotency: skip names that already exist on the account.
let existingNames = new Set();
try {
  const listed = mcp("list_pipelines", {});
  const raw = JSON.stringify(listed);
  for (const m of raw.matchAll(/"name"\s*:\s*"(oe-[^"]+)"/g)) existingNames.add(m[1]);
} catch (e) {
  console.warn(`list_pipelines failed (${e.message}); proceeding without skip-list.`);
}

const registry = fs.existsSync(REGISTRY)
  ? JSON.parse(fs.readFileSync(REGISTRY, "utf8"))
  : { created: [], config_version: config.version };

for (const def of definitions) {
  if (existingNames.has(def.name)) {
    console.log(`SKIP  ${def.name} (already exists)`);
    continue;
  }
  const { _meta, ...payload } = def;
  try {
    const res = mcp("create_pipeline", payload);
    console.log(`OK    ${def.name} -> project ${res.id} (${res.stepCount} steps)`);
    registry.created.push({
      projectId: res.id,
      createdAt: new Date().toISOString(),
      definition: def,
    });
    fs.writeFileSync(REGISTRY, JSON.stringify(registry, null, 2)); // write-through after each create
  } catch (e) {
    console.error(`FAIL  ${def.name}: ${e.message}`);
  }
  await new Promise((r) => setTimeout(r, 750)); // rate-limit hygiene
}

console.log(`\nRegistry: ${path.relative(REPO, REGISTRY)} (${registry.created.length} pipelines archived).`);
