# Architecture Decision Brief - LotLens

## Status
The first vertical-slice baseline was merged into `main` through PR #8 on 9 November 2026. This records the current development architecture. It is not a production deployment approval or a formal team security sign-off.

## Problem boundary
LotLens supports manufacturing quality engineers investigating recurring component and supplier defects. It retrieves and reasons over verified historical experiences, but does not certify root causes or autonomously close cases.

## Implemented baseline

- Web experience: React, TypeScript and Vite.
- API/application service: Python FastAPI modular monolith.
- Domain persistence: SQLAlchemy 2 async, with SQLite as the local default and PostgreSQL URL support.
- Memory adapter: official `hindsight-client`, using async `arecall`, `areflect` and `aretain`.
- Investigation orchestration: recall candidate case codes, validate them against canonical SQL records, build a bounded evidence packet, call Reflect, and return citation and unlinked-reference warnings.
- Human workflow: case intake, corrective action entry and QA verification.
- Development operations: Docker Compose PostgreSQL option and GitHub Actions backend/frontend checks.

See [ADR-0002](DECISIONS/ADR-0002-first-vertical-slice-architecture.md), [database design](DATABASE_DESIGN.md), and [implementation status](IMPLEMENTATION_STATUS.md).

## Why a modular monolith
A single backend keeps deployment and data consistency manageable for the first product slice. Hindsight is isolated behind an adapter so it can be tested or changed without rewriting the case workflow.

## Agent topology
The current implementation has one server-side investigation orchestrator, not six autonomous runtime agents. Hindsight Reflect is used for synthesis. Canonical database validation and human decisions remain outside model control.

## Separation of responsibilities
- SQL stores canonical cases, suppliers, components, lots, actions, verifications, audit events and memory-sync status.
- Hindsight stores derived experiences for future recall.
- Reflect produces a narrative synthesis from a bounded packet of validated records.
- Engineers choose corrective actions, and QA verifies outcomes.

## Known gaps before production
Authentication and organisation isolation, Alembic migrations, typed recommendation output, field-level evidence citations, a durable memory-sync outbox, browser end-to-end tests, monitoring and a broader evaluation benchmark remain future work.
