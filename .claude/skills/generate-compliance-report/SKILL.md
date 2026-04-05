---
name: generate-compliance-report
description: Run a SPEAKMAN.AI compliance workflow and generate a Compliance Assessment Report locally
---

# generate-compliance-report — SPEAKMAN.AI Compliance Assessment

You are running the SPEAKMAN.AI Compliance Assessment. You will orchestrate a full SPEAKMAN.AI MCP session and produce a locally-generated Compliance Assessment Report from the agent outputs.

Follow every step below exactly. Do not generate the report content yourself — it is built in Step 6 from real agent outputs.

---

## Before You Begin — Resolve Asset Directory

Determine the absolute path to the SPEAKMAN.AI asset directory by running:

```bash
echo "$HOME/.claude/speakmanai-cc"
```

Store the result as **ASSET_DIR**. Use this variable everywhere `~/.claude/speakmanai-cc` appears below — never use `~` in file read operations, as it does not expand outside of a shell context.

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
> - A file path (.md, .pdf, .txt, .docx)
> - A directory to scan for relevant documents
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
> Do you also have an existing controls inventory (spreadsheet, CSV, text file, or path)? If so, provide it and I'll use it when building the controls list — or press Enter to derive a baseline from the framework."

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

> **Do NOT download `MCP_COMPLIANCE_REPORT_WRITER_V1`.** The local prompt replaces it.

Create the output directory: `outputs/YYYY-MM-DD_{slug}/raw/` where slug is a lowercase-hyphenated version of the session title and YYYY-MM-DD is today's date.

**Save each agent output using the `Write` tool directly** — the `content` field returned by `get_output` is already in context. Do not use bash scripts or Python to write files; the `Write` tool handles large content natively and is reliable across all platforms.

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
> - [default] — SPEAKMAN.AI branded
> - [corporate] — your own brand (add logo.png to ~/.claude/speakmanai-cc/templates/corporate/)
> - Or paste a path to a custom template directory"

Default to `{ASSET_DIR}/templates/default` if the user presses Enter.

Store the resolved template path as **TEMPLATE_DIR**.

---

## Step 6 — Generate Local Compliance Report

Using the downloaded raw agent outputs saved in `outputs/YYYY-MM-DD_{slug}/raw/`, follow the instructions in `{ASSET_DIR}/prompts/compliance_agent_prompt.md` exactly to generate the report.

Key rules for this step:
- Read all 4 agent output files from the raw directory
- Follow the synthesis and template instructions in `compliance_agent_prompt.md`
- **Change Log date**: use today's actual date — do NOT rely on LLM knowledge for this
- Save the completed Markdown to: `outputs/YYYY-MM-DD_{slug}/{slug}.md`

---

## Step 7 — Build HTML and PDF

Run the following commands:

```bash
python3 {ASSET_DIR}/scripts/preprocess.py outputs/YYYY-MM-DD_{slug}/{slug}.md
python3 {ASSET_DIR}/scripts/doc_writer.py outputs/YYYY-MM-DD_{slug}/{slug}_clean.md \
  --template {TEMPLATE_DIR} \
  --output {absolute_path_to_output_dir}/{slug} \
  --yes
```

> **Note:** Always use the **absolute path** for `--output`. Obtain it by running `pwd` in the project directory and appending the output subdirectory (e.g. `/home/user/myproject/outputs/2026-04-04_my-project/my-project`). A relative path causes `doc_writer.py` to double the directory prefix and fail with a `FileNotFoundError`.

---

## Step 8 — Report

Report the following to the user:

```
Session ID        : {session_id}
Credits used      : {session_cost}
Framework(s)      : {frameworks}
Overall risk      : {risk_level} — {score}/10
Critical gaps     : {critical_gap_count}
Outputs
  Markdown        : outputs/{slug}/{slug}.md
  HTML            : outputs/{slug}/{slug}.html
  PDF             : outputs/{slug}/{slug}.pdf
```

Then say: "Review `{slug}.pdf` — this is your draft Compliance Assessment Report, ready for review before submission or remediation planning."
