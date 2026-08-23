#!/usr/bin/env node
// wave_create_pipelines.mjs — Protocol 12 (OSF jg49x) pipeline setup.
//
// Builds the wave registry (pipelines/fixed/wave_pipelines_registry.json):
//   - Study-1 five families (gpt/claude/gemini/kimi/qwen): REUSE the frozen
//     Study-1 pipelines for the 3 core cells (identical instrument, D50).
//     The kimi entry is live-verified via get_project_settings to run on
//     Moonshot DIRECT (D48: K2.6 retired on Together 2026-08-19); if the
//     live route is wrong, a replacement pipeline is created instead.
//   - New five families (thinkingmachines/gpt-oss/gemma/mistral/minimax):
//     3 pipelines each (C-S-N, C-T-N, F-S-N), created via MCP with the same
//     canonical role prompts, temperature and max_tokens as Study 1.
//
// NEVER touches pipelines/fixed/fixed_pipelines_registry.json (Study-1 frozen).
//
// Provider ids for new families come from pipelines/fixed/wave_provider_ids.json
// (written by the t5 setup step after add_provider).
//
// Usage:
//   node code/wave_create_pipelines.mjs --dry-run
//   node code/wave_create_pipelines.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.join(HERE, "..");
const WORKSPACE = path.join(REPO, "..", "..");
const MCP_CALL = path.join(WORKSPACE, "scripts", "mcp-call.mjs");
const REGISTRY = path.join(REPO, "pipelines", "fixed", "wave_pipelines_registry.json");
const STUDY1_REGISTRY = path.join(REPO, "pipelines", "fixed", "fixed_pipelines_registry.json");
const PROVIDER_IDS_FILE = path.join(REPO, "pipelines", "fixed", "wave_provider_ids.json");

const config = JSON.parse(fs.readFileSync(path.join(REPO, "config", "experiment_config.json"), "utf8"));
const GEN = config.generation;
const TEMP = String(GEN.temperature);   // 1 (D27)
const MAXTOK = GEN.max_tokens;          // 8192 (D28)

// DeeWaanAI canonical role templates — verbatim from api/routers/project.ts
// (identical to Study 1, create_pipelines.mjs).
const ROLE_PROMPTS = {
  builder:
    "You are a Builder agent. Create an initial, comprehensive response to the user's request. Focus on completeness and accuracy. Produce a well-structured draft.",
  critic:
    "You are a Critic agent. Review the provided output and identify weaknesses, errors, or areas for improvement. Be specific. End with Overall Assessment: PASS, NEEDS_WORK, or MAJOR_REVISIONS.",
  refiner:
    "You are a Refiner agent. Improve the provided output based on the feedback. Address each criticism systematically. Produce a significantly improved version.",
};
const SOLO_NEUTRAL_PROMPT =
  "You will be presented with a business problem. Analyze the situation and propose solutions. Provide a complete, well-structured response.";

// Wave cells (D50: 3 core cells only; persona excluded).
const CELLS = [
  { cell: "C-S-N", tier: "cheap", structure: "solo" },
  { cell: "C-T-N", tier: "cheap", structure: "team" },
  { cell: "F-S-N", tier: "frontier", structure: "solo" },
];

// Study-1 families reused verbatim (frozen pipelines). EXCEPTION: kimi —
// the frozen Study-1 kimi pipelines were switched to Together hosting
// mid-Study-1 (2026-08-04 credit exhaustion; MANIFEST routing deviation),
// and kimi-k2.6 was RETIRED on Together 2026-08-19 (D48). The wave therefore
// gets 3 NEW kimi pipelines on the native Moonshot provider (id 12), identical
// prompts/temp/maxTokens — a routing-only deviation with Study-1 precedent.
const STUDY1_FAMILIES = ["gpt", "claude", "gemini", "qwen"];
const KIMI_PROVIDER = "kimi";

// New families: pinned models per Protocol 12 §3 (verified 2026-08-22/23).
// kimi included here (Moonshot-direct recreation; see STUDY1_FAMILIES note).
const NEW_FAMILIES = [
  { family: "kimi", provider: "moonshot", frontier: "kimi-k3", cheap: "kimi-k2.6" },
  { family: "thinkingmachines", provider: "together", frontier: "thinkingmachines/Inkling", cheap: "thinkingmachines/Inkling-Small" },
  { family: "gpt-oss", provider: "together", frontier: "openai/gpt-oss-120b", cheap: "openai/gpt-oss-20b" },
  { family: "gemma", provider: "together", frontier: "google/gemma-4-31B-it", cheap: "google/gemma-3n-E4B-it" },
  { family: "mistral", provider: "mistral", frontier: "mistral-medium-2604", cheap: "mistral-small-2603" },
  { family: "minimax", provider: "minimax", frontier: "MiniMax-M3", cheap: "MiniMax-M2.7" },
];

function step(name, role, systemPrompt, model) {
  return { name, role, systemPrompt, stepType: "agent", model, temperature: TEMP, maxTokens: MAXTOK };
}
function buildSteps(cellDef, model) {
  if (cellDef.structure === "solo") return [step("Solo", "solo", SOLO_NEUTRAL_PROMPT, model)];
  return ["builder", "critic", "refiner"].map((role) =>
    step(role.charAt(0).toUpperCase() + role.slice(1), role, ROLE_PROMPTS[role], model));
}

