---
name: generate-compliance-report
description: Run a SPEAKMAN.AI compliance workflow and author a Compliance Assessment Report from the agent outputs. Use when the user wants a compliance assessment, gap analysis, or risk report against a regulatory framework (GDPR, PCI-DSS, SOC 2, ISO 27001, HIPAA, NIST CSF, etc.).
---

# generate-compliance-report — SPEAKMAN.AI Compliance Assessment (Claude Desktop / claude.ai)

You are running the SPEAKMAN.AI Compliance Assessment. You will orchestrate a full SPEAKMAN.AI MCP session and author a Compliance Assessment Report from the agent outputs, inside this conversation's execution environment.

Follow every step below exactly. Do not generate the report content yourself — it is built in Step 6 from real agent outputs.

**Prerequisites for this environment:**
- The SPEAKMAN.AI MCP connector must be added under Settings → Connectors. If `start_session` / `get_outputs` / `submit_response` tools are not available, tell the user to add the connector before continuing.
- PDF generation (Step 7) needs Node.js + puppeteer inside this session's sandbox. That is not guaranteed to be present here — if it's missing, the skill still delivers Markdown + HTML, and the user can print the HTML to PDF from their own browser.
- This skill's own folder (the one containing this SKILL.md) already bundles everything it needs — `prompts/`, `scripts/`, `templates/`. There is no separate host install step and no `~/.claude/speakmanai-cc` to resolve; reference bundled files with paths relative to this skill's folder, e.g. `prompts/compliance_agent_prompt.md`.
- This sandbox is ephemeral — every deliverable (the `.md`, `.html`, and `.pdf` if produced) must be surfaced to the user as a downloadable file before you finish, not just left on disk.

---

## Step 0 — Check for Existing Session

Before collecting any input, ask the user:

> "Do you have an existing SPEAKMAN.AI session ID you want to use? If so, paste it and I'll skip straight to generating the report. Otherwise, press Enter and I'll run a new session."

- If a session ID is provided: set `session_id` to that value and **skip to Step 4**.
- If no session ID is provided: continue to Step 1.

---

## Step 1 — Collect Assessment Scope

Ask the user:

> "What system, process, or organisation are you assessing? Describe it in a few sentences — or give me any of the following and I'll extract the context from it:
> - Paste text directly
> - Upload a file (.md, .pdf, .txt, .docx) into this conversation
> - A URL or internal wiki link
> - A connected MCP resource (Google Drive folder, Confluence space, SharePoint library)
> - An existing architecture document or SAD
> - A data flow or system inventory"

Read and parse whatever is provided. Extract:
- Name and purpose of the system or process being assessed
- Data classifications in scope (PII, PHI, PCI, financial, etc.)
- Hosting model (cloud, on-premise, hybrid) and key infrastructure
- User types and access patterns
- Any known existing controls or compliance certifications
- Regulatory context (geography, sector, existing obligations)

Store this as **SCOPE_CONTEXT**.

---

## Step 2 — Identify Regulatory Framework

Ask the user:

> "Which regulatory framework or standard are you assessing against? Common options:
> - GDPR (EU data protection)
> - PIPEDA / Law 25 (Canadian privacy)
> - PCI-DSS (payment card)
> - SOC 2 Type II (trust service criteria)
> - ISO 27001 (information security)
> - HIPAA (US healthcare)
> - NIST CSF (cybersecurity framework)
> - Or describe a custom / internal framework
>
> You can specify more than one.
>
> Do you also have an existing controls inventory (spreadsheet, CSV, text file, or upload)? If so, provide it and I'll use it when building the controls list — or press Enter to derive a baseline from the framework."

Record the selected framework(s) as **FRAMEWORKS**. If a controls inventory is provided, store the file path or reference as **CONTROLS_SOURCE**. **Do not parse it yet** — parsing happens at Step 3b once the live schema is available.

Merge SCOPE_CONTEXT + FRAMEWORKS as **FULL_CONTEXT**.

---

## Step 3 — Run SPEAKMAN.AI Session

### 3a — Start session

Call `start_session`:
- `workflow_id`: `MCP_COMPLIANCE_ASSESSMENT_V1`
- `title`: Short title derived from the system name and framework (max 60 chars, e.g. "Compliance Assessment — PaymentHub / PCI-DSS")
- `description`: Assessment scope and framework from FULL_CONTEXT (max 3000 chars — trim if needed, keep system purpose, data classifications, frameworks, and hosting model)

Poll every 30 seconds until `status = AWAITING_INPUT`.

### 3b — Build and submit controls inventory

When AWAITING_INPUT arrives, the payload contains `input_required.prompt`, `input_required.schema`, and `input_required.context`.

If **CONTROLS_SOURCE** was provided in Step 2, read and parse it now against the live schema.

1. Read the schema from `input_required.schema` — this defines exactly what to build.
2. Display a summary table to the user showing what the schema expects:

| Field | Description |
|---|---|
| control_id | Your internal control reference or framework control ID |
| domain | Control domain (e.g. Access Control, Cryptography, Incident Response) |
| description | What the control does |
| status | Implemented / Partial / Not Implemented / Not Applicable |
| evidence | Brief description of evidence available (or "None") |

