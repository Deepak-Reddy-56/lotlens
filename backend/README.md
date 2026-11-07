# LotLens Backend

FastAPI modular monolith for the first LotLens vertical slice.

## Local setup (Windows PowerShell)

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Copy the root env template if not already present and set the Hindsight values:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Set `HINDSIGHT_API_KEY`, `HINDSIGHT_BASE_URL`, `HINDSIGHT_BANK_ID`. Never commit `.env`.

Run the API from the repository root:

```powershell
$env:PYTHONPATH = "backend"
python -m uvicorn app.main:app --reload --app-dir backend
```

API documentation: http://localhost:8000/docs

## First-run workflow

1. Open `POST /api/v1/demo/seed` in Swagger to create canonical database records matching the three Hindsight POC cases. This endpoint does not write to Hindsight.
2. Open `GET /api/v1/cases` and copy a case `id`.
3. Call `POST /api/v1/cases/{id}/investigate`.
4. Propose an action using `POST /api/v1/cases/{id}/actions`.
5. Submit QA verification using `POST /api/v1/cases/{id}/verify`.

The browser dashboard will call these same endpoints.

## Database

Local default: SQLite at `./lotlens.db`. Set `DATABASE_URL` to a PostgreSQL async URL (for example `postgresql+asyncpg://...`) for a shared environment.

The current startup `create_all` is for development only. Add and run Alembic migrations before production deployment.

## Important limitations

- No authentication/organisation isolation is implemented yet; do not expose this development API publicly.
- Demo data is synthetic.
- Hindsight references are only displayed as historical evidence after matching case codes against canonical database rows.
- Every AI recommendation still requires human review.