function mcp(tool, args) {
  const out = execFileSync("node", [MCP_CALL, tool, JSON.stringify(args)], {
    encoding: "utf8", timeout: 90_000, maxBuffer: 16 * 1024 * 1024,
  });
  const parsed = JSON.parse(out);
  if (parsed.isError) throw new Error(`MCP ${tool} error: ${JSON.stringify(parsed.content)}`);
  if (parsed.structuredContent) return parsed.structuredContent;
  const text = parsed.content?.find((b) => b.type === "text")?.text;
  try { return JSON.parse(text); } catch { return { raw: text ?? out }; }
}

const dryRun = process.argv.includes("--dry-run");

// ---------- Provider ids ----------
// Study-1 ids verified via get_settings 2026-07-30; new ids from t5 setup.
let providerIds = { gpt: 15, claude: 16, gemini: 14, kimi: 12, qwen: 17 };
if (fs.existsSync(PROVIDER_IDS_FILE)) {
  providerIds = { ...providerIds, ...JSON.parse(fs.readFileSync(PROVIDER_IDS_FILE, "utf8")) };
}

// ---------- Study-1 reuse entries ----------
const study1 = JSON.parse(fs.readFileSync(STUDY1_REGISTRY, "utf8"));
const study1ByName = Object.fromEntries(study1.created.map((e) => [e.definition.name, e]));

const registry = fs.existsSync(REGISTRY)
  ? JSON.parse(fs.readFileSync(REGISTRY, "utf8"))
  : { protocol: "12-PROTOCOL-WAVE-CONFIRMATORY-REPLICATION.md", osf: "jg49x", created: [] };
const haveKey = new Set(registry.created.map((e) => `${e.definition._meta.family}|${e.definition._meta.cell}`));
const save = () => fs.writeFileSync(REGISTRY, JSON.stringify(registry, null, 2));

for (const fam of STUDY1_FAMILIES) {
  for (const c of CELLS) {
    if (haveKey.has(`${fam}|${c.cell}`)) { console.log(`SKIP  ${fam}/${c.cell} (already in wave registry)`); continue; }
    const srcName = `oe-${fam}-${c.cell}`;
    const src = study1ByName[srcName];
    if (!src) { console.error(`FAIL  ${srcName}: not found in Study-1 frozen registry`); continue; }

    if (dryRun) { console.log(`REUSE ${fam}/${c.cell} -> project ${src.projectId} (study-1 frozen)`); continue; }
    registry.created.push({
      projectId: src.projectId, createdAt: new Date().toISOString(),
      definition: src.definition,
      _wave_source: `study1-reuse:${srcName}`,
    });
    save();
    console.log(`REUSE ${fam}/${c.cell} -> project ${src.projectId}`);
  }
}

// ---------- New families ----------
let existingNames = new Set();
if (!dryRun) {
  try {
    const listed = mcp("list_pipelines", {});
    for (const m of JSON.stringify(listed).matchAll(/"name"\s*:\s*"(oe-wave-[^"]+)"/g)) existingNames.add(m[1]);
  } catch (e) { console.warn(`list_pipelines failed (${e.message}); proceeding without skip-list.`); }
}

for (const fam of NEW_FAMILIES) {
  const providerId = providerIds[fam.provider] ?? providerIds[fam.family];
  if (!providerId) {
    console.error(`FAIL  ${fam.family}: provider id missing — add it to ${path.relative(REPO, PROVIDER_IDS_FILE)} after add_provider (t5)`);
    continue;
  }
  for (const c of CELLS) {
    if (haveKey.has(`${fam.family}|${c.cell}`)) { console.log(`SKIP  ${fam.family}/${c.cell} (already in wave registry)`); continue; }
    const model = c.tier === "frontier" ? fam.frontier : fam.cheap;
    const def = {
      name: `oe-wave-${fam.family}-${c.cell}`,
      description:
        `Protocol-12 wave pipeline | cell=${c.cell} family=${fam.family} provider=${fam.provider} ` +
        `model=${model} temp=${TEMP} maxTokens=${MAXTOK} | models pinned 2026-08-22/23 (D48)`,
      defaultModel: model,
      defaultProviderId: providerId,
      steps: buildSteps(c, model),
    };
    const meta = { cell: c.cell, family: fam.family, provider: fam.provider, tier: c.tier, structure: c.structure, persona: false };
    if (dryRun) { console.log(`NEW   ${def.name} (provider ${providerId}, ${def.steps.length} steps)`); continue; }
    if (existingNames.has(def.name)) { console.log(`SKIP  ${def.name} (already exists on platform)`); continue; }
    try {
      const res = mcp("create_pipeline", { ...def });
      registry.created.push({
        projectId: res.id, createdAt: new Date().toISOString(),
        definition: { ...def, _meta: meta },
        _wave_source: "created",
      });
      save();
      console.log(`OK    ${def.name} -> project ${res.id} (${def.steps.length} steps)`);
    } catch (e) {
      console.error(`FAIL  ${def.name}: ${e.message}`);
    }
    await new Promise((r) => setTimeout(r, 750));
  }
}

console.log(`\nWave registry: ${path.relative(REPO, REGISTRY)} (${registry.created.length} pipelines).`);
if (!dryRun && registry.created.length !== 30) {
  console.warn(`WARNING: expected 30 wave pipelines (10 families x 3 cells), have ${registry.created.length}.`);
}
