# The SPEAKMAN.AI SDLC Pipeline

This document is the end-to-end roadmap: what phase produces what, which skill runs it, and
what order to run them in to take a project from a business description to a
pentested, production-promotable codebase.

If you want a guided run instead of reading this and driving each skill yourself, use
`/sdlc-pipeline` — it shepherds you through every phase below in order, carrying each
phase's output path into the next phase automatically. This document is the reference for
what that skill is doing under the hood, and for running any phase manually or out of order.

---

## Flow

```
/generate-sad                    Phase 1 — Solution Architecture Document
        │
        ▼
/generate-requirements           Phase 2 — Requirements & domain modeling (coding contracts)
        │
        ▼
/generate-speakmanai-code         Phase 3 — Working, milestone-gated, committed codebase
   (router → -js / -go / -python variant)
        │
        ▼
/generate-infrastructure          Phase 4 — Terraform + pre-pentest hardening
        │
        ▼
/promote-environment 1             Gate — local → DEV (code quality)
        │  (deploy to DEV — manual)
        ▼
/promote-environment 2             Gate — DEV → STG (security + reliability)
        │  (deploy to STG — manual)
        ▼
/pentest  (+ /pentest-execute)  ┐   Gate — penetration test against the live STG environment
                                 │
/generate-uat-tests             ┘   Produces uat_test_cases.md — human executes against STG
        │
        │  finding requires a code fix?
        │  ── yes → fix locally, then restart from /promote-environment 1 —
        │           the gates you already passed no longer describe the current code
        │  ── no  → continue
        ▼
/promote-environment 3             Gate — STG → PROD (hardening + UAT functionality score)
```

Pentest and UAT run against **STG, not DEV** — STG is the more stable, closer-to-production
target, and both gates should be exercising the same environment shape PROD will use.

**Any code change made after a promotion gate has passed invalidates that gate.** A pentest
or UAT finding fixed locally means the code that Level 1 and Level 2 approved no longer
exists — re-run `/promote-environment` from Level 1, redeploy through DEV and STG again, and
re-run pentest/UAT against the fresh STG deployment before attempting Level 3. Do not treat
Level 3 as re-runnable in isolation after a fix elsewhere in the chain.

