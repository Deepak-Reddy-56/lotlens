# ADR-0002: First LotLens vertical-slice architecture

- Status: Proposed implementation baseline — subject to team review
- Date: 2026-11-07

## Context
The Hindsight proof of concept passed a fixed three-case synthetic scenario. The next step is a usable end-to-end workflow for a four-to-five-person team, without premature distributed services or multiple autonomous agents.

## Decision
Build a modular monolith with the following baseline:
- API/backend: Python 3.12+, FastAPI, Pydantic v2.
- Persistence: SQLAlchemy 2 async; SQLite for local quick start, PostgreSQL for shared/deployed environments.
- Persistent memory: official `hindsight-client` Python SDK, using async `aretain`, `arecall`, `areflect` in FastAPI.
- Frontend: React + TypeScript + Vite.
- Local shared DB option: Docker Compose PostgreSQL.
- CI: GitHub Actions for backend compilation/tests; frontend build check.
- Reasoning: Hindsight Reflect produces the initial investigation narrative; backend validates surfaced case codes against canonical DB rows and exposes only validated cases as evidence. All actions remain human/QA approved.

## Why this scope
- A single deployable backend keeps four-to-five-person integration manageable.
- The async Hindsight SDK methods fit FastAPI's event loop.
- SQLite removes local setup friction; PostgreSQL is available for shared data and deployment.
- React/Vite is quick to iterate for the dashboard.
- A second LLM provider key is not required for the first vertical slice; Hindsight provides the initial synthesis operation.

## Case lifecycle
- `OPEN` → `INVESTIGATING` when the agent is run.
- `INVESTIGATING` → `AWAITING_QA` when an engineer records an action.
- QA verification retains the outcome in Hindsight.
- Case becomes `VERIFIED` only when the action is verified effective AND root cause status is confirmed.
- Ineffective/inconclusive actions or unresolved causes return to `INVESTIGATING`.

## Data boundary
- SQL database is canonical for supplier, component, lot, case, actions, verification, investigation and audit records.
- Hindsight is derived experience memory, not the system of record.
- Every recalled case code is checked against canonical records before it is displayed as historical evidence.
- Unlinked memory references and unvalidated citations are surfaced as warnings.

## Deliberate limitations for this slice
- No authentication or organisation isolation yet; local development only. Do not expose publicly.
- Startup table creation is for development. Alembic migrations are required before production.
- No PDF/ERP/MES/IoT ingestion.
- No autonomous root-cause certification or production action.
- Narrative Reflect output is not a typed or calibrated diagnostic. A larger benchmark and structured validation are required.
- API retry support exists for failed memory syncs. The public Python SDK documentation does not document an idempotency `operation_id` argument for retain, so exactly-once delivery across ambiguous network failures is not guaranteed; use the verification reference in retain metadata and add a durable outbox/deduplication strategy before production.

## Follow-up decisions
1. Add an authentication provider and organisation-level access control.
2. Add Alembic migrations and deployment configuration.
3. Expand memory benchmark and structured recommendation evaluation.
4. Revisit a separate LLM provider only if Reflect's quality/format limitations justify it.
