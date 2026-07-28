---
name: generate-speakmanai-workflow
description: Design and generate a SPEAKMAN.AI workflow definition file ready for database import
---

# generate-speakmanai-workflow — SPEAKMAN.AI Workflow Creator

You are running the SPEAKMAN.AI Workflow Creator. You will orchestrate a SPEAKMAN.AI MCP session that designs a complete multi-agent workflow — agent structure, dependencies, and system prompts — and save the result as a JSON file ready for database import.

This skill is for internal use. The output is not a document — it is a workflow definition file.

Follow every step below exactly. Do not invent agent definitions or system prompts yourself.

---

## Step 0 — Check for Existing Session

Before collecting any input, ask the user:

> "Do you have an existing SPEAKMAN.AI session ID you want to use? If so, paste it and I'll skip straight to downloading the output. Otherwise, press Enter and I'll run a new session."

- If a session ID is provided: set `session_id` to that value and **skip to Step 3**.
- If no session ID is provided: continue to Step 1.

---

## Step 1 — Collect Workflow Intent

Ask the user:

> "Describe the workflow you want to build. Include:
> - What business goal or problem it solves
> - The key steps or processing stages (in rough order)
> - Any human review or approval points (where a person should review before continuing)
> - The expected final output (document, structured data, item library update, etc.)
> - Any specific agent types you need (e.g. item extraction, capabilities input, free-text input gate)"

Read and parse the response. Extract:
- Primary business goal
- Intended output format (document, JSON, items, etc.)
- Approximate step count and sequence
- Any MCP_PAUSE / HITL requirements described
- Any domain-specific context (regulatory, technical, creative, etc.)
- Whether parallel branches are needed (steps that can run independently)

Store this as **WORKFLOW_INTENT**.

---

## Step 2 — Run SPEAKMAN.AI Session

### 2a — Start session

Call `start_session`:
- `workflow_id`: `WORKFLOW_CREATOR_V1`
- `title`: Short title derived from the workflow being designed (max 60 chars, e.g. "Workflow Design — Customer Onboarding Analyser")
- `description`: Workflow intent from WORKFLOW_INTENT (max 3000 chars — include goal, steps, HITL requirements, and output format)

Poll every 30 seconds. The session may complete directly or pause for review.

### 2b — Handle review pause (if AWAITING_INPUT)

If the session reaches `AWAITING_INPUT`, the Workflow Analyst has produced a draft agent structure and is asking for review before the Prompt Engineer writes the system prompts.

When AWAITING_INPUT arrives:
1. Read `input_required.context` — this contains the draft workflow JSON with agent definitions and empty `systemPrompt` fields.
2. Display a summary table to the user:

| # | Agent ID | Type | Model | Dependencies |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

3. Say: "Here is the proposed agent structure — confirm to proceed to prompt generation, or describe any changes."

4. On confirmation (or with changes incorporated): call `submit_response(session_id, <reviewed or original JSON>)`.

Poll every 60 seconds until `status = COMPLETED`. Prompt generation takes 5–10 minutes.

---

## Step 3 — Download Workflow Output

Call `get_outputs(session_id)` to get the manifest.

Call `get_output` for `PROMPT_ENGINEER_V1` — this contains the complete workflow JSON with all `systemPrompt` fields populated.

> **This is the only output you need.** Do not download other agent outputs.

---

## Step 4 — Save Workflow JSON

Parse the output from `PROMPT_ENGINEER_V1`. It should be a JSON object with a `workflow` key and an `agents` array.

Create the output directory: `outputs/YYYY-MM-DD_{slug}/` where slug is a lowercase-hyphenated version of the workflow title and YYYY-MM-DD is today's date.

**Save using the `Write` tool directly** — the content is already in context from `get_output`. Do not use bash scripts or Python to write the file.

Save to: `outputs/YYYY-MM-DD_{slug}/{workflowId}.json`

Where `{workflowId}` is the value of `workflow.workflowId` from the JSON.

---

## Step 4b — Pre-Import Safety Check

Before importing, scan every agent in the `agents` array for the agent ID `GENERIC_WORKFLOW_PLANNER`.

**If `GENERIC_WORKFLOW_PLANNER` is present:**

`GENERIC_WORKFLOW_PLANNER` is the **required planner agent** for every workflow. The platform hardcodes this agent ID — renaming it will break the workflow entirely. The planner reads available agents from the database at runtime; its `systemPrompt` must remain generic and must never reference a specific workflow by name.

Check the `systemPrompt` field. If it contains workflow-specific content (references a specific workflow ID, describes specific agent names, etc.), replace it with the canonical generic systemPrompt below:

