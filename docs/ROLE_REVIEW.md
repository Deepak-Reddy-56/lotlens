# Six-Role Engineering Review — Phase 2 Baseline

Status: Initial implementation review recorded; human team sign-off is still required.
Date: 2026-11-07
Implementation PR: https://github.com/Deepak-Reddy-56/lotlens/pull/8

This document records the six engineering perspectives used to shape the first implementation. It is not a claim that six independent human reviewers have approved the design.

## 1. Senior Solutions Architect

Recommendation: use a modular monolith for the hackathon MVP. Keep cases, investigation orchestration, Hindsight adapter, verification and audit as clear modules inside one backend.

Rationale:
- Four-to-five developers can integrate one application faster than multiple services.
- Hindsight has a central role without becoming the transactional source of truth.
- The initial workflow needs orchestration, not a fleet of autonomous agents.

Guardrails: no microservices or multiple autonomous agents without measured need; no public deployment before authentication, organisation isolation, migrations and secret management; no autonomous root-cause certification or production action.

## 2. System Design Engineer

Recommendation: use relational records for suppliers, components, production lots, defect cases, corrective actions, investigations, verifications, memory-sync status and audit events.

Rationale:
- Defect lifecycle and QA decisions must be deterministic and queryable.
- Hindsight memory is derived experience and can be rebuilt from canonical records.
- Recalled case references must resolve against the database before appearing as evidence.

Design constraints:
- Production lot identity is scoped by supplier and component.
- Corrective actions have deterministic ordering; QA explicitly selects the action it verifies.
- A case is VERIFIED only when the action is effective and root-cause status is confirmed.
- Ineffective/inconclusive actions or unresolved causes leave the case INVESTIGATING.

## 3. Senior Developer

Recommendation: FastAPI, Pydantic v2, SQLAlchemy async, and the official Hindsight Python SDK async operations aret ain/arecall/areflect. The frontend uses React, TypeScript and Vite.

Rationale:
- Async SDK operations fit FastAPI's event loop.
- Hindsight retain, recall and reflect already passed the team's three-case Cloud proof of concept.
- The first application slice does not require a second LLM provider key.

Known caveat: the official SDK guide documents retain context and metadata but does not document an operation_id parameter. The implementation does not pass that undocumented argument. A durable outbox/deduplication design is required before production to address ambiguous network failures during memory sync.

## 4. DevOps Engineer

Recommendation: keep the first development loop local:
- SQLite as a low-friction local database.
- Docker Compose PostgreSQL as an optional shared development database.
- Hindsight Cloud for memory.
- GitHub Actions for backend and frontend checks.

Guardrails:
- API keys stay in the root .env or deployment secret manager; never commit them.
- The development backend has no authentication/organisation isolation and must not be exposed publicly.
- Use PostgreSQL and migrations for shared/deployed environments.
- Deployment is not part of this phase's completion claim.

## 5. QA Engineer

Mandatory invariants:
- Similar symptoms do not prove a common root cause.
- An ineffective action does not prove a different cause.
- Facts, hypotheses and recommendations remain distinguishable.
- Only case references found in canonical records appear as validated historical evidence.
- Whitespace-only root-cause text cannot satisfy confirmation.
- QA selects the exact corrective action being verified.
- An LLM cannot mutate case status directly.

Current limitations: no authentication or organisation-level access enforcement; narrative Reflect output is not a typed diagnostic contract; full structured evidence validation remains future work.

## 6. Testing Engineer

Current automated checks:
- Backend compileall.
- Backend domain tests for canonical case-code parsing and verification validation.
- Frontend TypeScript/Vite production build.

Next required layers:
- API integration tests with a temporary SQLite database.
- Hindsight adapter tests with a mocked client.
- End-to-end case intake, investigation, corrective action, QA verification and memory retain.
- Failure injection for Hindsight outage, malformed output, memory-sync failure and retry.
- Larger fixed hard-negative benchmark beyond the three initial synthetic cases.

## Cross-role decision

Proceed with the current modular-monolith baseline for the first working demo. Do not add infrastructure or agents that do not strengthen the core learning workflow.

## Approval still required from the team

- Confirm the selected stack and data model.
- Confirm the QA state-transition rules.
- Review security and local-only limitations.
- Assign actual team members to the six responsibilities.
- Approve the next milestone: API integration tests and local end-to-end execution.
