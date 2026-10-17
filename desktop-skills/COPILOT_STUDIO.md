# Deploying SPEAKMAN.AI skills to Microsoft Copilot Studio

A second, independent deployment target for the same skill packages documented in
[`README.md`](./README.md) (which covers Claude Desktop / Cowork). Copilot Studio is Microsoft's
product, not Anthropic's — skills are uploaded per-agent under that agent's **Skills** tab, and
the upload mechanics are different enough from Cowork's plugin flow to warrant their own notes.

**Confirmed working (2026-08-12):** `generate-sad` run end-to-end inside a live Copilot Studio
agent via zip upload, MCP connector attached, session completed successfully.

## Prerequisite: the MCP connector

Same requirement as Claude Desktop — every skill that calls `start_session` / `get_outputs` /
`submit_response` / `render_document` needs the SPEAKMAN.AI MCP server reachable from the agent.
Add it before uploading any skill; if those tools aren't available when a skill runs, the skill
itself should tell the user to add the connector first (this is already the standard first line
under "Prerequisites for this environment" in each `SKILL.md`).

### Exposing a local MCP server to Copilot Studio (2026-08-12)

Copilot Studio is a cloud service — it cannot reach `http://127.0.0.1:8000`, where the local
SPEAKMAN.AI server (`SpeakmanAI.exe` / `launcher.py`) actually listens. Two extra steps beyond
what Claude Desktop needs (Desktop can talk to `localhost` directly):

**From SPEAKMAN.AI Lite v1.5.0 the server refuses requests that arrive through a tunnel unless
Remote access is switched on and the request carries the access token.** Without that, the
tunnel gets `Remote access is off`. The setup page and the local API are never served through a
tunnel, only `/mcp` is. Tested 2026-10-17 on the Windows `SpeakmanAI.exe` with a public Microsoft
Dev Tunnel, with a Copilot Studio agent running a search and reading a session's outputs.

1. **Turn on Remote access.** On the computer that runs SpeakmanAI, open the setup page
   (`http://localhost:8000/setup`), find the Remote access section, turn it on and copy the
   token. A new token can be generated there at any time; the old one then stops working.
2. **Tunnel the local port to a public URL.** Forward port `8000` and make the tunnel public
   (tested with a Microsoft Dev Tunnel set to public access, which gives a URL like
   `https://<id>-8000.use.devtunnels.ms`). The MCP address is that URL followed by `/mcp`. Use it,
   not `localhost`, in Copilot Studio. The URL changes when the tunnel is recreated, so update the
   connector then. VS Code's Ports panel gives the same kind of URL; it has not been re-tested
   with the token.
3. **Add the MCP server in Copilot Studio.** Choose **API key** as the authentication, enter the
   header name `x-api-key`, and paste the token as the value. The server also accepts
   `Authorization: Bearer <token>`, but `x-api-key` is what was tested.
4. **Create the connection.** At the connection step create a new connection with a name and
   enter the key again. The tool list should load straight away.
5. **Check it works.** Ask the agent to find a session by a word in its title. It should list
   matching sessions and, if asked, the outputs of one.

Things that go wrong:

- **`Couldn't load MCP tools` with HTTP 401.** The request reached SpeakmanAI without the right
  token. Copilot Studio creates a new sub connection each time the MCP test is edited, and each one
  appears in the connection drop-down of the MCP edit tool. A stale one keeps its old key. Pick the
  connection that holds the current key, or create a new one and enter the key again. A key
  mistyped on the first try looked like this too.
- **`Remote access is off`.** Turn it on in the setup page (step 1).
- **`A valid access token is required`.** The token is missing or does not match the current one.
- **The test panel replies `Not Acceptable: Client must accept text/event-stream`.** Harmless. The
  panel's plain JSON test does not ask for that response type. It also shows the request got past
  the token check. The agent's real calls work.
- **A browser-based test page fails with `Failed to fetch`.** A browser sends a preflight request
  with no token first, and the server answers it 401 without cross-origin headers. This is not a
  Copilot Studio problem. Test from Copilot Studio itself or with `curl`.
