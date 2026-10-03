# AI Legal Document Intelligence System (LegalIQ)

A multi-user web application that ingests legal documents (contracts, NDAs,
service agreements) and provides:

- **Document Q&A chat** — RAG over your documents with streaming answers and
  page-level citations
- **Summaries & key terms** — executive summary plus structured extraction
  (parties, dates, payment, termination, governing law, …)
- **Clause library** — LLM-classified clauses with types and page references
- **Document comparison** — clause-level diff between two versions with
  change summaries

## Architecture

```
React 19 + Vite + Tailwind (frontend/)
        │  JWT auth, SSE streaming
FastAPI (backend/app)
        │                          ┌─ Z.ai GLM (default, OpenAI-compatible)
        ├─ LLM provider layer ─────┤
        │                          └─ Ollama (local, config-switchable)
        ├─ PostgreSQL + pgvector (docker-compose) — chunks, embeddings,
        │   full-text search, clauses, conversations
        └─ local ./storage/ — uploaded files
```

Pipeline: upload → text extraction with page mapping (PyMuPDF / python-docx)
→ structure-aware chunking (legal headings, ~700-token windows with overlap)
→ embeddings (pluggable provider) → hybrid retrieval (pgvector cosine +
Postgres full-text search fused with Reciprocal Rank Fusion) → answer /
analysis with citations.

## Quick start

Prerequisites: **Python 3.12+**, **Node 18+**, **Docker Desktop**.

```bash
# 1. Database (PostgreSQL + pgvector)
docker compose up -d

# 2. Configure — edit .env and set ZAI_API_KEY (get one at https://z.ai)
cp .env.example .env

# 3. Backend
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt      # Windows
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m uvicorn app.main:app --port 8000 --reload

# 4. Frontend (second terminal, from the repo root)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — register an account, upload a contract from
`samples/`, and the document page will offer Summary / Key Terms / Clauses /
Chat tabs once ingestion finishes (a few seconds after the status badge turns
**Ready**). Use `Services_Agreement_v1.pdf` and `_v2.pdf` to try Compare.

### Using local models (Ollama) instead of Z.ai

```bash
ollama pull llama3.1          # chat model
ollama pull nomic-embed-text  # embedding model
```

then in `.env` set `LLM_PROVIDER=ollama` and `EMBEDDING_DIM=768`.
Note: changing the embedding provider/dimension requires re-ingesting any
already-processed documents (delete and re-upload).

## Configuration (`.env`)

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | `zai` (default) or `ollama` |
| `ZAI_API_KEY` | API key for Z.ai (required for the default provider) |
| `ZAI_LLM_MODEL` / `ZAI_EMBED_MODEL` | model names (defaults `glm-4.6`, `embedding-3`) |
| `OLLAMA_LLM_MODEL` / `OLLAMA_EMBED_MODEL` | local model names |
| `EMBEDDING_DIM` | must match the embedding model (1024 for Z.ai, 768 for nomic-embed-text) |
| `DATABASE_URL` | points at the dockerized Postgres |
| `RETRIEVAL_TOP_K`, `CHUNK_TOKENS`, `CHUNK_OVERLAP_TOKENS` | RAG tuning |

## Tests

Runs against a dedicated `legal_ai_test` database (created automatically on
the same Postgres server — dev data is untouched). Requires the dockerized
database (`docker compose up -d`):

```bash
cd backend
.venv\Scripts\python -m pytest -q
```

28 tests cover auth, JWT handling, the chunker (page mapping, section paths,
overlap), JSON extraction, provider behavior (mocked), hybrid retrieval with
RRF, multi-user scoping, and a full API pipeline smoke test
(upload → chat → summary → key terms → clauses → compare) using a fake LLM.

## Regenerating sample contracts

```bash
backend/.venv/Scripts/python samples/generate_samples.py
```

## Project layout

```
backend/app
  core/       config, database, security (JWT + argon2), dependencies
  models/     SQLAlchemy models (users, documents, chunks, clauses, chats)
  schemas/    Pydantic request/response models
  api/        routers: auth, documents, chat, analysis, compare
  services/   extraction, chunking, ingestion, retrieval, chat, summarization,
              key_terms, clauses, compare
  services/llm/  provider layer: base + zai + ollama
  workers/    background task entry points
frontend/src  pages, components, lib (API client + SSE), stores
samples/      generated sample contracts + generator script
```

## Roadmap (not in v1)

- Risk & red-flag analysis (one-sided clause detection, missing-clause warnings)
- OCR for scanned PDFs
- Celery/Redis job queue for large-scale ingestion
- S3-compatible object storage
- Teams / document sharing
