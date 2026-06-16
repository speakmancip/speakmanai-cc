---
name: generate-speakmanai-code
description: Phase 3 of the SPEAKMAN.AI pipeline — implement a working, locally-runnable codebase from Phase 2 coding contracts
---

# generate-speakmanai-code — SPEAKMAN.AI Phase 3 Code Generator

You are executing Phase 3 of the SPEAKMAN.AI delivery pipeline. Your job is to implement a complete, working, locally-runnable codebase from the Phase 2 coding contracts. You write, install, test, and commit — you do not stop at generating files.

Every milestone has a gate: write code → install dependencies → run the validation command → commit on pass, stop on failure. Do not advance past a failed gate.

---

## Step 0 — Collect Inputs

Ask the user:

> "Do you have Phase 2 output files already on disk?
>  - **Yes** → provide the path to the directory that contains a `raw/` folder (e.g. `D:\git\tutorial\outputs\2026-06-15_my-project`)
>  - **No** → provide your Phase 2 SPEAKMAN.AI session ID and I'll fetch the contracts and save them locally for future runs"

> "Where should the new project be created? Provide the parent directory path (e.g. `D:\git` or `/home/user/projects`)."

> "What is the project/repo name? This becomes the directory name (e.g. `todo-list-app`)."

Store:
- **PHASE2_SOURCE**: either a local directory path OR a session ID (determine from user answer)
- **PROJECT_ROOT**: parent directory where the repo will be created
- **REPO_NAME**: directory name for the new repo
- **REPO_PATH**: `{PROJECT_ROOT}/{REPO_NAME}`

---

## Step 1 — Load Phase 2 Contracts

Choose the branch below based on PHASE2_SOURCE.

### Branch A — Local files on disk

If PHASE2_SOURCE is a directory path, set **PHASE2_DIR** = that path and read these files directly:

| File | Variable | Contains |
|---|---|---|
| `{PHASE2_DIR}/raw/coding_brief.txt` | CODING_BRIEF | DDD layer map, directory skeleton, dependency list, coding standards, commit plan, validation gate |
| `{PHASE2_DIR}/raw/domain_model.txt` | DOMAIN_MODEL | Aggregates, value objects, invariants, repository interfaces |
| `{PHASE2_DIR}/raw/naming_dictionary.txt` | NAMING_DICT | Canonical names, banned synonyms, SQL/JSON/UI forms |
| `{PHASE2_DIR}/raw/use_case_catalog.txt` | USE_CASES | UC-XX IDs, Gherkin scenarios, actors, req_refs |
| `{PHASE2_DIR}/raw/api_schema.txt` | API_SCHEMA | OpenAPI 3.0 — all endpoints, request/response schemas, field constraints |
| `{PHASE2_DIR}/raw/database_schema.txt` | DB_SCHEMA | Idempotent SQL DDL — all tables, columns, constraints |
| `{PHASE2_DIR}/raw/test_strategy.txt` | TEST_STRATEGY | Per-layer test type, tooling, mock boundaries, T-xxx IDs |

If `{PHASE2_DIR}/raw/field_definitions.txt` exists, read it as FIELD_DEFS. If it is absent, warn the user and continue without it.

### Branch B — Fetch from SPEAKMAN.AI (uses credits)

If PHASE2_SOURCE is a session ID:

1. Call `get_outputs(PHASE2_SOURCE)` to retrieve the output manifest.

2. Call `get_output(PHASE2_SOURCE, agent_id)` in parallel for each contract:

