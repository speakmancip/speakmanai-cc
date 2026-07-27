# generate-speakmanai-code-js — JavaScript / Node.js Variant

This file is read by the `generate-speakmanai-code` router (Step 1c) to extract LANG_CONFIG
for JavaScript / Node.js projects. It is not invoked directly.

---

## LANG_CONFIG

### CODING_STANDARDS

- **Indent**: 2 spaces
- **Quotes**: single quotes
- **Semicolons**: none
- **Functions**: factory functions only — no `class` syntax anywhere in the codebase
- **Documentation**: JSDoc on all exported functions and types
- **HTTP between services**: Node.js 22 built-in `fetch` — no axios, got, or node-fetch
- **Field naming**:
  - JS identifiers and JSON fields: camelCase (per NAMING_DICT `canonical_name` / `json_field`)
  - SQL columns: snake_case (per NAMING_DICT `sql_column`)
  - All canonical names in NAMING_DICT take precedence over inferred names

---

### DIR_SKELETON_LAYOUT

```
{REPO_PATH}/
  backend/
    src/
      domain/
        {aggregate}/          ← one directory per aggregate root in DOMAIN_MODEL
      application/
        useCases/
        interfaces/           ← repository interface @typedef definitions
      infrastructure/
        database/
        {external-service}/   ← one directory per external service in API_SCHEMA tags
      interface/
        routes/
        controllers/
        middlewares/
    tests/
      domain/
      application/
      infrastructure/
      interface/
      e2e/
    data/                     ← dev SQLite file lives here (gitignored)
  bff/
    src/                      ← always present; BFF is always a separate Node.js service
  frontend/
    src/
      components/
      pages/
      hooks/
    public/                   ← if frontend is in TECH_STACK (React/Vite)
```

The `bff/` directory is always present regardless of frontend choice. If no SPA framework
is in TECH_STACK, `frontend/` is omitted.

---

### DEPENDENCIES_DERIVATION

Derive npm packages per service:

**backend/**
- Framework from TECH_STACK (e.g. `express`)
- DB driver from TECH_STACK: SQLite → `better-sqlite3`; Postgres → `pg`
- From API_SCHEMA security schemes: `jsonwebtoken` if BearerAuth present
- From DOMAIN_MODEL / FIELD_DEFS: `bcryptjs` if password hashing referenced; `uuid` if
  random UUIDs are generated (Node.js 22 has `crypto.randomUUID()` — add `uuid` only if
  the runtime is older)
- From API_SCHEMA operation tags / descriptions: external SDKs (e.g. Stripe → `stripe`;
  AWS SES → `@aws-sdk/client-ses`)
- TEST_STRATEGY tooling column: `jest`, `supertest`
- Always: `dotenv` for env var loading in dev

**bff/**
- Framework from TECH_STACK for the BFF (usually `express`)
- `dotenv`
- TEST_STRATEGY: `jest`, `supertest`

**frontend/** (if present)
- SPA library from TECH_STACK: e.g. `react`, `react-dom`, `react-router-dom`
- Build tool: `vite`, `@vitejs/plugin-react`
- No test tooling on frontend unless TEST_STRATEGY specifies it

**root package.json** (no runtime code — scripts only)

---

### SCAFFOLD_CONFIG

Create one `package.json` per service directory plus a root `package.json`.

**Root package.json scripts block:**
```json
{
  "scripts": {
    "test:domain":         "cd backend && npm run test:domain",
    "test:application":    "cd backend && npm run test:application",
    "test:infrastructure": "cd backend && npm run test:infrastructure",
    "test:interface":      "cd backend && npm run test:interface",
    "test:e2e":            "cd backend && npm run test:e2e",
    "test":                "npm run test:domain && npm run test:application && npm run test:infrastructure && npm run test:interface && npm run test:e2e"
  }
}
```

**backend/package.json scripts block:**
```json
{
  "scripts": {
    "test:domain":         "jest tests/domain --runInBand",
    "test:application":    "jest tests/application --runInBand",
    "test:infrastructure": "jest tests/infrastructure --runInBand",
    "test:interface":      "jest tests/interface --runInBand",
    "test:e2e":            "jest tests/e2e --runInBand",
    "test":                "jest --runInBand",
    "dev":                 "node --watch src/index.js"
  }
}
```

---

### SCAFFOLD_FILES

For any Vite-based frontend in DIR_SKELETON, create these two files at scaffold time
(Vite will not start without them — they are not application code):

- `frontend/index.html` — minimal HTML shell:
  ```html
  <!DOCTYPE html>
  <html lang="en">
    <head><meta charset="UTF-8" /><title>{REPO_NAME}</title></head>
    <body>
      <div id="root"></div>
      <script type="module" src="/src/main.jsx"></script>
    </body>
  </html>
  ```

- `frontend/src/main.jsx` — React root mount:
  ```jsx
  import { StrictMode } from 'react'
  import { createRoot } from 'react-dom/client'
  import './index.css'
  import App from './App'
  createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)
  ```

---

### GITIGNORE_ENTRIES

```
node_modules/
.env
*.db
dist/
.vite/
coverage/
```

---

### SECRET_GENERATION_CMD

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Use this to generate the JWT secret in the dev `.env` file.

---

### VALIDATION_GATE

```bash
npm test
```

(Run from repo root — delegates to all per-layer test suites.)

---

### MILESTONE_GATES

```
install:        npm install                 (run in each service directory that has new/changed dependencies)
domain:         npm run test:domain         (run from backend/)
application:    npm run test:application    (run from backend/)
infrastructure: npm run test:infrastructure (run from backend/)
interface:      npm run test:interface      (run from backend/)
e2e:            npm run test:e2e            (run from backend/)
ui_build:       npm run build               (run from frontend/)
```

---

### LOCAL_DB_TEST

SQLite in-memory: pass `:memory:` as the database path when constructing the connection
in test suites. `better-sqlite3` accepts this string directly. No file is created on disk.

---

### DOMAIN_IMPLEMENTATION_GUIDE

Implement each aggregate root, child entity, and value object as a **factory function**
that returns a frozen object.

**Value Object pattern:**
```javascript
/**
 * @param {string} value
 * @returns {{ value: string }}
 */
