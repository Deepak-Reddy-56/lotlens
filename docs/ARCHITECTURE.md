# Architecture Decision Brief — LotLens

## Status
Proposed — pending six-role review. No framework or hosting choice is frozen yet.

## Problem boundary
LotLens supports manufacturing quality engineers investigating recurring component/supplier defects. It retrieves and reasons over verified historical experiences, but does not certify root causes or autonomously close cases.

## Non-negotiable separation of concerns
- Transactional system of record: defect cases, suppliers, components, batches, evidence, actions, verification and audit records.
- Hindsight: persistent investigation experiences, recall and reflection across historical cases.
- LLM: extraction/reasoning that produces validated structured outputs.
- Human/QA: approval of investigation decisions and verified outcomes.

## Proposed logical components (technology-neutral)
1. Web experience: defect intake, case timeline, evidence, recommendation and verification views.
2. API/application service: authentication, authorisation, case lifecycle and business rules.
3. Investigation orchestrator: coordinates retrieval, evidence validation, LLM reasoning and output validation.
4. Memory adapter: isolates Hindsight SDK calls and supports retain/recall/reflect.
5. Relational persistence: canonical manufacturing and workflow records.
6. Audit/telemetry: user actions, model/memory calls, latency, errors and decision traceability.

## Candidate investigation sequence
1. Validate request and permissions.
2. Create/read canonical case from the transactional database.
3. Recall candidate historical experiences from Hindsight.
4. Resolve each referenced case/evidence ID against the transactional database and enforce access boundaries.
5. Build a bounded evidence packet with provenance and outcome status.
6. Ask the model for a schema-validated investigation recommendation.
7. Validate references, distinguish facts/hypotheses, and return uncertainty.
8. Human chooses an action; persist it transactionally.
9. QA records verification.
10. After successful commit, retain an idempotent, versioned experience in Hindsight; record memory-sync status for retry/reconciliation.

## Key design questions for review
- Single orchestrator with tools vs multiple specialised agents?
- How to handle Hindsight recall ranking, filters and case-ID validation?
- What is the memory schema and how do we avoid stale/contradictory memories?
- How are unsuccessful, inconclusive and verified corrective actions represented?
- Which data must never be sent to the LLM or memory service?
- How do we isolate organisation data and enforce row-level access?
- What is the fallback behaviour when Hindsight or the LLM is unavailable?
- How do we evaluate retrieval relevance and recommendation quality?
- What is the simplest deployable architecture for 4–5 developers?

## Constraints
- Hindsight is mandatory and central.
- Build one thin vertical slice before broad features.
- Prefer a modular monolith unless evidence justifies distributed services.
- No autonomous safety-critical action.
- Use synthetic, documented demo data.
- Secrets stay in server-side environment variables/secrets management.
- All model outputs are untrusted inputs and require validation.

## Approval gates
Architect: boundaries and component architecture.
System designer: ERD, APIs, state machine and data flow.
Developer: implementation feasibility and Hindsight integration proof.
DevOps: deployability, CI/CD, secrets and observability.
QA: requirements, risk controls and acceptance criteria.
Testing: automated test strategy and measurable test scenarios.

The board must record decisions and trade-offs in docs/DECISIONS/ before implementation begins.
