# SPEAKMAN.AI extension for the Claude app

A Claude Desktop extension (`.mcpb`) that connects the Claude app to `SpeakmanAI.exe` running on the same computer. It adds no tools. `server/index.js` reads each request from the app, posts it to `http://127.0.0.1:<port>/mcp`, and returns the answer. It has no dependencies and runs on the Node that ships with the Claude app.

For install steps see `../desktop-skills/CLAUDE_APP.md`.

| File | What it is |
|---|---|
| `manifest.json` | Extension manifest (v0.3). One setting: the port, default 8000 |
| `server/index.js` | The bridge |
| `speakmanai-local.mcpb` | The packed extension: a zip of the two files above |
| `test_bridge.py` | Checks the bridge against a running server: `python test_bridge.py <port>` |

## Rebuild

From this folder, with the files above (not the `.mcpb` itself) in place:

```
npx -y @anthropic-ai/mcpb validate manifest.json
npx -y @anthropic-ai/mcpb pack . speakmanai-local.mcpb
```

Packing from this folder also puts `README.md`, `test_bridge.py` and the old `.mcpb` into the bundle. Copy `manifest.json` and `server/` to an empty folder and pack from there to get the 2 kB bundle.

## Status

Version 0.1.0, unsigned. Tested 2026-10-16 on a standard Windows account with the unsigned v1.5.0 exe. Not tested: macOS, the Claude app's behavior on update, and publishing to Anthropic's extension directory.
