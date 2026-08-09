# speakmanai-cc

Claude Code skills for the [SPEAKMAN.AI](https://speakman.ai) MCP server (cloud) or the [local self-hosted version](https://github.com/speakmancip/speakmanai-local). Together these skills cover the full SDLC — architecture, requirements, code generation, infrastructure, UAT, environment promotion, and pentesting — each orchestrating a full SPEAKMAN.AI session (where applicable), downloading agent outputs, and generating a locally-authored deliverable or codebase.

Read the writeup: [The SDLC as Claude Code Skills](https://consulting.speakman.ai/blogs/sdlc-as-claude-code-skills) on the SPEAKMAN.AI blog.

**New here?** Read **[PIPELINE.md](PIPELINE.md)** for the full phase-by-phase roadmap — what
each skill consumes and produces, and what order to run them in. Or run `/sdlc-pipeline` for
a guided walkthrough that drives every phase for you.

## Available Skills

### The SDLC pipeline (run in order — see [PIPELINE.md](PIPELINE.md))

| Phase | Skill | Command | Output |
|---|---|---|---|
| 0 — Idea Intake | Project Brief (Create / Update / Validate) | `/generate-project-brief` | `brief.md` — structured idea brief, ready to feed Phase 1 or a sizing/investment gate. Zero credits, no MCP session. |
| 1 — Architecture | Solution Architecture Document | `/generate-sad` | SAD — HTML + PDF draft, ready for architect review before ARB submission |
| 2 — Requirements | Requirements Engineer | `/generate-requirements` | Domain model, naming dictionary, use cases, API/DB schema, test strategy |
| 2.5 — UX Design | UX & Interface Design | `/generate-ux-design` | Screen inventory, Mermaid user flows, proposed design direction, self-contained HTML mockups for human review. Optional. |
| 3 — Code Generation | Code Generator (router + JS/Go/Python variants) | `/generate-speakmanai-code` | Working, milestone-gated, git-committed codebase |
| 4 — Infrastructure | Infrastructure & Hardening | `/generate-infrastructure` | Terraform (GCP/AWS/Azure) + pre-pentest security fixes |
| Gate | Environment Promotion | `/promote-environment` | Pass/block report — local→DEV, DEV→STG, STG→PROD |
| Gate | Penetration Test | `/pentest` (+ `/pentest-execute` worker) | Findings + report, via a [pentest-platform-companion](https://github.com/speakmancip/pentest-platform-companion) engagement |
| Gate | UAT Test Generator | `/generate-uat-tests` | Human-executable UAT test cases, traced to use cases |
| Guided | SDLC Shepherd | `/sdlc-pipeline` | Runs the phases above in order, carrying state between them |

### Adjacent tools (standalone — not part of the sequential pipeline)

| Skill | Command | Workflow | Output |
|---|---|---|---|
| Compliance Assessment Report | `/generate-compliance-report` | `MCP_COMPLIANCE_ASSESSMENT_V1` | Risk scores, gap analysis, remediation roadmap |
| Workflow Creator | `/generate-speakmanai-workflow` | `WORKFLOW_CREATOR_V1` | Workflow definition JSON, ready for DB import |
| Skill Workflow Creator | `/generate-speakmanai-skill-workflow` | `CLAUDE_SKILL_WORKFLOW_CREATOR_V1` | Delegate-first workflow definition JSON — agents that need external data/tools run directly via the connected coding agent instead of pausing for a human |

---

## Prerequisites

- [Claude Code](https://claude.ai/claude-code) installed
- SPEAKMAN.AI MCP server configured in your Claude Code settings
- Python 3.9+
- Node.js (for PDF generation — puppeteer is installed automatically by the install script)

**For the `/pentest` gate only:** a running instance of
[pentest-platform-companion](https://github.com/speakmancip/pentest-platform-companion) —
it owns engagement scope, gate approvals, and findings review for that skill. None of the
other skills need it.

---

## Install

Clone this repository, then run the install script from within it.

**Windows:**
```powershell
git clone https://github.com/speakmancip/speakmanai-cc.git
cd speakmanai-cc
.\install.ps1
```

**macOS / Linux:**
```bash
git clone https://github.com/speakmancip/speakmanai-cc.git
cd speakmanai-cc
chmod +x install.sh && ./install.sh
```

**Claude Desktop / claude.ai:** these skills also ship as a self-contained plugin — one upload
gets you all of them, no clone or install script needed. See
[`desktop-skills/README.md`](desktop-skills/README.md).

The install script does two things:

| What | Where |
|---|---|
| Skill files | `~/.claude/skills/` — available globally in every Claude Code session |
| Supporting assets (scripts, prompts, templates) | `~/.claude/speakmanai-cc/` — referenced by the skills at runtime |

Once installed, you can run the skills from **any project directory** — no need to keep the cloned repo around.

---

## Usage

Open Claude Code in any project directory and run:

```
/generate-sad
```

The skill will:

1. **Collect your business description** — paste text, provide a file path, URL, or any connected MCP resource (Google Drive, Confluence, RAG)
2. **Collect capabilities context** — same sources; Terraform files are parsed automatically to extract your current technology stack
3. **Run a SPEAKMAN.AI session** — polls until complete (~10 min)
4. **Download agent outputs** — saves raw outputs to `outputs/YYYY-MM-DD_{slug}/raw/` in your project
5. **Generate a local SAD** — authored from the agent outputs using the installed synthesis prompt
6. **Build HTML + PDF** — using your chosen template

The other skills follow the same pattern — see each skill's step-by-step instructions when you invoke them.

---

## Output Structure

Outputs are written to your project directory:

```
outputs/
└── 2026-03-22_my-project/
    ├── raw/
    │   ├── business_context_clarifier.txt
    │   ├── business_analyst.txt
    │   ├── business_application_architect.txt
    │   ├── technical_solution_architect.txt
    │   ├── compliance_officer.txt
    │   └── visualization_specialist.txt
    ├── my-project.md        ← Markdown SAD
    ├── my-project.html      ← Branded HTML
    └── my-project.pdf       ← Print-ready PDF
```

---

## Templates

| Template | Use |
|---|---|
| `default` | SPEAKMAN.AI branded |
| `corporate` | Your own brand |

Templates are installed to `~/.claude/speakmanai-cc/templates/`.

To use your corporate brand, add `logo.png` to `~/.claude/speakmanai-cc/templates/corporate/` and select `[corporate]` when prompted. See that directory's README for asset specs.

---

## Customising the Prompts

The synthesis prompts that drive local document generation are installed to `~/.claude/speakmanai-cc/prompts/`:

| File | Used by |
|---|---|
| `sad_agent_prompt.md` | `/generate-sad` |
| `compliance_agent_prompt.md` | `/generate-compliance-report` |

Edit these to match your organisation's documentation standards — section names, required tables, compliance frameworks, or house style. They are intentionally separated from the skill files so teams can version-control their own prompts independently.

---

## Running Scripts Directly

The processing scripts are installed to `~/.claude/speakmanai-cc/scripts/`.

**Pre-process Markdown** (strip heading numbers):
```bash
python ~/.claude/speakmanai-cc/scripts/preprocess.py outputs/2026-03-22_my-project/my-project.md
```

**Build HTML + PDF from existing Markdown:**
```bash
python ~/.claude/speakmanai-cc/scripts/doc_writer.py my-project_clean.md \
  --template ~/.claude/speakmanai-cc/templates/default \
  --output /absolute/path/to/outputs/2026-03-22_my-project/my-project \
  --yes
```

---

## Accepted Input Sources

The skills accept input from any source accessible in your Claude Code session:

| Source | Example |
|---|---|
| Plain text | Paste directly into the prompt |
| File | `/path/to/brief.md`, `requirements.pdf`, `systems.json` |
| Directory | `/docs/architecture/` — skill scans for relevant files |
| Terraform | `main.tf`, `terraform.tfstate` — stack extracted automatically |
| MCP resource | Google Drive folder, Confluence space, SharePoint library |
| RAG results | Document links or search output from a connected RAG system |
| URL | Public page or internal wiki link |