const createEmail = (value) => {
  if (!value || !value.includes('@')) {
    throw { code: 'VALIDATION_ERROR', message: 'Email must be a valid email address' }
  }
  return Object.freeze({ value: value.toLowerCase() })
}
```

**Aggregate Root pattern:**
```javascript
/**
 * @param {{ id: string, title: string, isCompleted?: boolean }} props
 * @returns {TodoItem}
 */
const createTodoItem = ({ id, title, isCompleted = false }) => {
  if (!id) throw { code: 'VALIDATION_ERROR', message: 'id is required' }
  if (!title || title.length === 0) throw { code: 'VALIDATION_ERROR', message: 'title is required' }
  return Object.freeze({ id, title, isCompleted })
}
```

**Invariant violations**: always `throw { code: 'VALIDATION_ERROR', message: '...' }` — never
HTTP status codes, never `new Error(...)` without the `code` property.

**No `class` syntax anywhere.** No `async` in domain functions. No imports of db, http, or fs.

---

### REPO_INTERFACE_PATTERN

Define repository interfaces as JSDoc `@typedef` in `backend/src/application/interfaces/`:

```javascript
/**
 * @typedef {Object} TodoRepository
 * @property {function(TodoItem): Promise<void>} save
 * @property {function(string): Promise<TodoItem|null>} findById
 * @property {function(): Promise<TodoItem[]>} findAll
 * @property {function(string): Promise<void>} delete
 */
```

These are contracts only — no implementation code in this directory.

---

### DOMAIN_TEST_GUIDE

Use Jest. One test file per aggregate / value object in `backend/tests/domain/`.

```javascript
describe('createTodoItem', () => {
  it('throws VALIDATION_ERROR when title is empty', () => {
    expect(() => createTodoItem({ id: '1', title: '' }))
      .toThrow(expect.objectContaining({ code: 'VALIDATION_ERROR' }))
  })

  it('creates a valid todo item with defaults', () => {
    const item = createTodoItem({ id: '1', title: 'Buy milk' })
    expect(item.isCompleted).toBe(false)
  })
})
```

---

### APPLICATION_IMPLEMENTATION_GUIDE

Implement each UC-XX as a factory-injected function:

```javascript
/**
 * @param {{ todoRepo: TodoRepository, auditRepo: AuditRepository }} repos
 * @param {{ title: string, userId: string }} params
 * @returns {Promise<TodoItem>}
 */