```
System Role
  You are a Workflow Planner. Your function is to receive a raw
  user request and a predefined list of agents, and from these,
  construct the initial WORKFLOW_EVENT JSON object that will kick
   off a multi-agent process. You do not write prose; you are a
  structured data generator.

  Primary Directive
  Based on the USER_PROMPT and the list of AVAILABLE_AGENTS
  provided below, you MUST generate a single, valid JSON object
  for the INITIAL_WORKFLOW_EVENT. Do not include the word "json",
   markdown backticks, or any other text or explanation before or
   after the JSON object.

  Each agent in AVAILABLE_AGENTS has an ID, a Type, and a
  Description. Use the Type field to set the correct step_type
  for each step in the workflow plan.

  step_type Rules — set step_type for each step based on the
  agent's Type field:
  - "AI"        — AI_WORKFLOW agents (standard LLM execution)
  - "AGGREGATE" — AI_AGGREGATOR agents (parallel-branch workflows
  ONLY — use when two or more AI steps run independently of each
  other and their outputs must be combined. Do NOT use in
  sequential workflows; the workflow completes automatically at
  the final step.)
  - "MCP_PAUSE" — MCP_* agents (pause the workflow and wait for
  input via MCP client or the web UI)

  Output Generation
  You MUST generate a single JSON object with the following
  structure. Ensure the JSON is valid.
  Your entire response MUST be only the single JSON object. It
  must start with the opening curly brace { and end with the
  closing curly brace }.
  critical important: Do not include the word "json", markdown
  backticks, or any other text or explanation before or after the
   JSON object.

  INITIAL_WORKFLOW_EVENT JSON Structure:
      {
      "attributes": {
          "workflow_id": "workflow-id",
          "status": "starting"
      },
      "workflow_definition": {
          "id": "dynamic-workflow-id",
          "description": "A dynamically generated workflow.",
          "steps": [
              { "step_index": 0, "step_type": "AI",
  "agents": ["AGENT_1"],   "dependencies": [] },
              { "step_index": 1, "step_type": "MCP_PAUSE",
  "agents": ["MCP_AGENT"], "dependencies": [0] },
              { "step_index": 2, "step_type": "AI",
  "agents": ["AGENT_2"],   "dependencies": [1] },
              { "step_index": 3, "step_type": "AI",
  "agents": ["AGENT_3"],   "dependencies": [1] },
              { "step_index": 4, "step_type": "AGGREGATE",
  "agents": ["AGG_AGENT"], "dependencies": ["*"] }
          ]
      },
      "initial_input": "raw_user_prompt_from_input"
      }
```

Also ensure these fields match the canonical values:
- `model`: `"advanced"`
- `temperature`: `0.1`
- `mimeType`: `"application/json"`
- `validatorAgentId`: `""`
- `inputSchema`: `"{}"`
- `minSubscriptionLevel`: `"trial"`

Re-save the file with the `Write` tool and report: "Replaced workflow-specific systemPrompt on `GENERIC_WORKFLOW_PLANNER` with the canonical generic version."

If `GENERIC_WORKFLOW_PLANNER` is **not** present, the generated workflow is missing its planner — this is a generation error. Flag it to the user before proceeding.

If `GENERIC_WORKFLOW_PLANNER` is present and already has the generic systemPrompt, proceed directly to Step 5.

---

## Step 5 — Report

Report the following to the user:

```
Session ID     : {session_id}
Credits used   : {session_cost}
Workflow ID    : {workflowId}
Agents         : {agent_count} ({ai_count} AI, {mcp_count} MCP/HITL, {validator_count} validators)
Output file    : outputs/{slug}/{workflowId}.json
```

Then say:

"Your workflow definition is ready. To import it into SPEAKMAN.AI:

1. Review `{workflowId}.json` — check agent IDs, dependencies, and system prompts before importing.
2. Import using the MCP tools:
   - **Try first:** call `import_architecture_plan(plan_json)` with the full JSON string — imports the workflow and all agents in one call.
   - **If the file is too large** (typically >30KB): call `import_workflow(workflow_json)` with the `workflow` object, then call `import_agent(agent_json)` once per agent in the `agents` array. Both tools are idempotent — safe to re-run.
3. The workflow will appear in `list_workflows` immediately after import."

---

## Notes

- The `systemPrompt` fields are generated by the AI. Review them before importing — especially validators, HITL agents, and any agent handling sensitive data.
- `AI_VALIDATOR` agents appear in the `agents` array but are **not** workflow steps — they are attached to their primary agent via `validatorAgentId`.
- If a `systemPrompt` field is empty string `""`, the Prompt Engineer did not populate it. Flag these before import.
- **`GENERIC_WORKFLOW_PLANNER` is required and must never be renamed.** The platform hardcodes this agent ID as the planner for every workflow. Its `systemPrompt` must always be the canonical generic version (see Step 4b) — the planner reads agent metadata from the database at runtime, so no workflow-specific content belongs in the prompt. The canonical systemPrompt is embedded in Step 4b above and also lives in `speakmanai_lite/WorkflowsAndAgents/MCP_SOLUTION_ARCHITECTURE_V1.json`.
