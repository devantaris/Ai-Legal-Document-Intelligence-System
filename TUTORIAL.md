# LegalIQ from Zero — A Beginner's Guide to the Project

This guide explains the **AI Legal Document Intelligence System (LegalIQ)** to someone who has
never seen it before. No prior knowledge of web apps, databases, or AI is assumed — everything
is explained from scratch with analogies. Read it top to bottom and you'll understand not just
*what* the project does, but *why* every piece exists.

---

## 1. What does this project actually do?

Imagine you hand a lawyer a 20-page contract and ask:

- "Summarise this for me."
- "When does it terminate?"
- "Who pays whom, and by when?"
- "Compare it with last year's version — what changed?"

That's hours of careful reading. **LegalIQ does this in under a minute.** You upload a contract
(PDF, DOCX, or TXT) to a website, and it gives you:

1. **An executive summary** — structured, sectioned, readable.
2. **Key terms** — parties, dates, payment, termination, governing law, extracted into cards.
3. **A clause library** — every clause classified by type (termination, confidentiality, …).
4. **A chat box** — ask questions in plain English; answers come **with page citations**, so you
   can verify every claim against the actual document.
5. **A comparison view** — upload two versions of the same contract and see clause-by-clause
   what changed, how serious each change is, and who benefits.

And the important privacy trick: **all the AI runs on your own computer.** Confidential contracts
never leave your machine.

---

## 2. The big picture — a restaurant analogy

Every web application has three parts, and LegalIQ is no different:

```
   YOU (browser)          THE RESTAURANT (server)         THE STORE ROOM (database)
  ┌───────────────┐       ┌──────────────────────┐        ┌──────────────────┐
  │  React app    │──ask──▶  FastAPI (the waiter) │──fetch─▶ PostgreSQL        │
  │  (the menu &  │◀─food─│  kitchen = Python     │        │ (ingredients,    │
  │  the tables)  │       │  services)            │        │  every record)   │
  └───────────────┘       └──────────┬───────────┘        └──────────────────┘
                                     │ asks an expert when needed
                                     ▼
                          ┌──────────────────────┐
                          │  Ollama + LLM        │
                          │  (the AI consultant) │
                          └──────────────────────┘
```

- **Frontend** (React): what you see and click in the browser.
- **Backend** (FastAPI, written in Python): the brain. It receives requests, does the real
  work, and talks to the database and the AI.
- **Database** (PostgreSQL): where every user, document, and analysis result is stored
  permanently.
- **AI models** (via Ollama): the "language expert" the backend consults for summarising,
  classifying, and answering.

---

## 3. The technologies, one by one

### 3.1 Python — the backend language

Python is the programming language of the backend. It's readable, has the best AI ecosystem in
the world, and is the standard for this kind of project. All backend code lives in `backend/app/`.

### 3.2 FastAPI — the framework

A **web framework** is a toolkit that handles the boring parts of running a server (reading
requests, sending responses, validating input). FastAPI is a modern Python framework. When the
frontend asks `GET /api/documents`, a FastAPI *route* function runs and returns the data.

Look at `backend/app/api/documents.py`:

```python
@router.get("", response_model=list[DocumentOut])
def list_documents(user=Depends(get_current_user), db=Depends(get_db)):
    ...
```

That decorator (`@router.get`) says: "when someone GETs this URL, run this function." FastAPI
also auto-generates interactive API docs — visit `http://localhost:8000/docs` while the server
runs and you can click every endpoint.

**uvicorn** is the program that actually runs the FastAPI app on port 8000 (FastAPI is the app,
uvicorn is the engine).

### 3.3 REST APIs — how the parts talk

An **API endpoint** is simply a URL the frontend can call, like:

| Method | URL | Meaning |
|---|---|---|
| POST | `/api/auth/register` | create an account |
| POST | `/api/documents` | upload a file |
| GET | `/api/documents/{id}/summary` | get the summary |
| POST | `/api/documents/{id}/chat` | ask a question |

### 3.4 Authentication — JWT and Argon2

- **Argon2** stores passwords safely. We never save the password itself — we save a
  one-way "hash" (think: blended smoothie; you can't un-blend it). When you log in, we blend
  what you typed and compare.
- **JWT (JSON Web Token)** is your session pass. After login the backend hands you a signed
  token; the frontend attaches it to every request like a wristband at an event. The backend
  verifies the signature — no server-side session storage needed.
- **Per-user isolation**: every database query for documents filters by owner, so one account
  can never see another's contracts (there's literally an automated test for this).

### 3.5 PostgreSQL + Docker — the database

- **PostgreSQL** is a battle-tested open-source relational database — tables of rows with
  strict types, queried in SQL.
- **Docker** runs it in a *container*: a pre-packaged, isolated environment, so you don't
  install Postgres manually. `docker-compose.yml` says "give me a Postgres with the vector
  extension, on port 5433." One command (`docker compose up -d`) and it exists.

### 3.6 pgvector + embeddings — how a computer understands meaning

