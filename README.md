# CourseRadar

CourseRadar is a course-aware study workspace for grounded search and explanations across class materials. M0 provides the frontend chat shell and a FastAPI health endpoint; chat responses are clearly labeled previews until retrieval is implemented.

## Local development

### Backend

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000` and exposes `GET /health`.

### Database migrations

CourseRadar uses Alembic for PostgreSQL schema migrations. From `backend`, set
the connection URL and apply committed migrations:

```powershell
docker compose up -d database

cd backend
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/course_radar"
python -m alembic upgrade head
```

Check that the local database is healthy with:

```powershell
docker compose ps
```

To stop PostgreSQL without deleting its data:

```powershell
docker compose stop database
```

The named Docker volume `course_radar_postgres` preserves database data across
container restarts and recreation. Removing that volume deletes the local
database and is intentionally not part of the normal development commands.

After changing SQLAlchemy models, generate and review a migration before
applying it:

```powershell
python -m alembic revision --autogenerate -m "describe schema change"
python -m alembic upgrade head
```

The first committed migration enables PostgreSQL's `vector` extension. Keep
database credentials in the environment; `backend/.env.example` is only a
template.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`. Set `VITE_API_BASE_URL` to override the default backend URL.

## M0 status

- [x] FastAPI health endpoint with local-development CORS
- [x] Responsive chat shell with suggestions and multiline composer
- [x] Deterministic acknowledgment and honest typed mock adapter
- [x] Loading, success, error, retry, and backend connection states
- [x] Markdown, code, KaTeX, and demo citation rendering
- [x] Keyboard, focus, live-region, and reduced-motion support

PDF ingestion, retrieval, PostgreSQL persistence, and real course-material citations begin in later milestones.
