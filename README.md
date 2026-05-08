# AEx AI

AI platform for a fibre/telecoms operator, progressively moving from structured diagnostic tooling toward autonomous network issue resolution.

**Phase 1** — Expose NMS/ZMS endpoints into a structured interface. Engineer diagnostic sessions are captured as context objects and stored in a vector database.

**Phase 2** — When a new issue is raised, the agent retrieves semantically similar past cases and suggests a diagnosis and actions. Engineers review and approve each action before execution. Results are logged back, continuously improving accuracy.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python + FastAPI |
| AI Orchestration | LangGraph |
| LLM | Anthropic Claude API |
| Vector DB | pgvector (Postgres) |
| Frontend | Next.js 15 + React 19 + Tailwind 4 |
| Containerisation | Docker + Docker Compose |
| Reverse Proxy | Nginx |

---

## Project Structure

```
aex_rag/
├── app/                          # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx          # Dashboard
│   │   │   └── diagnostics/
│   │   │       └── page.tsx
│   │   ├── components/ui/        # Shared UI components
│   │   └── lib/
│   │       └── api.ts            # Typed API client
│   ├── Dockerfile
│   └── .env.example
│
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py               # App entry point, CORS, router mount
│   │   ├── api/v1/
│   │   │   ├── router.py
│   │   │   ├── diagnostics.py    # NMS/ZMS diagnostic routes
│   │   │   └── cases.py          # Context case CRUD routes
│   │   ├── agent/
│   │   │   ├── graph.py          # LangGraph StateGraph (retrieve → suggest → execute)
│   │   │   ├── nodes.py          # Node functions
│   │   │   └── state.py          # AgentState TypedDict
│   │   ├── agent_tools/
│   │   │   ├── state.py          # IssueResolveState TypedDict
│   │   │   ├── db_ops.py         # issue_resolve CRUD (fetch, insert, resolve)
│   │   │   ├── nodes.py          # Conversational node functions
│   │   │   ├── graph.py          # LangGraph graph with interrupt_before checkpoints
│   │   │   └── tool_use.py       # Controller: start_session / respond_to_session
│   │   ├── db/
│   │   │   ├── session.py        # Async SQLAlchemy engine + session factory
│   │   │   └── models.py         # CaseContext and IssueResolve ORM models
│   │   ├── services/
│   │   │   ├── embedding.py      # Anthropic embedding helper
│   │   │   ├── vector_search.py  # pgvector similarity search
│   │   │   └── nms_client.py     # NMS/ZMS HTTP client
│   │   └── core/
│   │       └── config.py         # Pydantic BaseSettings
│   ├── alembic/                  # Database migrations
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── nginx/
│   ├── nginx.conf                # /api → backend:8000, / → app:3000
│   └── Dockerfile
│
├── db/
│   ├── schema.sql                # Table definitions, pgvector extension, indexes
│   ├── seed.sql                  # Development seed data (8 telecoms cases)
│   ├── seed_issue_resolve.sql    # Development seed data for issue_resolve (10 records)
│   └── schema.dbml               # DBML schema for dbdiagram.io
│
├── context/                      # Project context documents
├── docker-compose.yml
├── .gitignore
└── .env.example
```

---

## Running Locally

### Prerequisites

- Docker and Docker Compose
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Configure environment variables

```bash
cp backend/.env.example backend/.env
cp app/.env.example app/.env
```

Edit `backend/.env` and set your API key:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/aex_rag
ANTHROPIC_API_KEY=sk-ant-...
ENVIRONMENT=development
```

`app/.env` defaults work for local Docker:

```env
NEXT_PUBLIC_API_URL=http://localhost
```

### 2. Start the stack

```bash
docker compose up --build
```

This starts two services:

| Service | Port | Description |
|---|---|---|
| `db` | 5432 | Postgres + pgvector |
| `backend` | 8000 | FastAPI API |

The API is available at `http://localhost:8000`.

> **Database initialisation** — on first boot, Postgres automatically runs `db/schema.sql` (creates tables and indexes) followed by `db/seed.sql` (loads development data). No manual migration step is needed. If you need a clean slate, run `docker compose down -v` to destroy the volume, then `docker compose up` again.

### 3. Verify

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## Development

### Backend (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit .env
uvicorn app.main:app --reload --port 8000
```

### Frontend (without Docker)

```bash
cd app
npm install
cp .env.example .env.local
npm run dev
```

### Running backend tests

```bash
cd backend
pytest
```

---

## API Routes

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/diagnostics/{device_id}` | Fetch diagnostic data for a device |
| `POST` | `/api/v1/diagnostics/run` | Run a diagnostic action |
| `GET` | `/api/v1/cases` | List stored context cases |
| `POST` | `/api/v1/cases` | Create a new context case |
| `GET` | `/api/v1/cases/{case_id}` | Retrieve a specific case |
| `POST` | `/api/v1/issues/session` | Start an issue resolution session |
| `POST` | `/api/v1/issues/session/{session_id}/respond` | Send a response in an active session |

