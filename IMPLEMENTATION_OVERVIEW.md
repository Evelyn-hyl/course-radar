# CourseRadar Implementation Overview

## Current state

CourseRadar is a course-scoped retrieval-augmented study assistant. It can create courses, ingest PDF material, clean and chunk extracted text, generate local embeddings, search relevant chunks with pgvector, generate a grounded answer with Gemini, and display the answer with page-level citations in the React frontend.

The working implementation now extends beyond the original M0 frontend prototype into ingestion, retrieval, and grounded answer generation. Concept detection models and tables exist, but concept extraction is not yet part of the active pipeline.

## Architecture

```text
React chat UI
    │
    ├── POST /courses/{course_id}/ask
    │
FastAPI API routes
    │
Application services
    ├── course creation
    ├── document ingestion
    ├── semantic retrieval
    └── grounded answer generation
    │
Repositories
    ├── courses
    ├── documents/chunks
    └── pgvector similarity search
    │
PostgreSQL + pgvector
```

External and model dependencies:

- PyMuPDF4LLM for layout-aware PDF-to-Markdown extraction.
- `ftfy` and deterministic cleanup rules for extraction normalization.
- `google/embeddinggemma-300m` through Sentence Transformers for local embeddings.
- Gemini through the official `google-genai` SDK for cloud answer generation.
- PostgreSQL with pgvector for persistent vector search.

## Implemented backend functionality

### Course management

- `POST /courses` creates a course with a generated UUID.
- Course names are normalized and blank names are rejected.
- Documents and retrieval requests are scoped by course UUID.

### PDF ingestion

- `POST /documents` accepts a multipart PDF upload and its metadata:
  - `course_id`
  - `title`
  - `source_type`
  - optional `week`
- Upload validation covers extension, content type, PDF signature, course existence, duplicate checksums, and a 25 MB limit.
- Files are stored locally under `backend/data/uploads/{course_id}/{document_id}.pdf`.
- The document is flushed before dependent chunks are inserted, satisfying the foreign-key ordering requirement while retaining one atomic transaction.
- Failures roll back database changes and remove the newly written file.

### Extraction and cleanup

- PyMuPDF4LLM produces one layout-aware Markdown chunk per page.
- Each chunk retains page start/end metadata.
- Cleanup runs before embedding and persistence:
  - repairs mojibake such as broken curly quotes and math symbols;
  - normalizes line endings and excessive blank lines;
  - converts `<br>` tags into line breaks;
  - removes extraction-only picture boundary comments while preserving their contents;
  - removes soft hyphens and zero-width spaces;
  - preserves meaningful Markdown and inline HTML.

### Embeddings

- Document chunks use `SentenceTransformer.encode_document()`.
- Search questions use `SentenceTransformer.encode_query()`.
- Embeddings are normalized 768-dimensional vectors from `google/embeddinggemma-300m`.
- Model inference runs outside the FastAPI event loop.
- The embedding client is cached once per backend process with `@lru_cache`.
- PostgreSQL stores the vectors in `chunks.embedding` with the associated model name.

### Retrieval

- `GET /courses/{course_id}/search?query=...&limit=...` exposes raw ranked retrieval results.
- Search embeds the question, filters chunks to the requested course, excludes null vectors, and orders results by pgvector cosine distance.
- `ChunkCandidate` gives the repository/service boundary a named structure instead of an error-prone positional tuple.
- Retrieval responses include chunk text, document identity/title, page range, optional chapter/section metadata, and cosine distance.

### Grounded answer generation

- `POST /courses/{course_id}/ask` accepts:

  ```json
  { "question": "What is Dirac's theorem?" }
  ```

- The service retrieves the five nearest chunks.
- Retrieved chunks are labeled with small integer source IDs before being sent to Gemini.
- Gemini is instructed to answer only from supplied course material and treat source content as data, not instructions.
- Structured output returns the answer and cited source IDs.
- The backend validates source IDs and resolves document/page metadata itself, preventing the model from inventing citation metadata.
- If retrieval finds no context, the service returns an explicit course-material fallback without calling Gemini.
- The answer generator is behind an `AnswerGenerator` protocol, so Gemini can be replaced without changing retrieval or citation orchestration.

