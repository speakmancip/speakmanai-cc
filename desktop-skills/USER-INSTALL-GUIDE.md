# Installing the SPEAKMAN.AI Assistant in Claude Desktop

A one-time, five-minute setup. After this, you just chat — no commands, no code.

## What you need first

1. **Claude Desktop** installed and signed in with a paid plan (Pro, Max, or Team). [Download Claude Desktop](https://claude.ai/download) if you don't have it.
2. The **`speakmanai-sdlc.zip`** file — get this from whoever sent you this guide.
3. The **SPEAKMAN.AI connector details** (a URL) — also from whoever sent you this guide.

## Step 1 — Connect SPEAKMAN.AI

1. Open Claude Desktop.
2. Click **Settings → Connectors**.
3. Click **Add connector** and paste in the SPEAKMAN.AI URL you were given.
4. Save.

## Step 2 — Install the assistant

1. Still in Claude Desktop, switch to the **Cowork** tab (this is Claude's workspace mode — separate from regular chat).
2. Click **Settings → Plugins → Upload**.
3. Select the `speakmanai-sdlc.zip` file.
4. That's it — installed.

## Step 3 — Just ask for what you need

No slash commands, no special syntax. Start a conversation in Cowork and describe what you want in plain English, for example:

- *"Generate a Solution Architecture Document for a new customer portal."*
- *"Write UAT test cases for the login and checkout flows."*
- *"Run a compliance assessment against GDPR for our booking system."*
- *"Check if this codebase is ready to promote from DEV to STG."*

Claude will ask you follow-up questions as it goes — describe your project, upload any documents you have, and confirm the details it shows you along the way.

## What you can ask it to do

| Ask for... | And you'll get... |
|---|---|
| A Solution Architecture Document (SAD) | A branded architecture document, ready for review |
| Requirements | A domain model, use cases, and API/database design |
| A working codebase | Generated code for your project, milestone by milestone |
| Infrastructure | Terraform + security hardening for GCP/AWS/Azure |
| UAT test cases | Human-executable test scripts your QA team can run |
| A compliance report | A gap analysis against GDPR, PCI-DSS, SOC 2, HIPAA, and others |
| An environment promotion check | A pass/block report before moving code between environments |
| A pentest | A coordinated penetration test through the pentest platform |

## If something doesn't work

- **No "Cowork" tab?** Your Claude Desktop version may not have it yet, or your plan doesn't include it — check with whoever set this up for you.
- **No PDF at the end of a document?** That's expected sometimes — you'll still get the document as a webpage (HTML) you can open and print to PDF yourself.
- **Anything else** — reach out to whoever sent you this guide.
