# Contributing a New Language Stack

The `generate-speakmanai-code` skill is a **router + variants** system. The router
(`SKILL.md`) contains the DDD pipeline structure and milestone gates that apply to every
language. The variants contain the language-specific implementation details.

To add a new language stack, you write a single variant file and register the language
keyword in the router's table. That's it — you never modify the router itself.

---

## Registered Variants

| Language / Stack | Variant directory | Matches when TECH_STACK contains… |
|---|---|---|
| JavaScript / Node.js | `generate-speakmanai-code-js/` | "JavaScript", "Node.js", "TypeScript" |
| Go | `generate-speakmanai-code-go/` | "Go", "Golang" |

To register a new variant, add a row to the table above in the router's `SKILL.md`
Step 1c section.

---

## What a Variant Must Provide

Your variant `SKILL.md` must define a `## LANG_CONFIG` section containing every key below.
The router reads this file and uses these values verbatim — any key you omit will cause the
router to fail with a missing-config error.

### Required keys

| Key | Type | Purpose |
|---|---|---|
| `CODING_STANDARDS` | prose | Indent, naming, idiom rules for the language |
| `DIR_SKELETON_LAYOUT` | directory tree | Service/package layout; use `{aggregate}` as a placeholder |
| `DEPENDENCIES_DERIVATION` | table or prose | How to derive the dependency list per service |
| `SCAFFOLD_CONFIG` | manifest examples | What config files to create at scaffold time |
| `SCAFFOLD_FILES` | file list | Build-tool entry points required before any code is written |
| `GITIGNORE_ENTRIES` | text block | `.gitignore` content for this stack |
| `SECRET_GENERATION_CMD` | bash command | Command to generate a random 32-byte hex secret |
| `VALIDATION_GATE` | bash command | Single command that runs the full test suite |
| `MILESTONE_GATES` | table | Per-milestone commands: `install`, `domain`, `application`, `infrastructure`, `interface`, `e2e`, `ui_build`. The `install` key is the dependency install command (e.g. `npm install`, `go mod download`) — the router runs it before each gate when new dependencies are declared |
| `LOCAL_DB_TEST` | prose | In-memory database DSN / configuration for integration tests |
| `DOMAIN_IMPLEMENTATION_GUIDE` | prose + code | How to represent aggregates and value objects |
| `REPO_INTERFACE_PATTERN` | prose + code | How to define repository interface contracts |
| `DOMAIN_TEST_GUIDE` | prose + code | How to write domain unit tests |
| `APPLICATION_IMPLEMENTATION_GUIDE` | prose + code | Use case function / class pattern |
| `APPLICATION_TEST_GUIDE` | prose + code | How to stub repositories in application tests |
| `INFRASTRUCTURE_IMPLEMENTATION_GUIDE` | prose + code | DB connection, migrations, repository implementation |
| `INFRASTRUCTURE_TEST_GUIDE` | prose + code | How to run integration tests against real in-memory DB |
| `INTERFACE_IMPLEMENTATION_GUIDE` | prose + code | HTTP handlers, error mapping, JWT middleware |
| `BFF_PRESENT` | `true` or `false` | Whether a BFF proxy service is generated |
| `BFF_IMPLEMENTATION` | prose + code | Required if BFF_PRESENT is true |
| `INTERFACE_TEST_GUIDE` | prose + code | How to write interface-layer integration tests |
| `E2E_IMPLEMENTATION_GUIDE` | prose + code | E2E test pattern — real HTTP server + real DB, no seeding at seams |
| `RUN_LOCALLY_INSTRUCTIONS` | text block | Multi-line instructions shown in Step 9 report |

---

## Non-Negotiable Rules (Built Into the Router)

These rules apply to every language variant. Your implementation guide must be consistent
with them — do not override them in the variant file.

- **Domain layer**: pure, synchronous, no I/O imports. Constructor functions return errors
  carrying `code: VALIDATION_ERROR` — never HTTP status codes.
- **Application layer**: repositories are injected, never imported. Audit log written on
  every mutation. Business errors use domain codes only.
- **Infrastructure layer**: NOT_FOUND and CONFLICT must be surfaced as domain errors.
  Integration tests use a real in-memory database — no mocks.