| Agent ID | Variable | Local filename |
|---|---|---|
| `RE_CODING_BRIEF_WRITER_V1` | CODING_BRIEF | `coding_brief.txt` |
| `RE_DOMAIN_MODELER_V1` | DOMAIN_MODEL | `domain_model.txt` |
| `RE_NAMING_CONVENTION_ARCHITECT_V1` | NAMING_DICT | `naming_dictionary.txt` |
| `RE_USE_CASE_ANALYST_V1` | USE_CASES | `use_case_catalog.txt` |
| `RE_API_SCHEMA_DESIGNER_V1` | API_SCHEMA | `api_schema.txt` |
| `RE_DATABASE_SCHEMA_DESIGNER_V1` | DB_SCHEMA | `database_schema.txt` |
| `RE_TEST_STRATEGIST_V1` | TEST_STRATEGY | `test_strategy.txt` |
| `RE_FIELD_DEFINITIONS_CATALOG_V1` | FIELD_DEFS | `field_definitions.txt` (optional) |

   If an agent ID is absent from `available_outputs`, check for a human-reviewed version with the same prefix (e.g. `RE_FIELD_DEFINITIONS_REVIEW_V1`). FIELD_DEFS is optional — warn and continue if absent. If any of the other 7 are missing, stop and report which are absent.

3. **Save every fetched output to disk** so future runs use Branch A and incur no further credit cost. Derive the directory from the session title:
   - `PHASE2_DIR` = `{PROJECT_ROOT}/outputs/YYYY-MM-DD_{session-title-slug}/`
   - Save each file to `{PHASE2_DIR}/raw/{local_filename}` using the Write tool.
   - Tell the user: "Contracts saved to `{PHASE2_DIR}/raw/` — future runs can use Branch A with this directory."

---

Extract from CODING_BRIEF and store:
- **TECH_STACK**: language, runtime, framework, database, testing tools
- **DIR_SKELETON**: directory structure to create
- **DEPENDENCIES**: per-service dependency tables (package names + version constraints)
- **CODING_STANDARDS**: indent size, quote style, semicolons, comment policy, naming rules
- **COMMIT_PLAN**: milestone table — what to commit and the validation command per milestone
- **VALIDATION_GATE**: the single final command that proves the full stack

---

## Step 2 — Scaffold Project

### 2a — Create directory structure

Create every directory from DIR_SKELETON. Do not write any implementation code yet — directories and config files only.

Create `.gitignore` at the repo root covering at minimum:
```
node_modules/
.env
*.db
dist/
.vite/
coverage/
```

**For any Vite-based frontend** in DIR_SKELETON, also create these two scaffold files at this step (Vite will not start without them):

- `{frontend}/index.html` — minimal HTML shell with `<div id="root"></div>` and `<script type="module" src="/src/main.jsx"></script>`
- `{frontend}/src/main.jsx` — React root mount: `createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)`

These are not application code — they are Vite's required entry points and belong in the scaffold commit, not Milestone 4.

### 2b — Create package.json files

Create one `package.json` per service listed in DIR_SKELETON, using the package names and version constraints from DEPENDENCIES in CODING_BRIEF.

Wire the `scripts` section so every milestone validation command from COMMIT_PLAN is defined (e.g. `test:domain`, `test:application`, `test:infrastructure`, `test:interface`, `test:e2e`, `test:all`). The root `package.json` `test:all` script must run each milestone command sequentially.

### 2c — Create environment files

For each service that reads from `process.env`, create two files:
- `.env.example` — all variable names with placeholder values and inline comments explaining each
- `.env` — same variables with working dev values:
  - **JWT secret**: generate with `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`
  - **Database path**: `./data/dev.db` (create the `data/` directory too)
  - **Ports**: assign non-conflicting defaults (e.g. backend: 3001, BFF: 3000, frontend: 5173)
  - **Service URLs**: wire each service to its dependency using the assigned ports (e.g. BFF `BACKEND_URL=http://localhost:3001`)
  - **CORS origin**: set to the frontend dev URL

### 2d — Git init and initial commit

Run in sequence:
```bash
git init {REPO_PATH}
```
Then stage `.gitignore` and all scaffold files (package.json files, .env.example files, directory structure) and commit:
```
chore: initialise repository structure
```

Do NOT commit `.env` files — they must be in `.gitignore`.

---

## Step 3 — Milestone 1: Domain Layer

### What to write

From DOMAIN_MODEL, implement every aggregate root, child entity, and value object as factory functions. Apply CODING_STANDARDS throughout.

**For each Value Object:**
- Factory function that validates its invariant and returns a frozen object
- Throws `{ code: 'VALIDATION_ERROR', message: '<specific message>' }` on violation
- No async, no I/O, no external imports

