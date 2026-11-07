# LotLens

**Persistent Failure Intelligence for Manufacturing**

LotLens is a Hindsight-powered manufacturing investigation agent. It helps quality engineers connect historical defect experiences, remember verified and unsuccessful corrective actions, and formulate evidence-backed next investigations.

> Current status: first vertical slice under development. The Hindsight Cloud retain/recall/reflect proof of concept has passed a fixed three-case synthetic scenario. The application is not production-ready.

## Start here
- [Problem statement](docs/PROBLEM_STATEMENT.md)
- [Requirements and MVP](docs/REQUIREMENTS.md)
- [Architecture decision brief](docs/ARCHITECTURE.md)
- [Six-role engineering board](docs/ENGINEERING_BOARD.md)
- [Implementation status](docs/IMPLEMENTATION_STATUS.md)
- [First vertical-slice ADR](docs/DECISIONS/ADR-0002-first-vertical-slice-architecture.md)
- [Six-role implementation review](docs/ROLE_REVIEW.md)
- [Hindsight memory design](docs/MEMORY_DESIGN.md)
- [Hindsight Cloud setup](docs/HINDSIGHT_SETUP.md)
- [Hindsight proof-of-concept results](docs/POC_RESULTS.md)
- [Draft API contracts](docs/API_CONTRACTS.md)
- [QA strategy](docs/QA_STRATEGY.md)
- [Testing strategy](docs/TESTING_STRATEGY.md)

## Architecture baseline
- Backend: FastAPI + SQLAlchemy async.
- Local database: SQLite; PostgreSQL supported through `DATABASE_URL`.
- Agent memory: Hindsight Cloud Python SDK (async retain/recall/reflect).
- Frontend: React + TypeScript + Vite.
- See ADR-0002 for trade-offs and current limitations.

## Run locally (Windows PowerShell)

### Backend
From the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Set `HINDSIGHT_API_KEY` in the root `.env`. Keep the key out of GitHub and chat. The default database is SQLite.

Start the API in terminal 1:

```powershell
python -m uvicorn app.main:app --reload --app-dir backend
```

Swagger UI: http://localhost:8000/docs

### Frontend
In terminal 2:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open http://localhost:5173.

### First demo flow
1. In Swagger, call `POST /api/v1/demo/seed`. This creates canonical database records matching LOT-POC-001/002/003; it does not write to Hindsight.
2. Refresh the dashboard and select LOT-POC-002.
3. Click **Investigate with historical memory**.
4. Review the validated historical-case cards and Hindsight synthesis.
5. Record an engineer-approved corrective action.
6. Submit QA verification. An effective action with a confirmed root cause marks the case VERIFIED; ineffective/inconclusive actions or unresolved causes return it to INVESTIGATING.
7. If Hindsight memory sync fails, use `POST /api/v1/cases/{case_id}/memory-sync/retry` in Swagger.

## Optional PostgreSQL for local team development

```powershell
docker compose up -d db
```

Then set this in root `.env`:

```env
DATABASE_URL=postgresql+asyncpg://lotlens:lotlens_dev_only@localhost:5432/lotlens
```

The Compose credentials are local-development only. Do not reuse them in deployment.

## Tests

```powershell
python -m pip install pytest
$env:PYTHONPATH = "backend"
python -m compileall -q backend/app backend/tests
python -m pytest backend/tests -q
```

## Important limitations
- No authentication or organisation-level isolation yet. Do not expose the development API publicly.
- Development startup uses SQLAlchemy `create_all`; add Alembic migrations before production.
- Demo data is synthetic.
- Hindsight is derived memory, not the system of record. Recalled case IDs are matched to canonical database rows before being displayed as evidence.
- Reflect produces narrative text. Citation warnings are checked, but typed structured reasoning and a larger evaluation benchmark remain to be implemented.
- Human engineers and QA retain decision-making authority.