Here's the core AI trick. An **embedding** turns a piece of text into a list of numbers — a
point in a 768-dimensional space — where *texts with similar meanings land close together*.
"The client must pay within 30 days" and "payment is due in one month" end up as neighbours,
even though they share almost no words.

- **pgvector** is a Postgres extension that stores these vectors and searches "which stored
  vectors are closest to this query vector?" — that's **semantic search**.
- The vectors come from an embedding model: **nomic-embed-text** (local, free) or Z.ai's
  **embedding-3** (hosted).

### 3.7 Full-text search + RRF — the other half of retrieval

Vectors are fuzzy; sometimes you need exact matching ("section 8.2", a defined term like
"Effective Date"). So LegalIQ searches **two ways at once**:

1. **Dense search** — pgvector cosine similarity (meaning).
2. **Sparse search** — PostgreSQL full-text search, a built-in keyword engine (exact words).

Then it merges the two rankings with **Reciprocal Rank Fusion**: each result gets points for
its rank in each list, `score = 1/(60 + rank)`, summed. Results both engines agree on float to
the top. This hybrid is measurably better than either alone on legal text.

### 3.8 Chunking — preparing documents for search

An LLM can't swallow a 200-page contract at once, and searching a whole document is too coarse.
So ingestion **chunks** it: the code in `backend/app/services/chunking.py` recognises legal
structure (`ARTICLE 7`, `8.2 Late payment`, ALL-CAPS headings), builds a section path like
`ARTICLE 2 - FEES AND PAYMENT > 2.2 Late payment`, and packs sections into ~700-token chunks
with a little overlap so nothing is cut mid-thought. Each chunk remembers its **page numbers** —
that's how citations can point at "p. 4".

### 3.9 LLMs, Ollama, and the provider layer

An **LLM** (Large Language Model) is a neural network trained on enormous text corpora that
predicts and generates text. LegalIQ uses two interchangeable sources:

- **Ollama** (default): runs open-weight models **on your machine** — `llama3.2:3b` for
  writing, `nomic-embed-text` for embeddings. Free, private, works offline.
- **Z.ai GLM** (optional): a hosted, stronger model, used by changing two lines in `.env`.

The magic is `backend/app/services/llm/`: every feature talks to an *interface*
(`chat()`, `stream_chat()`, `embed()`), never to a specific company's API. Swapping providers
is configuration, not code. This is called the **provider abstraction pattern** — one of the
best design decisions in the project.

### 3.10 RAG — Retrieval-Augmented Generation

LLMs have two famous problems: they **hallucinate** (confidently invent facts) and their
training data doesn't include *your* contract. **RAG** solves both:

> Before answering, **retrieve** the most relevant chunks of the actual document and hand them
> to the model with the instruction: *"answer ONLY from these passages and cite them as [1], [2]."*

Think of it as an **open-book exam** instead of memory quiz. The model's answer is grounded in
retrieved text, and each citation `[1]` maps to a real chunk with a real page number. The chat
flow in `backend/app/services/chat.py` does: embed the question → hybrid retrieval → build the
prompt → stream the answer.

### 3.11 SSE — streaming answers

You've watched ChatGPT type its answer word by word. LegalIQ does the same with **Server-Sent
Events**: the backend pushes small text deltas over one long HTTP connection, and the React chat
panel appends them live. Look for `StreamingResponse` in `api/chat.py` and the `streamSSE`
reader in `frontend/src/lib/api.ts`.

### 3.12 Structured extraction — taming the model's output

For key terms and clause classification, we need **JSON**, not prose. The pattern
(`ask_json` in `services/llm/__init__.py`): instruct the model to reply with only JSON matching
a schema, **validate with Pydantic** (a data-validation library), and if it's malformed, ask the
model to fix it and retry. The schema itself is forgiving — if a weak model returns a nested
object where a string was expected, the code coerces it instead of crashing. Rule of thumb:
*never trust model output; validate everything.*

### 3.13 React + Vite + TypeScript + Tailwind — the frontend

- **React** builds UI from small reusable **components** (e.g., `ChatPanel`, `ClausesPanel`).
- **TypeScript** is JavaScript with types — errors are caught before the code runs.
- **Vite** is the dev server/bundler: instant reload while developing.
- **Tailwind CSS** styles via small utility classes directly in the markup
  (`className="rounded-xl border bg-white p-4"`).