### Persistence and migrations

- Docker Compose provides local PostgreSQL with pgvector on host port 5433.
- Alembic migrations:
  1. enable the `vector` extension;
  2. create the initial schema;
  3. change embeddings from the former OpenAI size of 1536 to EmbeddingGemma's 768 dimensions.
- Current entities include courses, documents, pages, extraction warnings, chunks, concepts, examples, and example/concept links.

## Implemented frontend functionality

- Responsive React/Vite chat interface.
- Health/connection indicator.
- Suggested prompts and multiline composer.
- Request acknowledgment, loading, error, and retry states.
- Markdown, code, and KaTeX rendering.
- Real calls to `POST /courses/{course_id}/ask` instead of the original mock response.
- Backend answer responses are mapped into assistant messages.
- Page citations render as pills such as `math-180a-ch2 · p. 2`.
- Citation objects retain chunk ID, document ID, and page range for future navigation.
- Until course selection exists, the active course is supplied through `VITE_COURSE_ID` in `frontend/.env`.

## API summary

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Backend health check |
| `POST` | `/courses` | Create a course |
| `POST` | `/documents` | Upload, chunk, embed, and persist a PDF |
| `GET` | `/courses/{course_id}/search` | Inspect ranked semantic retrieval results |
| `POST` | `/courses/{course_id}/ask` | Generate a grounded answer with citations |

## Important design discussions and decisions

### Services and dependency injection

FastAPI dependencies construct request-scoped services and repositories. Services receive their dependencies through constructors instead of instantiating database sessions or model clients internally. This keeps orchestration testable and preserves the request-scoped session lifecycle.

### Repository versus service filtering

- Repositories perform data-bound filtering: course scope, non-null vectors, distance ordering, and SQL limits.
- Services perform application decisions: query embedding, top-k selection, possible future relevance thresholds, deduplication, answer generation, and citation validation.
- A relevance threshold has intentionally not been hard-coded yet; it should be calibrated with real query/result pairs for this model and corpus.

### Local embeddings and cloud generation

OpenAI embeddings were initially implemented, but a live diagnostic showed exhausted API credits. The project moved to local EmbeddingGemma embeddings, avoiding per-request embedding API costs and keeping the full document corpus local.

Answer generation was initially wired to local Ollama, then changed to Gemini at the user's request. The resulting hybrid architecture keeps extraction, document storage, embeddings, and retrieval local, while sending only the five retrieved chunks and question to Gemini.

### Citation trust boundary

The model does not author page numbers or document metadata. It only chooses integer source IDs from the provided contexts. The backend maps those IDs to trusted database records, so citations remain tied to actual retrieved chunks.

### Raw retrieval versus answers

Raw top-k retrieval remains available as a separate endpoint for debugging. This is useful for determining whether a poor result comes from retrieval or generation. The user-facing workflow renders a synthesized answer rather than dumping raw page chunks directly.

## Challenges encountered and resolutions

### Docker and PostgreSQL connectivity

- Docker initially could not reach the Desktop Linux engine because the daemon was not running.
- PostgreSQL authentication failed because another local PostgreSQL instance occupied port 5432.
- The project database was moved to host port 5433, separating it from the older installation.
- pgAdmin initially displayed a previously registered database; refreshing and connecting to the correct host/port exposed the migrated CourseRadar schema.

### Alembic and pgvector

- pgvector had to be enabled before tables containing `Vector` columns could be created.
- Moving from OpenAI embeddings to EmbeddingGemma required a migration from `vector(1536)` to `vector(768)`.
- Existing vectors from different models are not semantically compatible, so the migration clears old embedding/model values before changing dimensions.

### Hugging Face gated model access

