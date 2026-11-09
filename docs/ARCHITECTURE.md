# Architecture Decision Brief — LotLens

## Status
First vertical-slice baseline implemented on `feature/phase-2-vertical-slice`; PR review and six-role approval remain open. This is not a production deployment decision.

## Problem boundary
LotLens supports manufacturing quality engineers investigating recurring component/supplier defects. It retrieves and reasons over verified historical experiences, but does not certify root causes or autonomously close cases.

## Implemented baseline

- Web experience: React + TypeScript + Vite.
- API/application service: Python FastAPI modular monolith.
- Domain persistence: SQLAlchemy 2 async; SQLite local default, PostgreSQL URL supported.
- Memory adapter: official `hindsight-client`, async `arecall`, `areflect`, `aretain`.
- Investigation orchestration: recall case codes → validate against canonical SQL records → build bounded evidence packet → Reflect narrative → citation/unlinked-reference warnings.
- Human workflow: case intake, corrective action entry, QA verification.
- Operations: Docker Compose PostgreSQL option; GitHub Actions backend/frontend checks.

See [ADR-0002](DECISIONS/ADR-0002-first-vertical-slice-architecture.md), [database design](DATABASE_DESIGN.md), and [implementation status](IMPLEMENTATION_STATUS.md).

## Why modular monolith
A single backend avoids distributed-service deployment and cross-service consistency complexity for a four-to-five-person hackathon team. Hindsight is isolated behind an adapter so it can be tested or changed without rewriting domain workflows.

## Agent topology
One server-side investigation orchestrator in this slice, not six autonomous agents. The six roles are engineering review perspectives, not deployed agent personas. Hindsight Reflect is used for synthesis; canonical DB validations and human decisions remain outside model control.

## Non-negotiable separation
- SQL: canonical cases, suppliers, components, lots, actions, verifications, audit and sync status.
- Hindsight: persistent derived experiences for recall.
- Reflect: narrative synthesis from a bounded canonical evidence packet.
- Human engineer / QA: approves actions and verifies outcomes.

## Known gaps before production
Authentication/organisation isolation, Alembic migrations, typed recommendation output, field-level evidence citations, durable outbox, API/E2E tests, monitoring and a broader evaluation benchmark.
