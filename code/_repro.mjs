// One-shot diagnostic: reproduce the oe-claude-C-T-N / BP_8 failure LIVE and
// capture the literal pipeline_error message from the SSE stream.
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const HOST = "https://deewaanai-production.up.railway.app";
const BASE = HOST + "/mcp";
const TOKEN_URL = HOST + "/oauth/token";
const TOKEN_FILE = "/Users/youssefhariri/Documents/app 25/.deewaanai-test-token.json";
const tokens = JSON.parse(fs.readFileSync(TOKEN_FILE, "utf8"));

async function refresh() {
  const res = await fetch(TOKEN_URL, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ grant_type: "refresh_token", client_id: tokens.client_id, refresh_token: tokens.refresh_token }) });
  if (!res.ok) { console.error("refresh failed", res.status, await res.text()); process.exit(1); }
  const fresh = await res.json(); fresh.client_id = tokens.client_id; fresh.obtained_at = new Date().toISOString();
  fs.writeFileSync(TOKEN_FILE, JSON.stringify(fresh, null, 2), { mode: 0o600 });
  return fresh.access_token;
}
let access_token = tokens.access_token;
if (Date.now() - new Date(tokens.obtained_at).getTime() > 50 * 60 * 1000) access_token = await refresh();

let sessionId = null, id = 0;
async function rpc(method, params, notif = false) {
  const body = { jsonrpc: "2.0", method, params }; if (!notif) body.id = ++id;
  const headers = { "content-type": "application/json", "accept": "application/json, text/event-stream", "authorization": `Bearer ${access_token}` };
  if (sessionId) headers["mcp-session-id"] = sessionId;
  const res = await fetch(BASE, { method: "POST", headers, body: JSON.stringify(body) });
  const sid = res.headers.get("mcp-session-id"); if (sid) sessionId = sid;
  if (notif || res.status === 202) return null;
  const text = await res.text();
  const dl = text.split("\n").filter((l) => l.startsWith("data:")).map((l) => l.slice(5).trim());
  const payload = dl.length ? dl[dl.length - 1] : text;
  try { return JSON.parse(payload); } catch { return { raw: text, status: res.status }; }
}

const input = JSON.parse(fs.readFileSync(fileURLToPath(new URL("./_bp8_input.json", import.meta.url)), "utf8"));
const PROJECT_ID = 21; // oe-claude-C-T-N

await rpc("initialize", { protocolVersion: "2025-03-26", capabilities: {}, clientInfo: { name: "repro", version: "1.0" } });
await rpc("notifications/initialized", {}, true);

console.log("triggering run_pipeline on project", PROJECT_ID, "(oe-claude-C-T-N) with BP_8 input...");
const r = await rpc("tools/call", { name: "run_pipeline", arguments: { projectId: PROJECT_ID, input } });
const txt = r?.result?.content?.[0]?.text ?? "";
let runId;
try { runId = JSON.parse(txt).runId; } catch { const m = txt.match(/runId["\s:]+(\d+)/); runId = m && +m[1]; }
if (!runId) { console.error("no runId; raw:", JSON.stringify(r?.result ?? r).slice(0, 400)); process.exit(1); }
console.log("runId =", runId, "— subscribing to live SSE stream...");

const sseRes = await fetch(`${HOST}/api/stream/${runId}`, { headers: { "authorization": `Bearer ${access_token}`, "accept": "text/event-stream" } });
console.log("SSE status:", sseRes.status);
if (!sseRes.ok || !sseRes.body) { console.error("SSE failed:", (await sseRes.text().catch(() => "")).slice(0, 300)); process.exit(1); }

const reader = sseRes.body.getReader();
const dec = new TextDecoder();
let buf = "";
const deadline = Date.now() + 9 * 60 * 1000;
let done = false;
while (Date.now() < deadline && !done) {
  const { value, done: rd } = await reader.read();
  if (rd) break;
  buf += dec.decode(value, { stream: true });
  let idx;
  while ((idx = buf.indexOf("\n\n")) >= 0) {
    const chunk = buf.slice(0, idx); buf = buf.slice(idx + 2);
    for (const line of chunk.split("\n")) {
      if (!line.startsWith("data:")) continue;
      const data = line.slice(5).trim();
      if (!data) continue;
      try {
        const ev = JSON.parse(data);
        const t = ev.type;
        if (t === "pipeline_error") {
          fs.writeFileSync(fileURLToPath(new URL("./_repro_error.json", import.meta.url)), JSON.stringify(ev, null, 2));
          console.log(">>> PIPELINE_ERROR.error FIELD:\n" + ev.error);
          done = true;
        } else if (t === "pipeline_complete") { console.log(">>> PIPELINE_COMPLETE (did NOT fail this time)"); done = true; }
        else if (t === "step_start") console.log(`  [step_start] step=${ev.step} role=${ev.agentRole} name=${ev.agentName}`);
        else console.log("  [event]", t);
      } catch { /* non-json keepalive */ }
    }
  }
}
if (!done) console.log("TIMEOUT waiting for terminal event");
console.log("done. repro runId =", runId);
