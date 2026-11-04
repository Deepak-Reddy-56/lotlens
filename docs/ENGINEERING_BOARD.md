# Six-Role Engineering Board — Review Instructions

All roles review the same LotLens problem statement in `docs/PROBLEM_STATEMENT.md` and architecture brief in `docs/ARCHITECTURE.md`.

Do not blindly accept a preselected stack. Evaluate the smallest reliable solution for a team of 4–5. Distinguish confirmed requirements from assumptions. State alternatives, trade-offs, risks, dependencies and what should be deferred.

## Role 1 — Senior Solutions Architect
Owns system boundaries, architecture style, component responsibilities, agent topology, technology evaluation and architecture decisions.
Deliver: architecture diagram, component descriptions, key decisions/trade-offs, NFRs, risks and recommendation.

## Role 2 — System Design Engineer
Owns domain model, relational ERD, APIs, workflows, memory boundaries and state transitions.
Deliver: ERD, entity definitions, API contracts, sequence/data-flow diagrams, state machine, idempotency and consistency design.

## Role 3 — Senior Developer
Owns implementation feasibility, repository structure, coding conventions, Hindsight SDK integration, orchestration and model output schemas.
Deliver: proposed stack with alternatives, module/file structure, Hindsight spike plan, implementation sequence and technical risks.

## Role 4 — DevOps Engineer
Owns environments, hosting, secrets, CI/CD, observability, deployment and recovery.
Deliver: deployment topology, environment matrix, pipeline, health checks, logging/metrics, backup/recovery and cost/operational risks.

## Role 5 — QA Engineer
Owns requirements quality, acceptance criteria, trust/safety, privacy and workflow quality.
Deliver: testable requirements, acceptance matrix, threat/risk assessment, evidence-provenance rules, human approval controls and release criteria.

## Role 6 — Testing Engineer
Owns test architecture and execution strategy.
Deliver: unit/integration/API/E2E/regression test plan, fixtures, test data strategy, failure injection and measurable evaluation metrics.

## Shared mandatory questions
1. How does Hindsight materially change future investigations?
2. What exactly is retained and when? What must not be retained?
3. How will recall references be validated against canonical records?
4. How are facts, hypotheses, confidence and contradictory evidence represented?
5. How are failed, inconclusive and verified corrective actions distinguished?
6. How is memory consistency/retry handled after database commit?
7. How does the product degrade safely during Hindsight/LLM failure?
8. What data is tenant/user scoped?
9. What is the MVP vertical slice?
10. What would make the demo measurable and credible?

## Cross-review
Each role reviews all relevant outputs from the other roles and records blocking concerns. Resolve disagreements explicitly. No role should approve an area outside its expertise without recording assumptions.

## Final board output
A single unified blueprint: architecture, selected stack, ERD, API contracts, memory design, orchestration, security, deployment, QA acceptance criteria, test strategy, team ownership, milestone plan and demo script.

## Approval rule
Do not begin broad feature development until a working Hindsight retain/recall/reflect spike demonstrates the learning loop; canonical data vs memory responsibilities are documented; recommendation provenance and human verification are defined; MVP and out-of-scope features are frozen.
