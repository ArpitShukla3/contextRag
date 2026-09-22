# Contextual RAG — Backend

Production-oriented FastAPI backend for a Contextual Retrieval RAG application.
Implemented incrementally; this document covers **Phase 1** (foundation) and
**Phase 2** (document ingestion).

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2.x (psycopg 3 driver)
- PostgreSQL + pgvector
- Pydantic / Pydantic Settings
- Alembic
- pytest
- PyMuPDF, python-docx

## Project structure

```
backend/
├── app/
│   ├── main.py                # FastAPI app factory + entrypoint
│   ├── deps.py                # Dependency wiring (storage, parsers, services)
│   ├── api/
│   │   └── routes/
│   │       ├── health.py      # GET /api/health
│   │       └── documents.py   # Document upload/query/delete/chunks
│   ├── core/
│   │   ├── config.py          # Environment-driven settings
│   │   └── logging.py         # Structured logging setup
│   ├── db/
│   │   ├── base.py            # DeclarativeBase
│   │   ├── session.py         # Engine, SessionLocal, get_db dependency
│   │   └── models/
│   │       ├── document.py    # Document entity
│   │       └── chunk.py       # Chunk entity (pgvector embedding column)
│   ├── schemas/               # Typed request/response models
│   ├── services/
│   │   ├── parsing/           # DocumentParser abstraction + PDF/TXT/DOCX/MD
│   │   ├── chunking/          # Token-aware chunker
│   │   ├── storage/           # Storage abstraction + local disk backend
│   │   ├── validation.py      # FileValidator
│   │   ├── ingestion.py       # Ingest pipeline orchestrator
│   │   └── documents.py       # Document query/delete service
│   ├── repositories/          # Document + Chunk data access
│   └── exceptions/            # AppError hierarchy + handlers
├── tests/                     # Unit + integration (test-database) tests
├── alembic/                   # Migrations
├── requirements.txt           # Runtime deps (pinned)
├── requirements-dev.txt       # Test deps (pinned)
├── docker-compose.yml         # Local PostgreSQL + pgvector
├── alembic.ini
├── pytest.ini
└── .env.example
```

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env   # then fill in real values (never commit .env)
```

### 1. Run PostgreSQL

The project expects a PostgreSQL instance with the `vector` extension available.
The simplest option is the provided Docker Compose file:

```bash
docker compose up -d db
```

This starts `pgvector/pgvector:pg16` listening on `localhost:5432` with
`contextual_rag` database, user `rag`, password `rag` — matching the default in
`.env.example`. Point `DATABASE_URL` at any other instance (hosted, Neon, etc.)
as needed; a plain `postgres://`/`postgresql://` URL without a driver token is
normalized to the psycopg 3 driver automatically.

### 2. Run migrations

```bash
alembic upgrade head
```

The initial migration enables the `vector` extension and creates the
`documents` and `chunks` tables. Review online/offline with:

```bash
alembic current      # show applied revisions
alembic history      # show migration chain
alembic downgrade base   # revert everything
```

### 3. Start FastAPI

```bash
uvicorn app.main:app --reload
```

Interactive API docs at `http://127.0.0.1:8000/docs`.

Health check:

```bash
curl http://127.0.0.1:8000/api/health
# {"status":"ok"}
```

### 4. Run tests

Unit tests (parsers, chunker, validation, startup, health) run without a
database. Integration tests for the document API hit a **dedicated test
database** (`TEST_DATABASE_URL`, e.g. a local Postgres); they auto-skip if it
is unreachable.

```bash
# create the local test database on the dockerized Postgres
docker compose exec db createdb -U rag contextual_rag_test

pytest
```

### 5. Ingest documents

Upload a file — the pipeline validates it, runs the matching parser, chunks
the text, and stores the chunks:

```bash
curl -X POST http://127.0.0.1:8000/api/documents \
  -F "file=@report.pdf;type=application/pdf"

curl http://127.0.0.1:8000/api/documents                          # list
curl http://127.0.0.1:8000/api/documents/1                        # detail
curl http://127.0.0.1:8000/api/documents/1/chunks                 # chunks
curl -X DELETE http://127.0.0.1:8000/api/documents/1              # delete
```

## Ingestion pipeline

```
Upload (POST /api/documents)
   │
   ▼
File validation      (extension, size, empty file — FileValidator)
   │
   ▼
Parser dispatch      (suffix/MIME -> DocumentParser: PDF/TXT/DOCX/MD)
   │
   ▼
Normalized text      (ParsedDocument: pages with page numbers where available)
   │
   ▼
Token-aware chunking (TokenChunker: CHUNK_SIZE / CHUNK_OVERLAP)
   │
   ▼
Database             (Document + Chunk rows; file persisted to UPLOAD_DIR)
```

- Documents transition through `uploaded → processing → processed`; failed
  documents are marked `failed` and the client receives a useful `4xx` error.
- `GET /api/documents/{id}/chunks` returns chunks with
  `metadata.source` (original filename) and `metadata.page_number` where the
  format provides pages (PDF).
- Extending formats = add a `DocumentParser` subclass and register it in
  `create_parser_registry()`.

## Configuration

All configuration is environment-driven via `app/core/config.py`
(a `pydantic-settings` `BaseSettings`, loaded from `.env`).