`/generate-compliance-report` and `/generate-speakmanai-workflow` sit outside this chain —
see [Adjacent tools](#adjacent-tools-not-part-of-the-sequential-chain) below.

---

## Phase 1 — Architecture

| | |
|---|---|
| Skill | `generate-sad` |
| Workflow | `MCP_SOLUTION_ARCHITECTURE_V1` |
| Consumes | A business description (text, file, URL, MCP resource) + optional capabilities context (existing systems inventory, Terraform files) |
| Produces | `outputs/YYYY-MM-DD_{slug}/raw/` — `business_context_clarifier.txt`, `business_analyst.txt`, `business_application_architect.txt`, `technical_solution_architect.txt`, `compliance_officer.txt`, `visualization_specialist.txt` — plus a local SAD (Markdown/HTML/PDF) |
| Feeds | Phase 2 (business + tech context), Phase 4 (`technical_solution_architect.txt`, `compliance_officer.txt`), `generate-uat-tests` (`business_context_clarifier.txt`, `business_analyst.txt` for traceability) |

---

## Phase 2 — Requirements Engineering

| | |
|---|---|
| Skill | `generate-requirements` |
| Workflow | `MCP_REQUIREMENTS_ENGINEERING_V1` |
| Consumes | Phase 1 output directory (or a Phase 1 session ID, or raw business text if no Phase 1 was run) |
| Produces | `outputs/YYYY-MM-DD_{slug}/raw/` — `domain_model.txt`, `naming_dictionary.txt`, `use_case_catalog.txt`, `api_schema.txt`, `database_schema.txt`, `test_strategy.txt`, and optionally `field_definitions.txt` — the "coding contracts" |
| Feeds | Phase 3 (all six contracts, read directly — no credits), Phase 4 (`api_schema.txt`, `database_schema.txt`, `test_strategy.txt`), `generate-uat-tests` (`use_case_catalog.txt`, `api_schema.txt`, `field_definitions.txt`) |

Human-in-the-loop gates inside this workflow (`RE_TECH_STACK_PROVIDER_V1`, `RE_FIELD_DEFINITIONS_REVIEW_V1`, `RE_NAMING_REVIEW_V1`) are driven by the skill — you review and approve inline during the ~10–15 minute session.

---

## Phase 3 — Code Generation

| | |
|---|---|
| Skill | `generate-speakmanai-code` (router) → `generate-speakmanai-code-{js,go,python}` (variant) |
| Consumes | Phase 2 output directory + TECH_STACK description (used to pick the variant) + optional style guide for Milestone 5 |
| Produces | A working, git-committed codebase at `{PROJECT_ROOT}/{REPO_NAME}` — one commit per milestone gate (domain → application → infrastructure → interface → UI styling → E2E) |
| Feeds | Phase 4 (the codebase itself), `promote-environment` (the codebase), `generate-uat-tests` (the running application) |

Adding a new language: see `CONTRIBUTING.md` in the `generate-speakmanai-code` skill directory. The router never changes — only a new variant file is added and registered.

---

## Phase 4 — Infrastructure & Pre-Pentest Hardening

| | |
|---|---|
| Skill | `generate-infrastructure` |
| Consumes | Phase 3 codebase (required) + Phase 1 SAD dir (optional — infers architecture from code if absent) + Phase 2 requirements dir (optional) + target cloud (GCP/AWS/Azure) |
| Produces | `{PROJECT_ROOT}/infra/terraform/` (providers, backend, variables, modules for networking/compute/database/storage/secrets/iam, three environment tfvars) + `{PROJECT_ROOT}/infra/scripts/` (build.sh, deploy.sh) + in-place security hardening fixes applied directly to the Phase 3 codebase (security headers, CORS, rate limiting, error sanitization) |
| Feeds | Terraform apply is manual (human reviews plan before apply) — this skill produces files, never deploys |

Three sequential internal gates: reconcile SAD architecture against the target cloud → harden application code → generate Terraform. Ends by telling you to run `/promote-environment` through DEV then STG, then `/pentest` and `/generate-uat-tests` once STG is live.

---

## Gate — Environment Promotion

| | |
|---|---|
| Skill | `promote-environment` |
| Consumes | Project root + promotion level (1: local→DEV, 2: DEV→STG, 3: STG→PROD) + at level 3, the completed `uat_test_cases.md` |
| Produces | A pass/block report — FAILURES / WARNINGS / PASSED / N/A per checklist item. Never fixes anything itself. |

Levels are cumulative — level 3 re-runs every level 1 and 2 check plus its own. Level 3 additionally computes a **functionality score** from the UAT results file (`generate-uat-tests` output): any not-run or failing UC blocks PROD promotion.

Run level 1 right after Phase 3/4 (before deploying to DEV), level 2 before deploying to STG,
level 3 after pentest is clean and UAT is fully executed against STG. **A code fix made in
response to a pentest or UAT finding means levels 1 and 2 must be re-run** — they validated a
version of the code that no longer exists once the fix lands.

---

## Gate — Penetration Test

| | |
|---|---|
| Skills | `pentest` (orchestrator) + `pentest-execute` (worker, dispatched per task — never invoke directly) |
| Consumes | An **approved engagement** in the separate [pentest-platform-companion](https://github.com/speakmancip/pentest-platform-companion) app (scope must already be `GATE_1_APPROVED` there) |
| Produces | Structured findings + a full report, uploaded to the companion app; gate approvals (2, 3, 4) happen only in that app's UI, never via this skill |

This gate has a hard external dependency the others don't: a running instance of
[pentest-platform-companion](https://github.com/speakmancip/pentest-platform-companion) that
owns scope approval, findings review, and report sign-off. It targets a **live STG
environment** — more stable and closer to production than DEV — so run it after DEV *and*
STG promotion, once STG is deployed. Any finding that requires a code fix means Level 1 and
Level 2 promotion must be re-run before re-testing.

---

## Gate — UAT (Human Acceptance Testing)

| | |
|---|---|
| Skill | `generate-uat-tests` |
| Consumes | Phase 2 output dir (required — `use_case_catalog.txt`, `api_schema.txt`) + Phase 1 output dir (optional, adds business-outcome traceability) + Phase 3 codebase (optional, enables scope-delta / gap detection) + the running application's base URL — point this at **STG**, not DEV |
| Produces | `uat_test_cases.md` — one or more human-executable test cases per UC-ID, with blank Actual Result / Status / Tester / Date fields for a QA tester to fill in by hand in a browser |
| Feeds | `promote-environment` level 3 reads this file directly to compute the functionality score |

Traceability chain this closes: **Business outcome → Requirement → Use Case → UAT test → Pass/Fail → Functionality Score.** Run this against STG, same as pentest — a fix triggered by a FAIL means Level 1 and Level 2 promotion must be re-run before re-executing the affected test cases.

---

## Adjacent tools (not part of the sequential chain)

| Skill | Role |
|---|---|
| `generate-compliance-report` | Runs `MCP_COMPLIANCE_ASSESSMENT_V1` independently against any system/process description — risk scores, gap analysis, remediation roadmap. Useful before Phase 1 (scoping compliance constraints) or standalone against an existing system; not gated on any other phase. |
| `generate-speakmanai-workflow` | Meta-tool for defining a *new* SPEAKMAN.AI workflow (ready for DB import). This is platform tooling for extending SPEAKMAN.AI itself — it does not build or ship an end-user project. |

---

## Minimum viable run

The shortest path from nothing to a promotable, pentested project:

```
/generate-sad
/generate-requirements
/generate-speakmanai-code
/generate-infrastructure
/promote-environment          (level 1: local → DEV) → deploy to DEV
/promote-environment          (level 2: DEV → STG)   → deploy to STG
/pentest                      (against STG — requires companion app + approved engagement)
/generate-uat-tests           (against STG — then a human executes every test case in a browser)
  ── any fix required by a pentest or UAT finding → back to /promote-environment level 1
/promote-environment          (level 3: STG → PROD)
```

Every skill can also be run standalone against an existing codebase or existing Phase
outputs — none of them require starting from Phase 1. Each skill's own Step 0 explains what
it accepts when a prior phase's output isn't available.