**For each Aggregate Root / Entity:**
- Factory function that accepts all properties, validates all invariants, and returns a frozen object
- Each invariant from DOMAIN_MODEL is a falsifiable check — enforce every one
- `isCompleted` (or equivalent boolean status field) defaults to `false` if not provided

**Repository interfaces:**
- Write JSDoc `@typedef` definitions for each repository interface from DOMAIN_MODEL
- Place in the application interfaces directory — these are contracts, not implementations
- Method signatures, parameter types, return types, and thrown error codes all from DOMAIN_MODEL

**Domain layer absolute rules — no exceptions:**
- Zero imports of database drivers, HTTP libraries, `fs`, or any I/O module
- All functions are pure and synchronous
- All exported functions have JSDoc
- Invariant violations throw `{ code: 'VALIDATION_ERROR', message: '...' }` — never HTTP status codes
- No class syntax — factory functions only (as specified in CODING_STANDARDS)

Write domain unit tests covering:
- Every invariant: one test that violates it, one that satisfies it
- Every value object: invalid format rejected, valid format accepted
- Default values: verify defaults are applied correctly on creation

### Gate

```bash
npm install          # run in each service directory that has new dependencies
npm run test:domain
```

- **Pass**: stage all domain and test files, commit:
  `"feat: implement domain layer — entities, value objects, invariants"`
- **Fail**: surface the full test output. Diagnose and fix the specific failure. Re-run. Do not commit. Do not continue to Milestone 2.

---

## Step 4 — Milestone 2: Application Layer

### What to write

From USE_CASES, implement one use case factory function per UC-XX. Pattern from CODING_STANDARDS:
```
fn({ repo1, repo2, logger }, inputParams)
```
Repositories are injected — never imported directly from infrastructure.

**Each use case must:**
- Call domain factory functions to create or mutate entities
- Call repository methods to persist
- Write a LogEntry (or equivalent audit record) for every mutation — this is a requirement, not optional
- Throw domain error codes (`NOT_FOUND`, `UNAUTHORIZED`, `CONFLICT`, `VALIDATION_ERROR`) based on business outcomes — never HTTP status codes
- Be fully async (database calls are async)

**Application layer rules:**
- Never import from infrastructure (no SQLite, no ORM, no `fs`)
- Never import from the interface layer
- Never mock domain entities in tests — use real domain factory functions
- Only mock repository interfaces

Write application unit tests from TEST_STRATEGY:
- Inject mocked repository interfaces (`jest.fn()` stubs returning controlled values)
- Cover every happy path scenario from USE_CASES
- Cover every unhappy path scenario (NOT_FOUND, UNAUTHORIZED, CONFLICT, VALIDATION_ERROR)
- Verify LogEntry repository is called on every mutation use case

### Gate

```bash
npm run test:application
```

- **Pass**: commit: `"feat: implement application layer — use cases {UC-01} to {UC-XX}"`
- **Fail**: surface output, fix, re-run. Do not continue.

---

## Step 5 — Milestone 3: Infrastructure Layer

### What to write

From DB_SCHEMA:
- **Database connection module**: singleton, initialised once at startup, returns the db instance
- **Migration runner**: executes the full DB_SCHEMA DDL idempotently on startup (`CREATE TABLE IF NOT EXISTS`)
- **One repository implementation per aggregate root** — implements the repository interface from Milestone 1:
  - `rowToEntity()`: maps DB row snake_case columns → domain object camelCase properties (per NAMING_DICT `sql_column` → `json_field` mapping)
  - `entityToRow()`: maps domain object camelCase → DB row snake_case on write
  - Boolean columns: convert integer 0/1 ↔ boolean true/false where the DB does not have a native boolean type
  - NOT_FOUND: when a query returns no row, throw `{ code: 'NOT_FOUND', message: '...' }`
  - CONFLICT: when a UNIQUE constraint violation occurs, throw `{ code: 'CONFLICT', message: '...' }`