- EmbeddingGemma requires accepting Google's usage terms and authenticating with a Hugging Face token.
- The token itself was valid, but file access initially returned a gated-repository `403` because account-level authorization had not yet been granted.
- Fine-grained, read-only access to `google/embeddinggemma-300m` is sufficient after approval.

### Foreign-key insertion order

- Chunk insertion failed because the pending document row had not yet been written.
- Calling `session.flush()` after adding the document establishes the parent row inside the same transaction without prematurely committing.

### PDF math extraction

- PyMuPDF4LLM does not convert equations into LaTeX and may extract equations as individually positioned glyphs or images.
- Regular OCR is not a reliable mathematical-structure solution.
- Accurate equation reconstruction remains a future specialized math-OCR stage; it is not solved by a parser flag.

### Extraction corruption and display noise

- Retrieved chunks exposed broken UTF-8/Windows-1252 sequences, excessive blank lines, HTML break tags, picture markers, and repeated slide boilerplate.
- A conservative cleanup stage now repairs encoding and formatting without deleting potentially useful diagram text.
- Previously stored chunks must be deleted and re-ingested to receive cleaned text and regenerated embeddings.

### Strict typing around model libraries

- Sentence Transformers and Google GenAI expose broad or partially unknown third-party return types.
- The application-facing protocols remain strictly typed.
- NumPy types and narrowly targeted Pyright suppressions are used only at verified third-party boundaries instead of weakening checks for the entire backend.

### Retrieval result shape

- Selecting a chunk, document title, and distance while returning an underspecified tuple caused unpacking mismatches.
- A named `ChunkCandidate` dataclass now defines the repository contract explicitly.

### Course context in the frontend

- The backend is dynamically scoped by the route's `course_id`.
- The frontend currently has no course picker, so it temporarily reads a fixed `VITE_COURSE_ID` from its local environment.
- A question intended for MATH 154 was initially sent to MATH 180A because this environment value pointed at the wrong course.

### Local versus cloud answer generation

- Ollama would have required locally hosting and loading a generative model.
- Gemini was selected instead, while retaining the provider-independent `AnswerGenerator` boundary.
- Generic client-facing 502 messages avoid exposing provider internals; diagnostics should be logged server-side in a future observability pass.

## Verification status

Most recent checks:

- Backend: 21 unit/API tests passing.
- Backend: Pyright reports zero errors and zero warnings.
- Frontend: 3 test files and 4 tests passing.
- Frontend: TypeScript and production Vite build passing.
- Alembic: database migrated to the EmbeddingGemma vector revision with no pending schema operations.
- Gemini: a credential-safe structured-output request succeeded.

## Current limitations and recommended next work

1. Add frontend course listing/selection and remove reliance on `VITE_COURSE_ID`.
2. Add document metadata update and deletion endpoints.
3. Add cascade behavior or explicit cleanup for chunks and future concept/example records when deleting documents.
4. Calibrate retrieval with representative questions, then consider a relevance threshold, hybrid search, or reranking.
5. Add server-side structured logging for embedding and Gemini provider failures.
6. Add citation click-through to a document/page viewer.
7. Integrate concept and worked-example detection only after retrieval quality is stable.
8. Evaluate specialized equation recognition if faithful mathematical rendering becomes a milestone requirement.
9. Add background jobs if ingestion/model inference becomes too slow for synchronous requests.
10. Update the root README, whose milestone/status section still describes the earlier mock-only frontend.

## Local configuration

Backend variables:

```env
DATABASE_URL=postgresql+psycopg2://...
HF_TOKEN=...
GEMINI_API_KEY=...
ANSWER_MODEL=gemini-3.8-flash
```

Frontend variables:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_COURSE_ID=<active-course-uuid>
```

Secrets belong in ignored `.env` files. The committed `.env.example` files should contain placeholders only.

## Working-tree note

The latest ingestion, EmbeddingGemma, retrieval, answer-generation, cleanup, and frontend-integration work is currently uncommitted. Review and commit it by coherent feature area before starting another large milestone.