- **zustand** is a tiny state store (it remembers who's logged in).

All frontend code is in `frontend/src/`, with `pages/` (full screens), `components/` (reusable
pieces), and `lib/api.ts` (the single module that talks to the backend).

### 3.14 SQLAlchemy + Alembic — the database from Python

- **SQLAlchemy** lets you write Python classes (`class Document(...)`) that map to database
  tables — no raw SQL for everyday work. See `backend/app/models/`.
- **Alembic** records schema changes as **migrations** (versioned scripts), so the database can
  be recreated identically anywhere: `alembic upgrade head`.

### 3.15 Testing — pytest

`backend/tests/` contains 28 automated tests. Two clever tricks worth learning from:

1. **Isolated test database** — tests auto-create a separate `legal_ai_test` database, so your
   real data is never touched.
2. **FakeProvider** — a deterministic fake LLM (`tests/fakes.py`) replaces the real model in
   tests, so tests are fast, free, and never flaky. The full pipeline (upload → chat → compare)
   is tested end-to-end without any AI API call.

### 3.16 Git & GitHub — versions of the code

Every change is a **commit** (a labelled snapshot); GitHub hosts them. This repo has ~50 atomic
commits, each a small logical step — reading the history is itself a lesson in how software is
built incrementally.

---

## 4. Follow a document through the system

**Upload day:**

1. You drag `contract.pdf` onto the dashboard → `POST /api/documents` saves it under
   `storage/{user_id}/{doc_id}/` and schedules a background job.
2. The job extracts text page by page (PyMuPDF for PDFs), detects the legal headings, chunks the
   sections, embeds each chunk, and stores everything in Postgres. The card's badge goes
   `Queued → Parsing → Indexing → Ready`.

**Question time:**

3. You type *"What is the notice period?"* → `POST /api/documents/{id}/chat`.
4. The backend embeds your question, retrieves the top 6 chunks (hybrid search + RRF), builds a
   prompt: *system rules + [1]…[6] passages + your question*, and streams the model's answer
   back over SSE with citations.
5. Both messages are saved, so your conversation is still there tomorrow.

**Comparison day:**

6. You pick two versions → the backend matches their clauses by embedding similarity (+ a bonus
   for same clause type), then uses a *text diff* to decide which pairs truly changed; changed
   pairs go to the LLM, which returns a change level (minor/moderate/major) and a one-line
   summary. The UI shows everything side by side.

---

## 5. Guided tour of the code

```
backend/app/
  main.py            app entry: FastAPI app, CORS, health check
  core/              config (.env), database engine, JWT/argon2, auth guards
  models/            SQLAlchemy tables: User, Document, Chunk, Clause, Message...
  schemas/           request/response shapes (Pydantic)
  api/               the URL routes: auth, documents, chat, analysis, compare
  services/          the real work:
    extraction.py      PDF/DOCX/TXT → page-mapped text
    chunking.py        headings → sections → overlapping chunks
    ingestion.py       orchestrates the pipeline (runs in background)
    retrieval.py       hybrid search + RRF fusion
    chat.py            RAG prompt + SSE streaming
    summarization.py   map-reduce summary
    key_terms.py       schema-validated extraction
    clauses.py         clause classification
    compare.py         clause matching + change verdicts
    llm/               the provider layer: base, zai.py, ollama.py
frontend/src/
  pages/             AuthPage, Dashboard, DocumentPage, Compare, Settings
  components/        ChatPanel, SummaryPanel, KeyTermsPanel, ClausesPanel...
  lib/api.ts         one module for every backend call (incl. SSE reader)
  stores/auth.ts     login state (zustand)
samples/             generated demo contracts + the script that makes them
docker-compose.yml   the PostgreSQL database in one command
.env                 configuration — provider, models, ports, secrets (never committed)
```

---

## 6. Run it yourself (5 minutes)

Prerequisites: Python 3.12+, Node 18+, Docker Desktop. Full details in the README; the short
version:

```bash
docker compose up -d                          # database
cd backend
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m alembic upgrade head  # create tables
.venv/Scripts/python -m uvicorn app.main:app --port 8000
# second terminal:
cd frontend && npm install && npm run dev     # http://localhost:5173
```

---

## 7. If you want to *learn* this stack — a path

1. **Week 1 — Python + FastAPI**: do the official FastAPI tutorial; then read
   `backend/app/api/auth.py` (the smallest router) and trace one endpoint end to end.
2. **Week 2 — SQL + PostgreSQL**: learn basic SELECT/JOIN; then read `backend/app/models/`.
3. **Week 3 — React + TypeScript**: react.dev's tutorial; then read `frontend/src/pages/AuthPage.tsx`.
4. **Week 4 — the AI part**: read about embeddings, then this project's
   `chunking.py` → `retrieval.py` → `chat.py`, in that order. That trio *is* the project's brain.
5. **Exercise ideas**: add a "download summary as PDF" button; add a new clause type; add
   token-per-second display to the chat; write one pytest case for the chunker.

## 8. Glossary

| Term | Plain meaning |
|---|---|
| API | the menu of requests a server accepts |
| Embedding | text converted to a number-vector; similar meanings = nearby vectors |
| Token | ~4 characters of text; models read and bill in tokens |
| RAG | open-book answering: retrieve passages first, then generate |
| RRF | a formula for merging two search rankings fairly |
| Migration | a versioned script that changes the database schema |
| SSE | a one-way stream from server to browser (used for typing effects) |
| Container | an isolated pre-packaged program environment (Docker) |
| Hash | one-way scrambled password representation |
| LLM | the text-generating AI model |
