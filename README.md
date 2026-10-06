# AI Legal Document Intelligence System (LegalIQ)

Upload a legal document — get an executive summary, structured key terms, a classified clause
library, page-cited Q&A chat, and clause-level comparison between two versions. Multi-user,
JWT-secured, and **fully local by default**: the AI runs on your own machine via Ollama, so
confidential contracts never leave it.

> New to the project? Read [TUTORIAL.md](TUTORIAL.md) — a beginner's guide to every technology
> used here, with analogies and a guided code tour.

## Features

| Feature | What you get |
|---|---|
| **Q&A chat (RAG)** | Streaming answers grounded in your document, each claim cited `[1] [2]` to a real page |
| **Executive summary** | Sectioned markdown summary; long documents handled by map-reduce |
| **Key terms** | Parties, dates, payment, termination, governing law — extracted to cards |
| **Clause library** | Clauses classified into ~20 legal types with page references |
| **Compare** | Clause-by-clause diff of two versions: unchanged / minor / moderate / major, added, removed, with change summaries |

## Architecture

```
React 19 + Vite + Tailwind (frontend/)
        │  JWT auth · SSE streaming
FastAPI backend (backend/app)
        ├── LLM provider layer ──┬─ Ollama (default: llama3.2:3b + nomic-embed-text)
        │                        └─ Z.ai GLM (OpenAI-compatible, config-switch)
        ├── PostgreSQL 16 + pgvector (Docker) — chunks w/ embeddings + full-text search,
        │   clauses, conversations; hybrid retrieval fused via Reciprocal Rank Fusion
        └── ./storage — uploaded files
```

Pipeline: upload → page-mapped extraction (PyMuPDF / python-docx) → structure-aware chunking
(legal headings, ~700-token windows, page ranges kept) → embeddings → hybrid retrieval (pgvector
cosine + Postgres FTS → RRF) → grounded, cited generation.

## Quick start (Windows / macOS / Linux)

**Windows one-click:** double-click [`start_demo.bat`](start_demo.bat) — it starts Docker,
the database, Ollama, both servers, warms the AI models into GPU memory (~2 h), verifies
health and opens the app. The manual steps below are the equivalent by hand.

Prerequisites: **Python 3.12+**, **Node 18+**, **Docker Desktop**, and
[Ollama](https://ollama.com) with two models pulled:

```bash
ollama pull llama3.2:3b       # chat model
ollama pull nomic-embed-text  # embedding model
```

```bash
# 1. Database
docker compose up -d

# 2. Configuration — no API key needed for local mode
cp .env.example .env             # defaults are ready for Ollama

# 3. Backend
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt        # Windows
# .venv/bin/pip install -r requirements.txt          # macOS/Linux
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m uvicorn app.main:app --port 8000

# 4. Frontend — second terminal, repo root
cd frontend && npm install && npm run dev
```

Open **http://localhost:5173**, register an account, and upload a contract.
[`testing documents/`](testing%20documents/) holds everything you need for manual
testing: **ten** realistic fictional agreements (offer letter, lease, MSA+SOW, SaaS
terms, loan, franchise, MOU, partnership deed, supply agreement, privacy policy) plus
**three long-form contracts of 30+ pages** (enterprise IT outsourcing, construction
works with a bill of quantities, term-loan facility with amortisation schedules) —
regeneratable via the `generate_*.py` scripts in that folder.

### Switching to hosted AI (optional)

Get a key at [z.ai](https://z.ai), then in `.env`:

```ini
LLM_PROVIDER=zai
ZAI_API_KEY=your-key
EMBEDDING_DIM=1024
```

Changing the embedding provider/dimension requires re-ingesting existing documents
(delete and re-upload, or `alembic downgrade base && alembic upgrade head` + re-upload).

## Configuration (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` or `zai` |
| `OLLAMA_LLM_MODEL` / `OLLAMA_EMBED_MODEL` | `llama3.2:3b` / `nomic-embed-text` | local models |
| `ZAI_API_KEY`, `ZAI_BASE_URL`, `ZAI_LLM_MODEL`, `ZAI_EMBED_MODEL` | — | hosted provider |
| `EMBEDDING_DIM` | `768` | must match the embedding model (768 nomic / 1024 Z.ai) |
| `DATABASE_URL` | dockerized Postgres on :5433 | |
| `RETRIEVAL_TOP_K`, `CHUNK_TOKENS`, `CHUNK_OVERLAP_TOKENS` | `6` / `700` / `100` | RAG tuning |
| `MAX_UPLOAD_MB` | `50` | upload cap |

## Tests

```bash
cd backend
.venv/Scripts/python -m pytest -q
```

28 tests run against an auto-created isolated `legal_ai_test` database with a deterministic
fake LLM — auth, JWT, chunking (pages + section paths), retrieval fusion, multi-user isolation,
and the full upload → chat → summary → key terms → clauses → compare pipeline.

## Project layout

```
backend/app   core/ models/ schemas/ api/ services/ (extraction, chunking, ingestion,
              retrieval, chat, summarization, key_terms, clauses, compare) + services/llm/
frontend/src  pages/ components/ lib/ stores/
samples/      two small demo contracts (v1 vs v2) for a quick Compare demo
testing documents/  ten realistic agreements for manual upload testing
docs/         milestone reports (not in the repo)
TUTORIAL.md   beginner's guide to the whole stack
```

## Roadmap

- Risk & red-flag analysis (one-sided / missing clause detection)
- OCR for scanned PDFs
- Celery/Redis job queue, S3-compatible storage
- Teams, document sharing, per-document permissions
