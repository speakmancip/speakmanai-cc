# speakmanai-cc

Claude Code skills for the [SPEAKMAN.AI](https://speakman.ai) MCP server (cloud) or the [local self-hosted version](https://github.com/speakmancip/speakmanai-local). Each skill orchestrates a full SPEAKMAN.AI session, downloads the agent outputs, and generates a locally-authored deliverable using a configurable document template.

## Available Skills

| Skill | Command | Workflow | Output |
|---|---|---|---|
| Solution Architecture Document | `/generate-sad` | `MCP_SOLUTION_ARCHITECTURE_V1` | SAD — HTML + PDF, ARB-ready |
| Compliance Assessment Report | `/generate-compliance-report` | `MCP_COMPLIANCE_ASSESSMENT_V1` | Risk scores, gap analysis, remediation roadmap |
| Workflow Creator | `/generate-speakmanai-workflow` | `WORKFLOW_CREATOR_V1` | Workflow definition JSON, ready for DB import |

---

## Prerequisites

- [Claude Code](https://claude.ai/claude-code) installed
- SPEAKMAN.AI MCP server configured in your Claude Code settings
- Python 3.9+
- Node.js (for PDF generation — puppeteer is installed automatically by the install script)

---

## Install

Clone this repository, then run the install script from within it.

**Windows:**
```powershell
git clone https://github.com/speakmancip/speakmanai-local.git
cd speakmanai-cc
.\install.ps1
```

**macOS / Linux:**
```bash
git clone https://github.com/speakmancip/speakmanai-local.git
cd speakmanai-cc
chmod +x install.sh && ./install.sh
```

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
