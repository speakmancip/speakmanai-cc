"""The extension bridge (server/index.js) against a dev server. argv: port (a dev server must be running there)."""
import json, os, subprocess, sys

port = sys.argv[1]
BRIDGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server", "index.js")
fails = 0
def check(name, ok, extra=""):
    global fails
    print(("ok   " if ok else "FAIL ") + name + (" " + extra if extra else ""))
    fails += 0 if ok else 1

def run(messages, p):
    env = dict(os.environ, SPEAKMANAI_PORT=str(p))
    stdin = "".join(json.dumps(m) + "\n" for m in messages)
    r = subprocess.run(["node", BRIDGE], input=stdin, capture_output=True, text=True, env=env, timeout=60)
    out = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    return out, r.stderr

init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "bridge-test", "version": "0"}}}
note = {"jsonrpc": "2.0", "method": "notifications/initialized"}
tools = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
call = {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_sessions", "arguments": {"limit": 3}}}

out, err = run([init, note, tools, call], port)
by_id = {m.get("id"): m for m in out}
check("one reply per request (3), none for the notification", len(out) == 3, f"got {len(out)}")
check("initialize answered", "result" in by_id.get(1, {}) and "serverInfo" in by_id[1]["result"])
names = [t["name"] for t in by_id.get(2, {}).get("result", {}).get("tools", [])]
check("tools/list returns the server's tools", "start_session" in names and "list_sessions" in names, f"{len(names)} tools")
res = by_id.get(3, {}).get("result", {})
check("tools/call list_sessions returns content", bool(res.get("content")) and not res.get("isError"))
check("nothing written to stderr", err.strip() == "", err[:200])

out, err = run([init, tools], 59999)
check("server not running: each request gets a clear error", len(out) == 2 and all("error" in m for m in out))
check("error names the problem", "not running" in out[0]["error"]["message"] if out else False)

print("fails:", fails)
sys.exit(1 if fails else 0)
