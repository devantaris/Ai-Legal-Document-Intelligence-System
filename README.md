# LegalIQ — Enterprise AI Legal Document Intelligence System

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/react-19-blue.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, sovereign legal intelligence workstation for corporate legal teams, in-house counsel, and transactional attorneys. **Local-first by default** via Ollama—ensuring confidential agreements never leave your private infrastructure—with seamless cloud provider failover.

Built with a disciplined, high-density light-mode interface compliant with corporate legal design standards ([TasteSkill](https://www.tasteskill.dev/docs#installation)), featuring an interactive 3D WebGL architectural hero scene, in-situ split-screen reading canvas, and deterministic citation guards.

---

## Capabilities & Feature Matrix

| Core Pillar | What You Get |
| :--- | :--- |
| **🛡️ Institutional Playbook Compliance** | Automated compliance evaluation against 10 corporate standards (Liability, Indemnity, Governing Law, IP, etc.). Grades clauses into **Red (High Risk)**, **Amber (Deviation)**, or **Green (Compliant)** with a 0–100% compliance score. |
| **⚡ 3-Tier Remediation Fallbacks** | Generates pre-approved fallback drafts for every flagged clause: **Conservative** (market standard), **Compromise** (balanced), and **Aggressive** (high leverage) with 1-click clipboard copy. |
| **📝 Native Word (.docx) Redlines** | 1-click export generating real Microsoft Word documents with **native Track Changes (`w:ins` / `w:del` XML tags)** and attorney review notes—ready to email directly to opposing counsel. |
| **📖 Dual-Pane Document Canvas** | Split-screen legal reading environment. Clicking any citation `[1]` in chat or any finding in Playbook automatically scrolls to the exact paragraph and highlights the passage with a warm legal-amber glow. |
| **🔍 Defined-Term Resolution Graph** | Automatically indexes capitalized defined terms. Terms receive dotted underlines; hovering displays an instant tooltip popover with the official contractual definition and global occurrence count. |
| **📂 Contract Vault Due Diligence Grid** | Cross-repository intelligence table extracting structured metadata (Parties, Effective Date, Governing Law, Payment Terms, Liability Caps) across all contracts with 1-click **CSV Due Diligence Export**. |
| **🌐 Cross-Repository Legal AI Query** | Multi-document RAG query engine allowing cross-examination across 50+ contracts simultaneously, contrasting conflicting provisions with multi-contract citations. |
| **✅ Zero-Hallucination Entailment Guard** | Mathematical Natural Language Inference (NLI) claim verification. Evaluates generated answers sentence-by-sentence against cited text snippets, awarding an audited "100% Citation Grounded" certificate. |
| **💬 Citation-Backed Q&A (RAG)** | Low-latency streaming chat grounded in contract text using Reciprocal Rank Fusion ($k=60$) combining dense vector embeddings (`bge-m3` / `nomic`) with PostgreSQL BM25 keyword matching. |
| **📊 Hierarchical Map-Reduce Summary** | Analyzes 30+ page contracts without truncation via parallel map-reduce summarization detailing Parties, Purpose, Obligations, Liabilities, and Expirations. |
| **⚖️ Version Comparison & Diff** | Clause-by-clause semantic diff aligning provisions across contract revisions (added, removed, modified, unchanged) with severity assessments. |

---

## Empirical Benchmark Performance (LegalBench-RAG)

LegalIQ was evaluated against the Stanford **LegalBench-RAG** legal retrieval benchmark. Our local hybrid retrieval engine consistently outperforms standard commercial hosted dense-only baselines:

| Metric | Hosted OpenAI Baseline | LegalIQ Sovereign Hybrid (`bge-m3` + BM25 RRF) | Net Gain |
| :--- | :---: | :---: | :---: |
| **Recall@1** | 8.5% | **14.4%** | **+69.4%** |
| **Recall@8** | 31.9% | **46.2%** | **+44.8%** |
| **Recall@64** | 63.5% | **71.9%** | **+13.2%** |
| **MRR (Mean Reciprocal Rank)** | 0.218 | **0.284** | **+30.3%** |

*Evaluation harness and methodology documented in [`docs/eval/m1-legalbenchrag-retrieval.md`](docs/eval/m1-legalbenchrag-retrieval.md).*

---

## Architecture Overview

```
Frontend (frontend/)
├── React 19 + TypeScript + Vite + Tailwind CSS
├── TasteSkill Light-Mode Canvas (#f8f8f7) & Typography
├── Three.js / WebGL 3D Architectural Balance Scene (@react-three/fiber)
├── Split-Screen Legal Document Reader & Definition Tooltips
└── Global Command Palette (⌘K / Ctrl+K)

Backend API (backend/app/)
├── FastAPI REST & SSE Streaming Endpoints
├── Playbook Compliance & Risk Engine (backend/app/services/playbook.py)
├── Native Word Track Changes (.docx) Generator (backend/app/services/docx_export.py)
├── Defined-Term Graph & Reference Indexer (backend/app/services/defined_terms.py)
├── Portfolio & Cross-Contract Intelligence (backend/app/services/portfolio.py)
├── Sentence-Level Citation Entailment Guard (backend/app/services/entailment.py)
├── Hybrid RRF Retrieval Coordinator (BM25 + pgvector cosine, k=60)
└── Dual-Provider LLM Abstraction (Ollama local / Z.ai hosted)

Database & Storage
├── PostgreSQL 16 + pgvector (Docker on port 5433)
│   ├── HNSW Index on Dense Embeddings (Vector Cosine Ops)
│   ├── tsvector GIN Index on Document Chunks (FTS BM25)
│   └── Alembic Database Schema Migrations
└── Local Encrypted Document Storage (/storage/<user_id>/<doc_id>/)
```

---

## Quick Start (Windows / macOS / Linux)

### Option A: Windows One-Click Demo
Double-click [`start_demo.bat`](start_demo.bat) — it automatically starts Docker, initializes the PostgreSQL container, warms Ollama models into memory, runs migrations, boots the backend and frontend, and launches your browser.

---

### Option B: Manual Setup

#### 1. Prerequisites
- **Python 3.12+**
- **Node.js 18+** & **npm**
- **Docker Desktop** (running)
- **[Ollama](https://ollama.com)** (for local sovereign inference):
  ```bash
  ollama pull llama3.2:3b       # or llama3.1:8b
  ollama pull nomic-embed-text  # or bge-m3
  ```

#### 2. Start Database
```bash
docker compose up -d
```
*(Starts PostgreSQL 16 with `pgvector` on `localhost:5433`)*

#### 3. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. Frontend Setup
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

#### Demo Credentials
* **Email:** `demo@legaliq.ai`
* **Password:** `DemoPassword123!`
*(Or click "Fill Demo Credentials" on the login screen).*

---

## Deep Dive: Enterprise Modules

### 1. Institutional Playbook Review & Remediation
Corporate legal departments evaluate incoming agreements against strict risk parameters. LegalIQ audits clauses across 10 substantive categories:
- **Limitation of Liability:** Checks for mutual caps (12 months fees), indirect damage waivers, and narrow carve-outs.
- **Indemnification:** Ensures mutual third-party defense, IP indemnity from vendors, and defense control rights.
- **Governing Law & Venue:** Recommends recognized commercial courts (Delaware, New York, England & Wales) and flags hostile jurisdictions.
- **Confidentiality:** Enforces 3–5 year terms, perpetual trade secret protection, and mandatory standard exceptions.
- **Termination & Remedies:** Flags missing termination for convenience and unreasonable cure windows.

For every violation, LegalIQ supplies **Conservative**, **Compromise**, and **Aggressive** fallback drafts ready to paste into counter-proposals.

### 2. Native Word (.docx) Redlines with Track Changes
Lawyers negotiate by emailing `.docx` files back and forth. Rather than trapping edits in a web UI, LegalIQ's export engine generates a clean Microsoft Word file with:
- Formal Audit Executive Summary table.
- Original clauses marked for removal formatted as native Word tracked deletions (`<w:del>`).
- Pre-approved fallback clauses formatted as native Word tracked insertions (`<w:ins>`).
- Attorney margin notes attached to every modified section.

Opposing counsel opens the document directly in Microsoft Word with **Review > Track Changes** active.

### 3. Split-Screen Document Canvas & Synchronized Highlighting
Toggling **Split Canvas** opens a dual-pane legal workstation:
- **Left Pane:** Formatted contract reader displaying original document text, page numbers, and section headers.
- **Right Pane:** Analysis tabs (Summary, Key Terms, Clauses, Playbook Review, Chat).
- **Synchronized Focus:** Clicking any citation pill `[1]` in chat or clicking "Inspect in Canvas" on any Playbook finding automatically scrolls the reader to that exact paragraph and illuminates it with an amber highlight.

### 4. Interactive Defined-Term Resolution
Defined terms often hide substantial legal obligations. LegalIQ parses definitions across both dedicated definition sections and inline parenthetical quotes. Defined terms receive subtle dotted underlines in the document canvas; hovering displays a popover with:
- Canonical contractual definition text.
- Section and page where the term is defined.
- Total count of how many times the term is invoked across the contract.

### 5. Contract Vault & Portfolio Due Diligence
When conducting M&A due diligence or vendor audits, analyzing individual files is insufficient. LegalIQ's **Contract Vault** (`/portfolio`):
- Aggregates all uploaded agreements into an interactive spreadsheet grid.
- Extracts Parties, Effective Date, Governing Law, Payment Terms, and Liability Caps into sortable columns.
- Provides a 1-click **Export Due Diligence (CSV)** button.
- Enables cross-contract AI queries (e.g. *"Compare payment terms and liability caps across all vendor contracts"*), returning multi-document cited responses.

### 6. Zero-Hallucination Entailment Guard
Legal AI cannot afford hallucinations. Under every assistant response, clicking **Audit Entailment** executes sentence-by-sentence Natural Language Inference (NLI) claim verification:
- Verifies lexical containment, named entities, and numeric claims against cited text.
- Disallows altered figures (e.g., claiming "$5,000,000" if the source says "$500,000").
- Issues an Entailment Certificate confirming whether the answer is **100% Citation Grounded**.

---

## Configuration (`.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://legal_ai:legal_ai_dev@localhost:5433/legal_ai` | PostgreSQL connection string |
| `LLM_PROVIDER` | `ollama` | Provider: `ollama` (local) or `zai` (cloud fallback) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama daemon endpoint |
| `OLLAMA_LLM_MODEL` | `llama3.2:3b` | Local generation model (`llama3.1:8b`, `mistral`, etc.) |
| `OLLAMA_EMBED_MODEL`| `nomic-embed-text` | Local embedding model (`bge-m3`, `nomic-embed-text`) |
| `EMBEDDING_DIM` | `768` | Dimension: `768` for nomic, `1024` for bge-m3 / Z.ai |
| `ZAI_API_KEY` | — | API key for Z.ai hosted inference |
| `ZAI_LLM_MODEL` | `glm-4-flash` | Z.ai chat model |
| `RETRIEVAL_TOP_K` | `6` | Chunks retrieved per query |
| `MAX_UPLOAD_MB` | `50` | Maximum upload file size in megabytes |

---

## Testing & Quality Assurance

The test suite runs against an isolated SQLite/in-memory or test PostgreSQL instance with deterministic mock providers:

```bash
cd backend
.venv\Scripts\pytest backend\tests -v -k "not integration and not client"
```

**Results:** **37 unit tests passing in 0.41s**:
* `tests/test_playbook.py`: Risk grading, heuristic evaluation, fallback generation (3 passed)
* `tests/test_docx_export.py`: OpenXML `<w:ins>` / `<w:del>` tracked changes generation (2 passed)
* `tests/test_defined_terms.py`: Definition extraction, regex resolution, frequency indexing (1 passed)
* `tests/test_entailment.py`: Sentence parsing, containment audit, numeric verification (2 passed)
* `tests/test_chunking.py`: Legal heading hierarchy, token boundaries, page retention (5 passed)
* `tests/test_security.py`: Argon2 password hashing, JWT token expiry, tenant isolation (5 passed)
* `tests/test_providers.py`: JSON extraction, retry logic, provider failovers (8 passed)
* `tests/test_eval_scoring.py`: LegalBench-RAG evaluation scoring, MRR, Recall@K (11 passed)

Frontend verification:
```bash
cd frontend
npm run build
```
**Results:** **0 TypeScript errors, 0 compilation warnings.**

---

## Test Documents Included

The [`testing documents/`](testing%20documents/) directory contains 10 realistic sample agreements for immediate testing:
* Commercial Lease Agreement
* Employment Agreement / Offer Letter
* Master Services Agreement (MSA) + SOW
* SaaS Terms of Service
* Loan & Security Agreement
* Franchise Agreement
* Memorandum of Understanding (MOU)
* General Partnership Deed
* Manufacturing & Supply Agreement
* Corporate Privacy Policy

Plus **three 30+ page contracts** for stress-testing map-reduce summarization (Enterprise IT Outsourcing, Commercial Construction Works, and Multi-Tranche Term-Loan Facility).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
