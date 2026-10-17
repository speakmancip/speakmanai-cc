'use strict';
// Bridge between a stdio MCP client (the Claude app) and the SPEAKMAN.AI server on this computer,
// which speaks MCP over HTTP at http://127.0.0.1:<port>/mcp. No dependencies: Node 18+ has fetch.
// One JSON-RPC message per line in, one per line out.

const readline = require('readline');

const PORT = Number(process.env.SPEAKMANAI_PORT) || 8000;
const URL_ = `http://127.0.0.1:${PORT}/mcp`;
let sessionId = null;

function send(message) {
  process.stdout.write(JSON.stringify(message) + '\n');
}

function reportFailure(id, text) {
  if (id !== undefined && id !== null) {
    send({ jsonrpc: '2.0', id, error: { code: -32000, message: text } });
  } else {
    process.stderr.write(text + '\n');
  }
}

// A streamed answer is a list of events separated by blank lines; the JSON is on the data: lines.
function readEvents(text) {
  const out = [];
  for (const block of text.split(/\r?\n\r?\n/)) {
    const data = block
      .split(/\r?\n/)
      .filter((l) => l.startsWith('data:'))
      .map((l) => l.slice(5).replace(/^ /, ''))
      .join('\n');
    if (!data) continue;
    try { out.push(JSON.parse(data)); } catch (e) { /* not a message, ignore */ }
  }
  return out;
}

async function forward(line) {
  let message;
  try { message = JSON.parse(line); } catch (e) { return; }
  const id = Array.isArray(message) ? undefined : message.id;

  const headers = { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream' };
  if (sessionId) headers['Mcp-Session-Id'] = sessionId;

  let res;
  try {
    res = await fetch(URL_, { method: 'POST', headers, body: line });
  } catch (e) {
    reportFailure(id, `SPEAKMAN.AI is not running on port ${PORT}. Start SpeakmanAI.exe, check the port on its setup page, then try again.`);
    return;
  }

  const newSession = res.headers.get('mcp-session-id');
  if (newSession) sessionId = newSession;

  if (res.status === 202 || res.status === 204) return; // a notification: nothing to return
  const body = await res.text();
  if (!res.ok) {
    reportFailure(id, `SPEAKMAN.AI answered with status ${res.status}. ${body.slice(0, 300)}`);
    return;
  }
  const type = (res.headers.get('content-type') || '').toLowerCase();
  let replies;
  if (type.includes('text/event-stream')) {
    replies = readEvents(body);
  } else {
    try { replies = [].concat(JSON.parse(body)); } catch (e) { replies = []; }
  }
  for (const reply of replies) send(reply);
}

const pending = new Set();
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
  if (!line.trim()) return;
  const p = forward(line).catch((e) => process.stderr.write(String(e) + '\n'));
  pending.add(p);
  p.finally(() => pending.delete(p));
});
rl.on('close', async () => {
  await Promise.all(pending);
  process.exit(0);
});
