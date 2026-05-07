### AEx AI – Phase 1 & 2 Overview

AEx is building an AI platform for a fibre/telecoms operator, progressively moving from data querying toward autonomous network issue resolution.

---

**Phase 1 – Troubleshooting Interface & Context Logging (2–4 weeks)**
Expose all NMS/ZMS endpoints and data used by network engineers into a structured interface. When engineers run diagnostic calls, a context object (inputs, actions, results, outcome) is built and stored in a Vector DB. This creates the dataset that powers Phase 2.

**Phase 2 – Human-in-the-Loop Agent (2–4 weeks)**
When a new issue is raised, the agent semantically searches the Vector DB for similar past cases and uses that context to suggest a diagnosis and recommended actions. Engineers review and approve each action before execution. Results are logged back to the Vector DB, continuously improving the agent's accuracy.

---

**Critical dependency:** Almost no NMS actions are currently exposed and much of the relevant data sits only in ZMS databases — resolving this is the critical path for both phases.

---

**Tech Stack**

| Layer | Technology |
|---|---|
| Backend API | Python + FastAPI |
| AI Orchestration | LangGraph |
| LLM | Anthropic Claude API  |
| Vector DB | pgvector (Postgres) |
| Frontend | Next.js |
| Containerisation | Docker + Docker Compose |
| Reverse Proxy | Nginx |


## Setup 

Frontend: /app
Backend: /backend

Context files: /context