3. Build the controls inventory JSON array from FULL_CONTEXT, guided by the schema and `input_required.prompt`. Aim for 20–40 controls covering the full framework scope. If the user has no inventory, derive a baseline set from the framework requirements and mark each as `Not Implemented` pending review.

4. Present a draft table to the user:

| # | Domain | Control | Status | Evidence |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

Say: "Here is the controls inventory I've built — confirm to submit, or describe any changes."

5. On user confirmation, call `submit_response(session_id, <controls JSON array>)`.

Poll every 60 seconds until `status = COMPLETED`. This takes 10–15 minutes.

---

## Step 4 — Download Agent Outputs

Call `get_outputs(session_id)` to get the manifest.

Then call `get_output` for these agents **only** — fetch in parallel where possible:

| Agent ID | Contains |
|---|---|
| `MCP_COMPLIANCE_SCOPE_CLARIFIER_V1` | Confirmed assessment scope, data classifications, system context |
| `MCP_RISK_ANALYST_V1` | Risk scoring by domain, likelihood and impact ratings, residual risk |
| `MCP_COMPLIANCE_OFFICER_V1` | Control-by-control assessment, gap identification, severity ratings |
| `MCP_REMEDIATION_ADVISOR_V1` | Prioritised remediation recommendations, effort and impact estimates |

> **Do NOT download `MCP_COMPLIANCE_REPORT_WRITER_V1`.** The Step 6 prompt replaces it.

Create the working directory in this session's sandbox: `outputs/YYYY-MM-DD_{slug}/raw/` where slug is a lowercase-hyphenated version of the session title and YYYY-MM-DD is today's date.

**Save each agent output using your file-write capability directly** — the `content` field returned by `get_output` is already in context. Write it straight to disk rather than shelling out to write it.

Use the stable filename mapping below (not the raw `agent_id`):

| Agent ID | Save as |
|---|---|
| `MCP_COMPLIANCE_SCOPE_CLARIFIER_V1` | `compliance_scope_clarifier.txt` |
| `MCP_RISK_ANALYST_V1` | `risk_analyst.txt` |
| `MCP_COMPLIANCE_OFFICER_V1` | `compliance_officer.txt` |
| `MCP_REMEDIATION_ADVISOR_V1` | `remediation_advisor.txt` |

---

## Step 5 — Choose Template

Ask the user:

> "Which document template?
> - [default] — SPEAKMAN.AI branded, bundled with this skill
> - [corporate] — your own brand. Upload a logo.png into this conversation and I'll use it for this run
> - Or paste/upload a custom template directory"

Default to this skill's own `templates/default` folder if the user presses Enter.

If the user wants a corporate template for repeat use (not just this run), tell them: since this sandbox doesn't persist, the only way to make a corporate logo stick across future conversations is to add it to `templates/corporate/` in the skill package itself and re-upload the plugin. For a one-off, uploading the logo into the conversation and pointing `--template` at that upload is enough.

Store the resolved template path as **TEMPLATE_DIR**.

---

## Step 6 — Generate Compliance Report

Using the downloaded raw agent outputs saved in `outputs/YYYY-MM-DD_{slug}/raw/`, follow the instructions in this skill's `prompts/compliance_agent_prompt.md` exactly to generate the report.

Key rules for this step:
- Read all 4 agent output files from the raw directory
- Follow the synthesis and template instructions in `compliance_agent_prompt.md`
- **Change Log date**: use today's actual date — do NOT rely on LLM knowledge for this
- Save the completed Markdown to: `outputs/YYYY-MM-DD_{slug}/{slug}.md`

---

## Step 7 — Build HTML and PDF

Run the following commands (this skill's `scripts/` folder, relative to this SKILL.md):

```bash
python3 scripts/preprocess.py outputs/YYYY-MM-DD_{slug}/{slug}.md
python3 scripts/doc_writer.py outputs/YYYY-MM-DD_{slug}/{slug}_clean.md \
  --template {TEMPLATE_DIR} \
  --output outputs/YYYY-MM-DD_{slug}/{slug} \
  --yes
```

`doc_writer.py` tries Node + puppeteer for the PDF step and prints a warning and continues if that's unavailable — it always produces the HTML regardless. **Do not treat a PDF failure as a skill failure.** If PDF generation was skipped, tell the user: "PDF generation isn't available in this session — here's the Markdown and HTML; open the HTML and use your browser's Print → Save as PDF to get a PDF copy."

---

## Step 8 — Deliver and Report

Make sure `{slug}.md`, `{slug}.html`, and `{slug}.pdf` (if produced) are all offered to the user as downloadable files from this conversation — this sandbox does not persist, so anything not downloaded now is lost.

Report:

```
Session ID        : {session_id}
Credits used      : {session_cost}
Framework(s)      : {frameworks}
Overall risk      : {risk_level} — {score}/10
Critical gaps     : {critical_gap_count}
Outputs
  Markdown        : {slug}.md
  HTML            : {slug}.html
  PDF             : {slug}.pdf (or "not generated — see HTML")
```

Then say: "Review `{slug}.pdf` (or `{slug}.html` if no PDF was generated) — this is your draft Compliance Assessment Report, ready for review before submission or remediation planning."
