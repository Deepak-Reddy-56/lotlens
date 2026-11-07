# Six-Role Engineering Board — Review Instructions and Current Status

The six roles are engineering review responsibilities; they are not six autonomous runtime agents.

All roles review the problem statement and the first vertical slice. Do not blindly approve the stack. Record alternatives, assumptions, trade-offs, risks, and deferred work.

## Role outputs and owners

1. Senior Solutions Architect — system boundaries, modular-monolith decision, agent topology, NFRs. Review ADR-0002 and `docs/ARCHITECTURE.md`.
2. System Design Engineer — ERD, lifecycle, APIs, evidence provenance, consistency. Review `docs/DATABASE_DESIGN.md` and `docs/API_CONTRACTS.md`.
3. Senior Developer — Hindsight adapter, async SDK use, repository structure and feasibility. Review implementation and the fixed three-case POC.
4. DevOps Engineer — environments, secrets, CI/CD, database backup/migrations, health and deployment. Review both GitHub Actions workflows and Docker Compose.
5. QA Engineer — lifecycle/trust invariants, human approval and security blockers. Review `docs/QA_STRATEGY.md`.
6. Testing Engineer — unit/API/integration/E2E strategy, hard negatives, metrics and failure injection. Review `docs/TESTING_STRATEGY.md`.

## Current implementation status (2026-11-07)

- Hindsight Cloud Retain/Recall/Reflect POC passed the fixed three-case synthetic scenario.
- A first vertical slice is on PR #8: FastAPI, SQLAlchemy, Hindsight adapter, React dashboard, QA verification, memory-sync status/retry, CI.
- Backend CI and frontend build currently pass on the latest PR head.
- The full local dashboard + live Hindsight journey has not yet been run by the project owner.
- No auth/tenant isolation or production deployment; do not expose the development API publicly.

## Review gates still open
- Validate the proposed architecture and six-role ownership.
- Add database/API integration and E2E tests.
- Add auth and tenant isolation before shared use.
- Add Alembic migrations and durable memory-sync outbox.
- Replace narrative-only Reflect output with a typed recommendation schema and field-level evidence refs.
- Verify PostgreSQL deployment and Hindsight outage recovery.

## Final board output
Maintain one unified blueprint: architecture, stack, ERD, API contracts, memory boundaries, security, deployment, QA acceptance, test plan, team ownership, milestones and demo script. Record changes in `docs/DECISIONS/`.