| Variable             | Description                                              | Default                                     |
| -------------------- | -------------------------------------------------------- | ------------------------------------------- |
| `DATABASE_URL`       | SQLAlchemy connection string                             | `postgresql+psycopg://rag:rag@localhost:5432/contextual_rag` |
| `CHUNK_SIZE`         | Max tokens per chunk                                     | `1000`                                      |
| `CHUNK_OVERLAP`      | Overlapping tokens between consecutive chunks (`< CHUNK_SIZE`) | `200`                                  |
| `UPLOAD_DIR`         | Local directory for uploaded files                       | `data/uploads`                              |
| `MAX_UPLOAD_SIZE_MB` | Maximum accepted upload size                             | `20`                                        |
| `TEST_DATABASE_URL`  | Dedicated database used by the integration tests         | `postgresql+psycopg://rag:rag@localhost:5432/contextual_rag_test` |
| `OPENROUTER_API_KEY` | OpenRouter key (used from Phase 3)                       | *(empty)*                                   |
| `OPENROUTER_MODEL`   | Default model id                                          | `anthropic/claude-sonnet-4-20250514`        |
| `EMBEDDING_MODEL`    | Sentence-transformer model id (used from Phase 3)        | `sentence-transformers/all-MiniLM-L6-v2`    |
| `EMBEDDING_DIM`      | Vector dimensionality; must match `EMBEDDING_MODEL`      | `384`                                       |
| `ENVIRONMENT`        | `development` / `production`                              | `development`                               |
| `DEBUG`              | Enable debug mode                                         | `false`                                     |
| `LOG_LEVEL`          | Root logger level                                         | `INFO`                                      |

## Architecture decisions (Phase 1)

- **App factory**: `create_app()` builds the application; tests import it
  directly (no global-state coupling). A module-level `app` instance is
  provided for uvicorn.
- **Centralized settings**: one `Settings` class; no hardcoded secrets, no
  scattered `os.getenv`. URLs such as `postgres://`/`postgresql://` (without a
  driver token) are normalized to `postgresql+psycopg://` so hosted databases
  work out of the box.
- **Dependency injection for DB sessions**: `get_db()` is the FastAPI
  dependency; services/repos (Phase 2+) will receive sessions explicitly.
- **Separation of concerns**: route handlers contain no business logic — the
  health route only reads/writes schemas. `services/` and `repositories/`
  packages exist as seams for later phases.
- **pgvector embeddings**: the `Chunk.embedding` column uses
  `pgvector.sqlalchemy.Vector(EMBEDDING_DIM)`. Dimensionality is config-driven
  and must match the embedding model. `metadata` is a JSONB column; the Python
  attribute is `metadata_` because `metadata` is reserved by SQLAlchemy's
  Declarative API.
- **Typed entities**: `DocumentStatus` is a `str`-based enum; `Document` and
  `Chunk` use SQLAlchemy 2.0 `Mapped`/`mapped_column` typed declarations.
- **Exceptions**: a small `AppError` hierarchy with JSON handlers registered on
  the app; unhandled exceptions are logged and masked as 500s.
- **Logging**: single structured `StreamHandler` formatter, configured once.
- **Alembic**: `env.py` derives the URL from app settings (single source of
  truth); `compare_type=True` keeps column types aligned with models. Verified
  no drift via `alembic revision --autogenerate` (empty diff) and an
  up/down/up cycle.
- **Dependencies pinned**: exact versions in `requirements*.txt`.

## Architecture decisions (Phase 2)

- **Parser abstraction**: `DocumentParser` ABC with `ParsedDocument`/`ParsedPage`
  outputs; `ParserRegistry` maps suffix and MIME type to a parser. Adding a
  format is a new parser + one registration.
- **Page-aware parsing**: PDFs expose per-page text and page numbers; flow
  formats (TXT/MD/DOCX) report a single continuous region, so
  `page_number` metadata is only emitted when meaningful.
- **Token-aware chunking**: `TokenChunker` splits on approximate token
  boundaries (word/punctuation regex with character spans) and slides a
  `CHUNK_SIZE` window with `CHUNK_OVERLAP`. Chunk text is reconstructed from
  the original character ranges, so content is never truncated mid-token and
  consecutive chunks share exactly `overlap` tokens.
- **Storage abstraction**: `Storage` ABC with a `LocalDiskStorage` backend so
  an object store can be swapped in later; files are keyed by UUID.
- **Repositories**: `DocumentRepository`/`ChunkRepository` isolate SQL; the
  services orchestrate and own transactions.
- **Ingestion transaction handling**: the document row is created before
  parsing so a parsing failure still persists the document with
  `status=failed` for observability, while client-facing errors remain `4xx`
  with actionable messages.
- **Validation**: `FileValidator` enforces extension whitelist, size limit,
  and non-empty content; parsers additionally verify format signatures (e.g.
  PDF header) to catch renamed files.
- **Config-driven**: `CHUNK_SIZE`, `CHUNK_OVERLAP`, `UPLOAD_DIR`, and
  `MAX_UPLOAD_SIZE_MB` are environment variables; chunker settings are
  validated at load time.
- **Test isolation**: integration tests run against a dedicated
  `TEST_DATABASE_URL` (created via `docker compose exec db createdb ...`) and
  an in-memory `tmp_path` storage, so neither the development database nor the
  filesystem is touched.

## Roadmap (future phases)

- Phase 3: contextualization (LLM context generation) and embeddings;
  BM25 index, hybrid retrieval, fusion, reranking.
- Phase 4: chat + streaming, citations, baseline-vs-contextual comparison.