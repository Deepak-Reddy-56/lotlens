# LotLens — Requirements and MVP

## Personas
- Quality engineer: opens and investigates defects.
- QA/quality approver: verifies outcomes and closes cases.
- Administrator: manages users, suppliers and reference data (minimal MVP).

## Functional requirements
- FR-01 Create defect case with supplier, component, production lot, date, symptoms, severity and evidence references.
- FR-02 View case list, detail and chronological investigation timeline.
- FR-03 Retrieve related historical experiences through Hindsight.
- FR-04 Validate recalled case/evidence references against canonical database records.
- FR-05 Generate structured recommendations including candidate patterns, supporting cases, disconfirming evidence, differences, next steps and uncertainty.
- FR-06 Record an engineer's decision and corrective action.
- FR-07 Require QA verification before marking an outcome verified/closed.
- FR-08 Retain verified outcomes in Hindsight after successful database commit.
- FR-09 Show memory-sync status and allow safe retry.
- FR-10 Maintain audit events for important user and agent actions.
- FR-11 Distinguish confirmed facts, hypotheses and recommendations in the UI.
- FR-12 Provide a no-memory baseline for demo/evaluation.

## Non-functional requirements
- Secrets only on server side.
- Enforce authentication and role-based access.
- Scope records and memories to the organisation.
- Validate all inputs and model outputs.
- Graceful degradation when LLM/Hindsight unavailable.
- Observable API and memory failures.
- Reproducible synthetic demo dataset and benchmark.
- Accessible and understandable investigation UI.

## MVP
One organisation, a small set of suppliers/components/lots, synthetic historical cases, one investigation workflow, Hindsight integration, evidence-linked recommendations, QA verification, audit trail and tests.

## Not in MVP
ERP/MES/IoT connectors, autonomous root-cause certification, automatic production actions, predictive maintenance, enterprise-wide multi-tenant admin, broad document ingestion unless a spike proves it essential.
