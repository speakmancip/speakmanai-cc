---
name: generate-sad
description: Run a SPEAKMAN.AI architecture workflow and generate a Solution Architecture Document locally
---

# generate-sad — SPEAKMAN.AI Local SAD Generator

You are running the SPEAKMAN.AI SAD Generator. You will orchestrate a full SPEAKMAN.AI MCP session and produce a locally-generated Solution Architecture Document (SAD) from the agent outputs.

Follow every step below exactly. Do not generate the SAD content yourself — it is built in Step 6 from real agent outputs.

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

> "Do you have an existing SPEAKMAN.AI session ID you want to use? If so, paste it and I'll skip straight to generating the document. Otherwise, press Enter and I'll run a new session."

- If a session ID is provided: set `session_id` to that value and **skip to Step 4**.
- If no session ID is provided: continue to Step 1.

---

## Step 1 — Collect Business Input

Ask the user:

> "What do you want to build? Describe it in a few sentences — or give me any of the following and I'll extract the description from it:
> - Paste text directly
> - A file path (.md, .pdf, .txt, .docx)
> - A directory to scan for relevant documents
> - A URL or internal wiki link
> - A connected MCP resource (Google Drive folder, Confluence space, SharePoint library)
> - RAG search results or document links
> - Terraform files (.tf or terraform.tfstate) — I'll extract your tech stack from these"

Read and parse whatever is provided. Extract:
- Business goal and problem being solved
- Target scale and success metrics (look for numbers — transactions/month, users, uptime targets)
- Key user types or stakeholders mentioned
- Regulatory or compliance requirements (PCI-DSS, GDPR, HIPAA, ISO 27001, etc.)
- Preferred or existing technology stack

Store this as **BUSINESS_CONTEXT**.

---

## Step 2 — Collect Capabilities Source (Reference Only)

Ask the user:

> "Do you have any additional context for your current or planned technology capabilities? This helps build a richer architecture. You can provide:
> - An existing systems inventory (any format)
> - Terraform files (.tf / terraform.tfstate) — I'll map resources to capabilities
> - Architecture documents, RFPs, or technical briefs
> - A connected doc store, Google Drive folder, or RAG search
> - Or press Enter to use the business description only"

**Store the file path, text, or reference as `CAPABILITIES_SOURCE`. Do not parse it yet.**

Parsing happens at Step 3b, once the live schema arrives from the workflow. Loading and interpreting capabilities before the schema is available wastes context and may not match what the workflow expects.

---

## Step 3 — Run SPEAKMAN.AI Session

### 3a — Start session

Call `start_session`:
- `workflow_id`: `MCP_SOLUTION_ARCHITECTURE_V1`
- `title`: Short title derived from the business description (max 60 chars)
- `description`: Business description from **BUSINESS_CONTEXT only** (max 3000 chars — trim if needed, keep goal, scale, compliance). Do NOT include technology stack or capabilities detail — that belongs only in Step 3b.

Poll every 30 seconds until `status = AWAITING_INPUT`.

### 3b — Build and submit capabilities

When AWAITING_INPUT arrives, the payload contains `input_required.prompt`, `input_required.schema`, and `input_required.context`.

Now read and parse `CAPABILITIES_SOURCE` (from Step 2). Extract:
- Current/existing technology systems and their deployment states (Current)
- Planned or proposed tools (Proposed)
- Legacy systems being replaced (Legacy)
- Any migration strategies mentioned

If Terraform files are provided:
- Parse `resource` blocks to identify AWS/Azure/GCP services → map to technology capability names
- Use `terraform.tfstate` as ground truth for Current state; `.tf` files for Proposed
- Infer migration_strategy from context (rename, replace, lift-and-shift)

1. Read the schema from `input_required.schema` — this defines exactly what to build.
2. Display a summary table to the user showing what the schema expects:

| Field | Description |
|---|---|
| name | Capability name |
| type | Business or Technology |
| deployments[].tool_name | Tool or platform name |
| deployments[].state | Current / Proposed / Legacy |
| deployments[].migration_strategy | N/A, Replace, Replatform, etc. |

3. Build the capabilities JSON array from FULL_CONTEXT, guided by the schema and `input_required.prompt`. Aim for 15–25 capabilities covering the full scope. Include both Business capabilities (functions, processes) and Technology capabilities (tools, platforms, APIs, infrastructure).

4. Present a draft table to the user:

| # | Name | Type | Tool | State |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

Say: "Here are the capabilities I've extracted — confirm to submit, or describe any changes."

5. On user confirmation, call `submit_response(session_id, <capabilities JSON array>)`.

Poll every 60 seconds until `status = COMPLETED`. This takes 10–15 minutes.

---

## Step 4 — Download Supporting Agent Outputs

Call `get_outputs(session_id)` to get the manifest.

Then call `get_output` for these agents **only** — fetch in parallel where possible:

| Agent ID | Contains |
|---|---|
| `MCP_BUSINESS_CONTEXT_CLARIFIER_V1` | Project brief, business context |
| `MCP_BUSINESS_ANALYST_V1` | Requirements, personas, process flows, data entities |
| `MCP_BUSINESS_APPLICATION_ARCHITECT_V1` | Component catalog, data flows, ADRs |
| `MCP_TECHNICAL_SOLUTION_ARCHITECT_V1` | Infrastructure decisions, deployment strategy, ADRs |
| `MCP_COMPLIANCE_OFFICER_V2` | Traceability matrix, violations, compliance score |
| `MCP_TECHNICAL_VISUALIZATION_SPECIALIST_V1` | Raw Mermaid diagrams |

> **Do NOT download `MCP_TECHNICAL_WRITER_V2`.** The local prompt replaces it.

Create the output directory: `outputs/YYYY-MM-DD_{slug}/raw/` where slug is a lowercase-hyphenated version of the session title and YYYY-MM-DD is today's date.

**Save each agent output using the `Write` tool directly** — the `content` field returned by `get_output` is already in context. Do not use bash scripts or Python to write files; the `Write` tool handles large content natively and is reliable across all platforms.

Use the stable filename mapping below (not the raw `agent_id`):

| Agent ID | Save as |
|---|---|
| `MCP_BUSINESS_CONTEXT_CLARIFIER_V1` | `business_context_clarifier.txt` |
| `MCP_BUSINESS_ANALYST_V1` | `business_analyst.txt` |
| `MCP_BUSINESS_APPLICATION_ARCHITECT_V1` | `business_application_architect.txt` |
| `MCP_TECHNICAL_SOLUTION_ARCHITECT_V1` | `technical_solution_architect.txt` |
| `MCP_COMPLIANCE_OFFICER_V2` | `compliance_officer.txt` |
| `MCP_TECHNICAL_VISUALIZATION_SPECIALIST_V1` | `visualization_specialist.txt` |

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

## Step 6 — Generate Local SAD

Using the downloaded raw agent outputs saved in `outputs/YYYY-MM-DD_{slug}/raw/`, follow the instructions in `{ASSET_DIR}/prompts/sad_agent_prompt.md` exactly to generate the SAD.

Key rules for this step:
- Read all 6 agent output files from the raw directory
- Follow the synthesis and template instructions in `sad_agent_prompt.md`
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
Session ID   : {session_id}
Credits used : {session_cost}
Compliance   : {score}/10 — {status}
Outputs
  Markdown   : outputs/{slug}/{slug}.md
  HTML       : outputs/{slug}/{slug}.html
  PDF        : outputs/{slug}/{slug}.pdf
```

Then say: "Review `{slug}.pdf` — this is your draft SAD, ready for architect review before ARB submission."