Write infrastructure integration tests from TEST_STRATEGY:
- Use a real in-memory database (`:memory:`) — no mocks at all
- Run the migration runner before each test suite
- Test every repository method: `save`, `findById`, `findByX`, `delete`
- Test constraint violations produce the correct domain error codes

### Gate

```bash
npm run test:infrastructure
```

- **Pass**: commit: `"feat: implement infrastructure layer — SQLite repositories and schema migrations"`
- **Fail**: surface output, fix, re-run. Do not continue.

---

## Step 6 — Milestone 4: Interface Layer

### What to write

**Backend — Express routes and controllers** (from API_SCHEMA):

For each path + method in API_SCHEMA:
- One controller function that: parses the request, validates required fields, calls the use case, maps the result to the response shape
- Request body field names follow NAMING_DICT `json_field` values (camelCase)
- Response body field names follow NAMING_DICT `json_field` values (camelCase)
- Map domain error codes → HTTP status codes: `NOT_FOUND`→404, `UNAUTHORIZED`→401, `CONFLICT`→409, `VALIDATION_ERROR`→422
- Global error handler catches all thrown errors and maps to `{ error: string, message: string }` response

**Backend — non-negotiable interface rules (apply regardless of stack):**
- Error handler must return a static string for any unhandled error (status 500) — never
  forward the raw error message to the client; internal details stay server-side
- Log every unhandled error (console.error or equivalent) before responding — silent 500s
  make production debugging impossible
- Always create a `GET /health` route returning `200 { status: 'ok' }` with no auth
  requirement — this is expected by every load balancer, container runtime, and uptime monitor
- Boolean request fields must be validated as strict boolean type before use — never coerce
  with `Boolean()` or equivalent, which silently converts strings and integers incorrectly;
  return VALIDATION_ERROR if the field is present but not the correct type
- All inter-service URLs (backend URL in BFF, BFF URL in frontend) must be read from
  environment variables — never hardcoded; hardcoded URLs are the most common reason a
  prototype cannot be promoted to any other environment

**Field Definitions Catalog enforcement (when FIELD_DEFS is present):**
- For every field that appears in a request body, cross-reference its entry in FIELD_DEFS
- Enforce `minLength` / `maxLength` on string fields at the controller boundary, before
  the use case is called — do not rely solely on domain invariants catching these at the
  aggregate level
- Enforce `minimum` / `maximum` on numeric fields at the controller boundary
- Enforce `pattern` (regex) on string fields where specified in FIELD_DEFS
- Enforce `allowedValues` (enum) on constrained fields — return VALIDATION_ERROR for any
  value not in the allowed set
- Any field marked as strict boolean type in FIELD_DEFS must use the strict boolean check
  rule above — no exceptions even if the domain aggregate would catch it later
- If a field has no constraint entry in FIELD_DEFS, flag it as `[DECISION REQUIRED]` rather
  than implementing it without bounds

JWT authentication middleware:
- Verifies the Bearer token on every protected endpoint
- Attaches `userId` to the request object on success
- Returns 401 with a generic message on failure — no user enumeration, no token detail in the error

**BFF — Express proxy** (stateless, logic-free):
- One route per API_SCHEMA path group
- Forwards request method, path, headers (especially `Authorization`), and body to the backend verbatim
- Uses **Node.js 22 built-in `fetch`** — no `http-proxy-middleware` or other proxy library
- Returns backend response to the SPA verbatim
- On network failure (backend unreachable): returns 502

**Frontend — React SPA** (if in DIR_SKELETON):
- API service module: all calls go through BFF — never directly to the backend
- React Router for navigation between pages
- No business logic in components — only presentation and API calls
- One page per primary user flow derived from USE_CASES (e.g. auth page, main resource page)

**UI completeness rule — every USE_CASE operation must be reachable from the UI:**
- Read USE_CASES and API_SCHEMA together: for every endpoint that exists, there must be a UI control that invokes it
- Create forms must include inputs for every field the API accepts (required AND optional — e.g. description, due date), not just the minimum required field
- List views must display all fields the API returns that are meaningful to the user (title, status, due date, etc.)
- Each list item must have controls for every single-resource operation defined in API_SCHEMA: view detail, edit/update, delete, and any status-toggle actions
- Edit must be inline or via a form that pre-populates all current field values from the API response
- If USE_CASES defines a "view detail" scenario, implement a detail view or expandable row — do not omit it because the list already shows some fields

