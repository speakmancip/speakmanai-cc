# speakmanai-sdlc — Claude Desktop plugin

The Claude Desktop / claude.ai counterpart to this repo's `.claude/skills/`. Claude Desktop
skills run in Anthropic's own sandboxed VM (fresh per conversation), not on your machine, so
they can't reach `~/.claude/speakmanai-cc` the way the Claude Code skills do. Every skill in
here is self-contained instead: each `skills/<name>/` folder bundles its own `prompts/`,
`scripts/`, and `templates/` rather than depending on a separate host install step.

## What's in here

```
desktop-skills/
├── build.ps1                    ← regenerates the zips below from source
├── org-plugins/speakmanai-sdlc/ ← the plugin: all 14 SDLC skills, one upload
│   ├── .claude-plugin/plugin.json
│   ├── version.json
│   └── skills/<name>/SKILL.md   ← one per skill, self-contained
├── generate-sad/                ← standalone copy, for the Skills-only fallback
└── generate-compliance-report/  ← standalone copy, for the Skills-only fallback
```

`generate-sad` and `generate-compliance-report` are the only two skills that needed adapting
from their Claude Code version (they're the two that generate a document via
`prompts/*_agent_prompt.md` + `scripts/doc_writer.py`). The other 12 skills were already
self-contained and are carried over unmodified from `.claude/skills/`.

## Installing (recommended): the plugin, one upload

Requires **Cowork** (Claude Desktop's agentic workspace) — check for a Cowork tab/mode
separate from plain chat. If your Desktop build doesn't have one, use the per-skill fallback
below instead.

1. Run `desktop-skills/build.ps1` (or use the `speakmanai-sdlc.zip` already there if you
   haven't changed anything).
2. In Claude Desktop: **Cowork → Settings → Plugins → Upload**, select `speakmanai-sdlc.zip`.
3. All 14 SDLC skills are now available in that conversation — Claude picks the right one
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

- `generate-sad.zip` and `generate-compliance-report.zip` are pre-built by `build.ps1`.
- For any other skill, zip the corresponding folder under
  `org-plugins/speakmanai-sdlc/skills/<name>/` directly — each is already self-contained. The
  zip must contain the skill folder itself at its root (not just `SKILL.md` loose), and entries
  need forward-slash paths — `Compress-Archive` on Windows emits backslashes, which some
  unzip tools on Anthropic's end may not handle. Use `build.ps1`'s `New-SkillZip` function as
  a template if you need to zip one manually, or copy the folder into `desktop-skills/` and add
  a line to `build.ps1`.

## Known gaps / things to verify before relying on this

- **PDF generation is best-effort.** `doc_writer.py` needs Node.js + puppeteer in the sandbox
  to render a PDF; that's not guaranteed to be present in Cowork's VM. It degrades gracefully
  — you still get the Markdown and HTML, and the user can print the HTML to PDF from their own
  browser. Confirmed on at least one test machine that it does fall back cleanly (no
  puppeteer, HTML delivered).
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
  this whole setup gets you from 14 uploads down to 1, not down to 0.