- **Checking what arrived.** Refused remote requests are logged to
  `%USERPROFILE%\.speakmanai\speakmanai.log` with which headers were present, never their
  values. This needs a build from 2026-10-17 or later (`dist\v1.5.0-guard2` or newer).

The token is the only thing protecting the endpoint, so treat it like a password. Generate a new
one on the setup page after sharing it in a screenshot, chat or ticket, and turn Remote access off
when you are not using the tunnel.

## Two upload paths — pick based on skill complexity

Copilot Studio's Skills → Upload accepts either a single `.md` file, or a `.zip`. Which one a
given skill needs depends on whether it bundles extra files beyond `SKILL.md` itself:

| Skill | Bundles extra files? | Upload as |
|---|---|---|
| `generate-sad` | Yes — `prompts/sad_agent_prompt.md` | `.zip` |
| `generate-compliance-report` | Yes — `prompts/compliance_agent_prompt.md` | `.zip` |
| `generate-speakmanai-code` | Yes — `CONTRIBUTING.md` | `.zip` |
| All other 14 skills (`generate-requirements`, `generate-ux-design`, `pentest`, etc.) | No — self-contained in one file | Plain `.md` — upload `SKILL.md` directly |

For the zip path: Microsoft's own guidance for Copilot Studio skill packages recommends `SKILL.md`
at the zip root, but the confirmed-working `generate-sad` upload above actually used the
Claude-Desktop-shaped zip instead — `SKILL.md` nested one level down inside a `generate-sad/`
folder (same shape `New-SkillZip` in `build.ps1` already produces for `generate-sad.zip` /
`generate-compliance-report.zip` / `generate-speakmanai-code.zip`). Copilot Studio accepted it
without complaint, so that nested shape is kept rather than introducing an untested flat-root
variant — if a future upload rejects a zip, flattening `SKILL.md` to the true root is the first
thing to try.

## Installing all 17 skills

No equivalent to Cowork's single-plugin-installs-everything pattern — Copilot Studio's Skills tab
is a manual drag-and-drop UI, one skill at a time, with no bulk-import mechanism found. `build.ps1`
produces `copilot-studio-skills.zip` for exactly this: unzip it locally, then drag each of the 18
items (14 `.md` files, 3 `.zip` files, and its own `INSTRUCTIONS.md`) into Skills → Upload
individually. Seventeen uploads, not one — no further trick found to reduce that on this platform.

## Open questions — not yet tested

- **`generate-ux-design`'s review step.** Same gap noted for Cowork in `README.md` — it publishes
  each mockup as an Artifact for human review in Claude Code; whether Copilot Studio has an
  equivalent inline-preview capability, or the skill just falls back to raw saved HTML, is
  unverified.
- **`pentest` / `pentest-execute`.** Same gap as Cowork — these lean on Claude Code's
  Agent/Task subagent-dispatch mechanism, which has no obvious Copilot Studio equivalent.
  Validate specifically before trusting this pair for a real engagement.

## Resolved gaps (carried over from README.md's Known Gaps)

- **PDF generation** — no longer applicable. `generate-sad`/`generate-compliance-report` render
  HTML via the SPEAKMAN.AI MCP server's `render_document` tool (server-side, no local
  Python/Node/puppeteer dependency), which is exactly what made Copilot Studio deployment
  possible in the first place — its skill runtime can't be assumed to shell out to either.
- **Local branding/template directory** — also no longer applicable, for the same reason: no
  filesystem convention to resolve. `render_document` renders a plain "SPEAKMAN.AI" text
  wordmark by default (no embedded logo image — this also keeps the response small: a full test
  document is ~1,400 tokens, versus ~57,000 for the original unoptimized embedded-PNG version). A
  calling agent that wants different branding edits the returned HTML directly (swap the
  `.wordmark` div for an `<img>`, or change its color/text) rather than needing a bundled
  template file.