**Frontend — non-negotiable UI rules (apply regardless of framework):**
- All service URLs must come from environment variables (e.g. `VITE_BFF_URL`, `REACT_APP_API_URL`)
  with a localhost default — never a hardcoded string in source code
- Destructive actions (delete, deactivate, irreversible status changes) must require explicit
  user confirmation before the API call is made — a native confirm dialog is acceptable for a prototype

**Styling — minimal CSS (one stylesheet, no framework):**
- Create `src/index.css` and import it in `src/main.jsx`
- Style goal: clean, readable, demo-ready — not unstyled HTML, not a design system
- Apply at minimum: a max-width centered layout, consistent font (system-ui or similar), card/panel for list items, clear button styles (primary action distinct from destructive), form field spacing, and a subtle colour accent for the primary action
- Inline `style` props are acceptable for one-off adjustments; all base styles go in the stylesheet

Write interface integration tests (Supertest) from TEST_STRATEGY:
- Backend: drive every route with a real Express app instance backed by an in-memory database
- BFF: drive proxy routes with mocked backend HTTP responses (`jest.mock('./httpClient')` or equivalent)
- Verify HTTP status codes and JSON response shapes match API_SCHEMA exactly

### Gate

```bash
npm run test:interface
```

- **Pass**: commit: `"feat: implement interface layer — Express API, BFF proxy, React SPA"`
- **Fail**: surface output, fix, re-run. Do not continue.

---

## Step 7 — Milestone 5: E2E

### What to write

From TEST_STRATEGY E2E catalog, implement one test file per use case (UC-01.test.js, etc.) covering every Gherkin scenario marked as an E2E target.

Each E2E test:
- Sets up a fresh in-memory database via the migration runner
- Executes the full Gherkin scenario as real HTTP calls through Supertest against the full backend stack
- Asserts response status code, response body shape, and side effects (e.g. LogEntry written after every mutation)
- Tests are named exactly after the Gherkin scenario name from USE_CASES

Then run the full validation gate:

### Gate

```bash
npm run test:e2e
```

Then immediately run the full suite:

```bash
{VALIDATION_GATE}
```

- **Pass** (both commands green): commit: `"feat: E2E acceptance tests — all UC-01 to UC-XX scenarios passing"`
- **Fail**: surface output, fix, re-run. Do not commit a broken state.

---

## Step 8 — Report

```
Project       : {REPO_NAME}
Location      : {REPO_PATH}
Commits       : 6 (initial scaffold + 5 milestones)
Validation    : {VALIDATION_GATE} — PASS

To run locally:
  cd {REPO_PATH}/backend  && npm run dev    # backend API
  cd {REPO_PATH}/bff      && npm run dev    # BFF proxy
  cd {REPO_PATH}/frontend && npm run dev    # React SPA
```

List any `[DECISION REQUIRED]` items surfaced during implementation. If there are none, say so.

Then say: "Phase 3 complete. All milestone gates passed and committed. Proceed to Phase 4 (Terraform / cloud deployment) when ready."

---

## Rules

- **Never advance past a failed gate.** Fix the failure, re-run, confirm green before committing or moving on.
- **All names come from NAMING_DICT.** Use `canonical_name` for JS identifiers, `sql_column` for DB columns, `json_field` for API request/response fields. If a name is not in the dictionary, flag it with `[DECISION REQUIRED]`.
- **No invented business rules.** If a decision is not present in the Phase 2 contracts, mark it `[DECISION REQUIRED: <description>]` in a code comment and report it in Step 8.
- **Domain layer stays pure.** No I/O, no async, no external imports. No exceptions.
- **Application layer never imports infrastructure.** Repositories are always injected.
- **BFF uses Node.js 22 built-in fetch.** No proxy library.
- **Tests pass before committing.** The git log must only contain passing states.
- **`.env` is never committed.** Only `.env.example` goes into git.