const createTodoItem = async ({ todoRepo, auditRepo }, { title, userId }) => {
  const item = domain.createTodoItem({ id: crypto.randomUUID(), title })
  await todoRepo.save(item)
  await auditRepo.save({ action: 'TODO_CREATED', entityId: item.id, userId, at: new Date().toISOString() })
  return item
}
```

Repositories are always injected — never imported. Never import from infrastructure or interface.
Use `jest.fn()` stubs as the injected repositories in tests.

---

### APPLICATION_TEST_GUIDE

```javascript
describe('createTodoItem use case', () => {
  let todoRepo, auditRepo

  beforeEach(() => {
    todoRepo = { save: jest.fn(), findById: jest.fn(), findAll: jest.fn(), delete: jest.fn() }
    auditRepo = { save: jest.fn() }
  })

  it('saves the item and writes an audit entry', async () => {
    todoRepo.save.mockResolvedValue()
    auditRepo.save.mockResolvedValue()

    const result = await createTodoItem({ todoRepo, auditRepo }, { title: 'Buy milk', userId: 'u1' })

    expect(result.title).toBe('Buy milk')
    expect(todoRepo.save).toHaveBeenCalledTimes(1)
    expect(auditRepo.save).toHaveBeenCalledTimes(1)
  })

  it('throws NOT_FOUND when item does not exist on update', async () => {
    todoRepo.findById.mockResolvedValue(null)
    await expect(updateTodoItem({ todoRepo, auditRepo }, { id: 'x', title: 'New' }))
      .rejects.toMatchObject({ code: 'NOT_FOUND' })
  })
})
```

---

### INFRASTRUCTURE_IMPLEMENTATION_GUIDE

Use `better-sqlite3` for SQLite. The connection module exports a singleton `db` instance.

**Connection module** (`backend/src/infrastructure/database/connection.js`):
```javascript
import Database from 'better-sqlite3'
let _db = null
export const getDb = (dbPath = process.env.DB_PATH || './data/dev.db') => {
  if (!_db) _db = new Database(dbPath)
  return _db
}
```

**Migration runner** — executes idempotent DDL on startup:
```javascript
import { readFileSync } from 'fs'
export const runMigrations = (db) => {
  db.exec(`CREATE TABLE IF NOT EXISTS todo_items ( ... )`)
}
```

**Repository implementation** — one per aggregate:
```javascript
const rowToEntity = (row) => ({
  id: row.id,
  title: row.title,
  isCompleted: Boolean(row.is_completed),
})

export const createTodoRepository = (db) => ({
  save: (item) => {
    db.prepare('INSERT OR REPLACE INTO todo_items (id, title, is_completed) VALUES (?, ?, ?)')
      .run(item.id, item.title, item.isCompleted ? 1 : 0)
  },
  findById: (id) => {
    const row = db.prepare('SELECT * FROM todo_items WHERE id = ?').get(id)
    if (!row) throw { code: 'NOT_FOUND', message: `Todo item ${id} not found` }
    return rowToEntity(row)
  },
  findAll: () => db.prepare('SELECT * FROM todo_items ORDER BY created_at DESC').all().map(rowToEntity),
  delete: (id) => db.prepare('DELETE FROM todo_items WHERE id = ?').run(id),
})
```

CONFLICT: catch SQLite `SQLITE_CONSTRAINT` error and rethrow `{ code: 'CONFLICT', message: '...' }`.

---

### INFRASTRUCTURE_TEST_GUIDE

Use real in-memory SQLite — no mocks:
```javascript
import Database from 'better-sqlite3'
import { runMigrations } from '../../src/infrastructure/database/migrations.js'
import { createTodoRepository } from '../../src/infrastructure/database/todoRepository.js'

describe('TodoRepository', () => {
  let db, repo

  beforeEach(() => {
    db = new Database(':memory:')
    runMigrations(db)
    repo = createTodoRepository(db)
  })

  it('saves and retrieves by ID', () => {
    const item = domain.createTodoItem({ id: '1', title: 'Test' })
    repo.save(item)
    expect(repo.findById('1').title).toBe('Test')
  })

  it('throws NOT_FOUND for unknown ID', () => {
    expect(() => repo.findById('nonexistent')).toThrow(expect.objectContaining({ code: 'NOT_FOUND' }))
  })
})
```

---

### INTERFACE_IMPLEMENTATION_GUIDE

**Backend — Express routes:**

```javascript
import express from 'express'
import { createTodoItem } from '../../application/useCases/createTodoItem.js'

export const todoRouter = express.Router()

