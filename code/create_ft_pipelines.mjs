#!/usr/bin/env node
// create_ft_pipelines.mjs — create the F-T-N / F-T-P pipelines for the 2
// families selected by the pre-registered rule (strongest Western frontier by
// F-S-N Novelty + Kimi V3). Reads config/selected_ft_families.json.
//
// Mirrors create_pipelines.mjs structure (team = builder/critic/refiner,
// frontier model, persona congruent mapping). Appends to the fixed registry.
//
// Usage:
//   node code/create_ft_pipelines.mjs --dry-run   # print definitions only
//   node code/create_ft_pipelines.mjs             # create + archive registry

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.join(HERE, "..");
const WORKSPACE = path.join(REPO, "..", "..");
const MCP_CALL = path.join(WORKSPACE, "scripts", "mcp-call.mjs");
const REGISTRY = path.join(REPO, "pipelines", "fixed", "fixed_pipelines_registry.json");
const SELECTED = path.join(REPO, "config", "selected_ft_families.json");

const config = JSON.parse(fs.readFileSync(path.join(REPO, "config", "experiment_config.json"), "utf8"));
const personas = JSON.parse(fs.readFileSync(path.join(REPO, "data", "personas", "cultural_personas.json"), "utf8"));
const personaById = Object.fromEntries(personas.map((p) => [p.id, p.description]));
const selected = JSON.parse(fs.readFileSync(SELECTED, "utf8")).selected_families;

const PROVIDER_IDS = { gpt: 15, claude: 16, gemini: 14, kimi: 12, qwen: 17 };

const ROLE_PROMPTS = {
  builder:
    "You are a Builder agent. Create an initial, comprehensive response to the user's request. Focus on completeness and accuracy. Produce a well-structured draft.",
  critic:
    "You are a Critic agent. Review the provided output and identify weaknesses, errors, or areas for improvement. Be specific. End with Overall Assessment: PASS, NEEDS_WORK, or MAJOR_REVISIONS.",
  refiner:
    "You are a Refiner agent. Improve the provided output based on the feedback. Address each criticism systematically. Produce a significantly improved version.",
};

const GEN = config.generation;
const TEMP = String(GEN.temperature);
const MAXTOK = GEN.max_tokens;
const MAP = config.persona_role_mapping_congruent;

function step(name, role, systemPrompt, model) {
  return { name, role, systemPrompt, stepType: "agent", model, temperature: TEMP, maxTokens: MAXTOK };
}

function teamSteps(model, persona) {
  return ["builder", "critic", "refiner"].map((role) => {
    const base = ROLE_PROMPTS[role];
    const prompt = persona ? `${personaById[MAP[role]]}\n\n${base}` : base;
    const name = role.charAt(0).toUpperCase() + role.slice(1);
    return step(name, role, prompt, model);
  });
}

// F-T cells: frontier tier, team structure, persona N/P.
const FT_CELLS = [
  { cell: "F-T-N", tier: "frontier", structure: "team", persona: false },
  { cell: "F-T-P", tier: "frontier", structure: "team", persona: true },
];

const famByFamily = Object.fromEntries(config.tiers.families.map((f) => [f.family, f]));

const definitions = [];
for (const famName of selected) {
  const fam = famByFamily[famName];
  if (!fam) throw new Error(`selected family ${famName} not found in config.tiers.families`);
  const providerId = PROVIDER_IDS[famName];
  if (!providerId) throw new Error(`no provider id mapped for family ${famName}`);
  for (const c of FT_CELLS) {
    const model = fam.frontier; // frontier tier
    const steps = teamSteps(model, c.persona);
    definitions.push({
      name: `oe-${famName}-${c.cell}`,
      description:
        `orchestration-economics fixed confirmatory pipeline | cell=${c.cell} family=${famName} ` +
        `provider=${fam.provider} model=${model} temp=${TEMP} maxTokens=${MAXTOK} | ` +
        `config version ${config.version} | F-T family selected by preregistered rule (F-S-N novelty)`,
      defaultModel: model,
      defaultProviderId: providerId,
      steps,
      _meta: { cell: c.cell, family: famName, provider: fam.provider, tier: c.tier, structure: c.structure, persona: c.persona },
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
  if (parsed.structuredContent) return parsed.structuredContent;
  const text = parsed.content?.find((b) => b.type === "text")?.text;
  try { return JSON.parse(text); } catch { return { raw: text ?? out }; }
}

const dryRun = process.argv.includes("--dry-run");
if (dryRun) {
  console.log(JSON.stringify(definitions, null, 2));
  console.log(`\n${definitions.length} F-T pipeline definitions (dry run — nothing created).`);
  process.exit(0);
}

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
    fs.writeFileSync(REGISTRY, JSON.stringify(registry, null, 2));
  } catch (e) {
    console.error(`FAIL  ${def.name}: ${e.message}`);
  }
  await new Promise((r) => setTimeout(r, 750));
}

console.log(`\nRegistry: ${path.relative(REPO, REGISTRY)} (${registry.created.length} pipelines archived).`);