Interactive API docs are available at `http://localhost:8000/docs` when the backend is running directly.

---

## Agent Flow

The LangGraph agent follows a human-in-the-loop pattern:

```
retrieve → suggest → [interrupt: human review] → execute
```

1. **retrieve** — semantic search of the vector DB for similar past cases
2. **suggest** — Claude generates a diagnosis and recommended actions
3. **interrupt** — execution is paused for engineer approval
4. **execute** — approved actions are sent to NMS/ZMS

Results are written back to the vector DB after execution.


---

## Issue Resolution Agent

The issue resolution agent is a conversational, multi-turn flow that logs a device issue, attempts to resolve it using historical data, and records the outcome. It lives in `backend/app/agent_tools/`.

### Files

| File | Role |
|---|---|
| `agent_tools/state.py` | `IssueResolveState` TypedDict — holds all conversation state (device ID, messages, retry count, etc.) |
| `agent_tools/db_ops.py` | Three async DB helpers: `fetch_device_issues`, `insert_issue`, `resolve_issue` |
| `agent_tools/nodes.py` | One async function per conversation step, plus the `route_after_resolved` conditional router |
| `agent_tools/graph.py` | Assembles the LangGraph `StateGraph`, wires edges, and compiles with `MemorySaver` + `interrupt_before` |
| `agent_tools/tool_use.py` | Controller used by the API: `start_session` and `respond_to_session` |
| `api/v1/issues.py` | Two FastAPI endpoints that delegate to the controller |

### Conversation flow

```
POST /issues/session
        │
        ▼
  prompt_device_id  ──── returns first message ────► client
        │ (interrupt)
        ▼ user sends device ID
  capture_device_id  ── fetches issue history from DB
        │
  prompt_issue  ── summarises history, asks for issue description ────► client
        │ (interrupt)
        ▼ user sends issue description
  capture_issue  ── inserts new unresolved row into issue_resolve
        │
  build_resolution  ── calls Claude with device history as context
        │
  prompt_resolved  ── sends suggestion, asks "is this resolved?" ────► client
        │ (interrupt)
        ▼ user sends yes / no
  capture_resolved
        │
        ├── yes  ──► finish_resolved  ── marks row resolved in DB  ──► done
        │
        ├── no, attempts < 2  ──► build_resolution  (retry loop)
        │
        └── no, attempts = 2  ──► escalate  ── directs user to support  ──► done
```

Each `(interrupt)` point pauses the graph. The client sends the user's reply via `POST /issues/session/{session_id}/respond`, which updates the checkpointed state and resumes execution. Session state is held in memory by LangGraph's `MemorySaver` and keyed by `session_id`.

### Example usage

```bash
# 1. Start a session
curl -X POST http://localhost:8000/api/v1/issues/session
# → { "session_id": "abc-123", "message": "Please provide the device ID...", "done": false }

# 2. Send device ID
curl -X POST http://localhost:8000/api/v1/issues/session/abc-123/respond \
  -H "Content-Type: application/json" \
  -d '{"input": "OLT-CPT-001"}'
# → { "message": "I found 3 previous issue(s)... Please describe the current issue.", "done": false }

# 3. Send issue description
curl -X POST http://localhost:8000/api/v1/issues/session/abc-123/respond \
  -H "Content-Type: application/json" \
  -d '{"input": "Port 0/1/2 showing LOS alarm"}'
# → { "message": "Based on device history, here is a suggested resolution:\n...\nHas this resolved the issue?", "done": false }

# 4a. Confirm resolved
curl -X POST http://localhost:8000/api/v1/issues/session/abc-123/respond \
  -H "Content-Type: application/json" \
  -d '{"input": "yes"}'
# → { "message": "Great! The issue has been marked as resolved.", "done": true, "escalated": false }

# 4b. Or report unresolved (retries up to 2 attempts, then escalates)
curl -X POST http://localhost:8000/api/v1/issues/session/abc-123/respond \
  -H "Content-Type: application/json" \
  -d '{"input": "no"}'
```

### Database table

The `issue_resolve` table stores the record of each issue and its outcome.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `device_id` | VARCHAR(100) | Device the issue relates to |
| `issue_description` | TEXT | Description provided by the user |
| `resolved` | BOOLEAN | Whether the issue was resolved |
| `resolution_description` | TEXT | Steps taken to resolve (null if unresolved) |
| `created_at` | TIMESTAMPTZ | When the issue was logged |
| `resolved_at` | TIMESTAMPTZ | When it was marked resolved (null if unresolved) |

---

## Testing endpoints

Can be done on `http://localhost:8000/docs` 


## Testing Frontend

cd app
cp .env.example .env.local

set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local

npm run dev


### Frontend Troubleshooting 
If styling doesn't seem to appear:
```
rm -rf .next
npm run dev 
```