todoRouter.post('/', async (req, res, next) => {
  try {
    const { title } = req.body
    if (typeof title !== 'string' || title.length === 0) {
      return res.status(422).json({ error: 'VALIDATION_ERROR', message: 'title is required' })
    }
    const item = await createTodoItem(req.repos, { title, userId: req.auth.userId })
    res.status(201).json(item)
  } catch (err) {
    next(err)
  }
})
```

**Global error handler** (register last, after all routes):
```javascript
app.use((err, req, res, next) => {
  const STATUS = { NOT_FOUND: 404, UNAUTHORIZED: 401, CONFLICT: 409, VALIDATION_ERROR: 422 }
  const status = STATUS[err.code] ?? 500
  if (status === 500) console.error('Unhandled error', err)
  res.status(status).json({
    error: err.code ?? 'INTERNAL_ERROR',
    message: status === 500 ? 'Internal server error' : err.message,
  })
})
```

**JWT middleware** (`backend/src/interface/middlewares/auth.js`):
```javascript
import jwt from 'jsonwebtoken'
export const requireAuth = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1]
  try {
    req.auth = jwt.verify(token, process.env.JWT_SECRET)
    next()
  } catch {
    res.status(401).json({ error: 'UNAUTHORIZED', message: 'Invalid or missing token' })
  }
}
```

---

### BFF_PRESENT

`true` — the BFF is always a separate Node.js service when JavaScript is the stack.

---

### BFF_IMPLEMENTATION

The BFF is an Express app that proxies to the backend using Node.js 22 built-in `fetch`.
No `http-proxy-middleware` or other proxy library.

```javascript
import express from 'express'
const app = express()
const BACKEND_URL = process.env.BACKEND_URL  // e.g. http://localhost:3001

app.use(express.json())

app.all('/api/*', async (req, res) => {
  const url = `${BACKEND_URL}${req.path}${req.search ?? ''}`
  try {
    const upstream = await fetch(url, {
      method: req.method,
      headers: { ...req.headers, host: undefined },
      body: ['GET', 'HEAD'].includes(req.method) ? undefined : JSON.stringify(req.body),
    })
    const data = await upstream.json()
    res.status(upstream.status).json(data)
  } catch {
    res.status(502).json({ error: 'BAD_GATEWAY', message: 'Backend service unavailable' })
  }
})
```

---

### INTERFACE_TEST_GUIDE

Use `supertest` against a real Express app backed by an in-memory database:

```javascript
import request from 'supertest'
import { buildApp } from '../../src/interface/app.js'
import Database from 'better-sqlite3'
import { runMigrations } from '../../src/infrastructure/database/migrations.js'

describe('POST /api/todos', () => {
  let app, db

  beforeEach(() => {
    db = new Database(':memory:')
    runMigrations(db)
    app = buildApp(db)
  })

  it('returns 201 with the created item', async () => {
    const token = signTestToken()
    const res = await request(app)
      .post('/api/todos')
      .set('Authorization', `Bearer ${token}`)
      .send({ title: 'Buy milk' })
    expect(res.status).toBe(201)
    expect(res.body.title).toBe('Buy milk')
  })

  it('returns 422 when title is missing', async () => {
    const token = signTestToken()
    const res = await request(app)
      .post('/api/todos')
      .set('Authorization', `Bearer ${token}`)
      .send({})
    expect(res.status).toBe(422)
  })
})
```

---

### E2E_IMPLEMENTATION_GUIDE

One test file per UC-ID named `UC-{XX}.test.js` in `backend/tests/e2e/`. Use `supertest`
against a full backend instance backed by an in-memory database. The frontend and BFF are NOT
involved in E2E tests — test the backend directly through HTTP.

Chain calls through the API — no seeding at journey seams:
```javascript
// Create a user via POST /api/auth/register, extract the token from the response,
// then use that token to create a todo. Never insert the user directly into the database.
const registerRes = await request(app).post('/api/auth/register').send({ username: 'alice', password: 'Password123!' })
const { token } = registerRes.body

const createRes = await request(app)
  .post('/api/todos')
  .set('Authorization', `Bearer ${token}`)
  .send({ title: 'Buy milk' })
expect(createRes.status).toBe(201)
const { id } = createRes.body

const getRes = await request(app).get(`/api/todos/${id}`).set('Authorization', `Bearer ${token}`)
expect(getRes.body.title).toBe('Buy milk')
```

---

### RUN_LOCALLY_INSTRUCTIONS

```
cd {REPO_PATH}/backend  && npm run dev    # backend API
cd {REPO_PATH}/bff      && npm run dev    # BFF proxy
cd {REPO_PATH}/frontend && npm run dev    # React SPA (Vite)
```
