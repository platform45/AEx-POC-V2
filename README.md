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
│   │   ├── db/
│   │   │   ├── session.py        # Async SQLAlchemy engine + session factory
│   │   │   └── models.py         # CaseContext model with pgvector embedding
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