- **Interface layer**: 500 errors return a static string. `GET /health` has no auth
  requirement. Boolean fields are strict-type validated. All inter-service URLs come from
  environment variables.
- **E2E tests**: no database seeding at use case seams — obtain produced values from the
  real API response.
- **Dev env file** (`.env`, etc.) is never committed.

---

## Variant File Template

Copy this template to `generate-speakmanai-code-{lang}/SKILL.md` and fill in every section.
Delete any placeholder comments before publishing.

```markdown
# generate-speakmanai-code-{lang} — {Language Name} Variant

This file is read by the `generate-speakmanai-code` router (Step 1c) to extract LANG_CONFIG
for {Language Name} projects. It is not invoked directly.

---

## LANG_CONFIG

### CODING_STANDARDS
<!-- indent, naming conventions, style rules -->

### DIR_SKELETON_LAYOUT
<!-- directory tree using {aggregate} placeholder; note which dirs are "always present" -->

### DEPENDENCIES_DERIVATION
<!-- table or prose: how to decide which packages/modules to include per service -->

### SCAFFOLD_CONFIG
<!-- manifest file examples: go.mod / package.json / pom.xml / etc. -->

### SCAFFOLD_FILES
<!-- entry-point files required by the build tool at scaffold time -->

### GITIGNORE_ENTRIES
<!-- .gitignore content block -->

### SECRET_GENERATION_CMD
<!-- bash command to generate a 32-byte random hex secret -->

### VALIDATION_GATE
<!-- single command that runs the full test suite -->

### MILESTONE_GATES
<!-- install / domain / application / infrastructure / interface / e2e / ui_build commands -->
<!-- install = the dependency install command for this language (npm install, go mod download, mvn dependency:resolve, etc.) -->

### LOCAL_DB_TEST
<!-- in-memory database DSN or config for integration tests -->

### DOMAIN_IMPLEMENTATION_GUIDE
<!-- struct/class/record patterns, error types, invariant enforcement -->

### REPO_INTERFACE_PATTERN
<!-- how repository interfaces are declared (interface, protocol, @typedef, etc.) -->

### DOMAIN_TEST_GUIDE
<!-- test framework, assertion library, naming convention -->

### APPLICATION_IMPLEMENTATION_GUIDE
<!-- use case function signature, dependency injection pattern, audit log call -->

### APPLICATION_TEST_GUIDE
<!-- how to stub/mock repository interfaces in application tests -->

### INFRASTRUCTURE_IMPLEMENTATION_GUIDE
<!-- DB connection singleton, migration runner, repository implementation, error mapping -->

### INFRASTRUCTURE_TEST_GUIDE
<!-- real in-memory DB setup, test lifecycle (before/after each suite) -->

### INTERFACE_IMPLEMENTATION_GUIDE
<!-- HTTP handler pattern, error → HTTP status mapping, JWT middleware -->

### BFF_PRESENT
<!-- true or false -->

### BFF_IMPLEMENTATION
<!-- proxy pattern for the BFF layer; omit if BFF_PRESENT is false -->

### INTERFACE_TEST_GUIDE
<!-- test server setup, assertion patterns for HTTP tests -->

### E2E_IMPLEMENTATION_GUIDE
<!-- real HTTP server, test file naming convention, no-seeding-at-seams pattern -->

### RUN_LOCALLY_INSTRUCTIONS
<!-- multi-line: how to start each service for local development -->
```

---

## Testing Your Variant

Validate by running the full pipeline against a minimal but complete Phase 2 contract set.
A good test project is a simple "todo list" application with:
- 3–4 use cases (create, list, update, delete)
- A `TodoItem` aggregate with 2–3 invariants
- JWT authentication
- One external service (optional)

The variant is considered working when all 6 milestone gates pass and the final
`make test` / `npm test` / equivalent is green.

---

## Submitting

1. Create `generate-speakmanai-code-{lang}/SKILL.md` following the template above
2. Add a row to the router's Step 1c variant table in `generate-speakmanai-code/SKILL.md`
3. Add a row to the Registered Variants table at the top of this `CONTRIBUTING.md`
4. Open a PR with a short description of: the language/framework, the test project used
   for validation, and any non-obvious design decisions in your variant
