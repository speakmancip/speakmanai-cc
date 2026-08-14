# speakmanai-sdlc — Claude Desktop plugin

The Claude Desktop / claude.ai counterpart to this repo's `.claude/skills/`. Claude Desktop
skills run in Anthropic's own sandboxed VM (fresh per conversation), not on your machine, so
they can't reach `~/.claude/speakmanai-cc` the way the Claude Code skills do. Every skill in
here is self-contained instead: 14 of the 17 are a single `SKILL.md`; `generate-sad` and
`generate-compliance-report` each also bundle a `prompts/` folder (their document-synthesis
instructions), and `generate-speakmanai-code` bundles a `CONTRIBUTING.md`.

## What's in here

```
desktop-skills/
├── build.ps1                    ← regenerates the zips below from source
├── org-plugins/speakmanai-sdlc/ ← the plugin: all 17 SDLC skills, one upload
│   ├── .claude-plugin/plugin.json
│   ├── version.json
│   └── skills/<name>/SKILL.md   ← one per skill, self-contained
├── generate-sad/                ← standalone copy, for the Skills-only fallback
└── generate-compliance-report/  ← standalone copy, for the Skills-only fallback
```

`generate-sad` and `generate-compliance-report` are the only two skills that needed adapting
from their Claude Code version (they're the two that generate a document: synthesis via
`prompts/*_agent_prompt.md`, then rendering via the SPEAKMAN.AI MCP server's `render_document`
tool). The other 15 skills — including
`generate-project-brief` (Phase 0, idea intake) and `generate-ux-design` (Phase 2.5, screen
inventory + design mockups) — were already self-contained and are carried over unmodified from
`.claude/skills/`.

## Installing (recommended): the plugin, one upload

Requires **Cowork** (Claude Desktop's agentic workspace) — check for a Cowork tab/mode
separate from plain chat. If your Desktop build doesn't have one, use the per-skill fallback
below instead.

1. Run `desktop-skills/build.ps1` (or use the `speakmanai-sdlc.zip` already there if you
   haven't changed anything).
2. In Claude Desktop: **Cowork → Settings → Plugins → Upload**, select `speakmanai-sdlc.zip`.
3. All 17 SDLC skills are now available in that conversation — Claude picks the right one
   based on your request (there's no `/slash-command` triggering on Desktop the way Code has
   it, so just describe what you want: "generate a SAD for...", "give me UAT tests for...").

**Updating:** bump the `version` string in both `org-plugins/speakmanai-sdlc/.claude-plugin/plugin.json`
and `version.json` (any change is picked up as a new version — there's no ordering, so even a
downgrade string counts as an update), rebuild with `build.ps1`, and re-upload. Uninstall the
old copy first if the UI doesn't treat the re-upload as a replace.

## Installing (fallback): individual skills via Settings → Skills

If Cowork/Plugins isn't available, each skill can be uploaded on its own through
**Settings → Skills → Upload** — but that flow accepts exactly one `SKILL.md` per zip, so this
means one upload per skill you want, not one for the whole set.

- `generate-sad.zip`, `generate-compliance-report.zip`, and `generate-speakmanai-code.zip` are
  pre-built by `build.ps1`.
- For any other skill, zip the corresponding folder under
  `org-plugins/speakmanai-sdlc/skills/<name>/` directly — each is already self-contained. The
  zip must contain the skill folder itself at its root (not just `SKILL.md` loose), and entries
  need forward-slash paths — `Compress-Archive` on Windows emits backslashes, which some
  unzip tools on Anthropic's end may not handle. Use `build.ps1`'s `New-SkillZip` function as
  a template if you need to zip one manually, or copy the folder into `desktop-skills/` and add
  a line to `build.ps1`.

See also: [`COPILOT_STUDIO.md`](./COPILOT_STUDIO.md) for deploying these same skill packages to
Microsoft Copilot Studio instead of/alongside Claude Desktop.

## Known gaps / things to verify before relying on this

- ~~**PDF generation is best-effort.**~~ Resolved (2026-08-12): `generate-sad` and
  `generate-compliance-report` no longer generate a PDF or depend on Node/puppeteer at all —
  document rendering (Markdown → branded HTML) now happens server-side via the SPEAKMAN.AI MCP
  server's `render_document` tool, so there's no longer a sandbox-capability question here. See
  `LITE_ENHANCEMENTS.md` in the main `speakmanai_lite` repo for the full change.
- **`generate-ux-design`'s review step is unverified in Cowork.** In Claude Code it publishes
  each mockup as an Artifact for the human to actually look at before approving. Whether Cowork
  has an equivalent capability hasn't been tested — if not, the skill still has the mockups'
  raw HTML to fall back on (saved to disk, per its own Step 4), just without a rendered preview
  in the conversation itself.
- **`pentest` / `pentest-execute` are unverified in Cowork.** In Claude Code these lean on the
  Agent/Task subagent-dispatch mechanism and expect scanning tools to be reachable from the
  sandbox. Whether Cowork's VM has equivalent subagent dispatch and tooling hasn't been tested
  — validate this pair specifically before trusting it for a real engagement.
- **The MCP connector is a separate prerequisite.** Every skill that calls `start_session` /
  `get_outputs` / `submit_response` needs the SPEAKMAN.AI MCP connector added under
  Settings → Connectors — the plugin doesn't provision that for you.
- **No true org-wide push on this channel.** The `org-plugins/` filesystem + MDM mechanism
  Anthropic documents for centrally-managed Desktop deployments requires the enterprise
  "third-party inference" build; it isn't available on the standard Microsoft
  Store/consumer Desktop build. On that build, every user uploads the plugin themselves —
  this whole setup gets you from 17 uploads down to 1, not down to 0.
