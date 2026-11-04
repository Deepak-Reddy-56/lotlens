# Hindsight Memory Design — LotLens

## Status
Open design. Must be validated against the installed Hindsight SDK/API version before implementation.

## Purpose
Persist investigation experiences that improve later investigations. Hindsight is not the transactional database and must not be treated as a substitute for canonical case records.

## Candidate experience schema (logical, not assumed SDK payload)
- experience_id / idempotency_key
- organisation_scope
- case_id (canonical database ID)
- occurred_at
- supplier_id, component_id, lot_id (canonical references)
- defect_symptoms (normalised and original wording)
- investigation_findings
- root_cause_status: confirmed | suspected | unknown | disputed
- root_cause (only when appropriately verified)
- corrective_actions: action, status, dates
- outcome: effective | ineffective | inconclusive | pending
- verification_status and verifier reference
- evidence_refs (canonical evidence IDs)
- source_version / schema_version
- sensitivity classification

The final shape must respect Hindsight's supported retain API and avoid assuming arbitrary metadata filtering exists.

## Operations
### Retain
Only after transactional writes succeed. Retain verified experiences as authoritative learning. Pending/suspected experiences may be stored only with explicit status and must never be presented as confirmed. Use idempotency and retry/reconciliation.

### Recall
Retrieve candidate experiences using the defect description and structured context. Resolve all returned case/evidence references against PostgreSQL and enforce organisation/user permissions before use.

### Reflect
Synthesize from a bounded, validated evidence packet. The model must return structured output with candidate patterns, supporting case IDs, disconfirming cases, known differences, prior corrective actions and outcomes, next investigation suggestions, uncertainty/evidence gaps, and no claim of confirmed root cause unless canonical verification supports it.

## Consistency and safety
- PostgreSQL is canonical.
- Memory is derived and rebuildable.
- Never allow memory text alone to authorise case state transitions.
- Track memory sync status and retry failed retention.
- Handle stale memories by rechecking canonical case status.
- Scope memories by organisation.
- Minimise personal/confidential data.
- Log retain/recall/reflect trace IDs and versions without leaking secrets.

## Evaluation
Create a fixed benchmark of synthetic queries with expected relevant cases and hard negatives (similar symptoms, different causes). Measure Recall@3, evidence-reference validity, unsupported claims and whether the output correctly reports conflicting/insufficient evidence.

## Required spike
1. Retain at least two distinct historical cases, one effective and one ineffective corrective action.
2. Recall using paraphrased symptom descriptions.
3. Reflect across both cases, including disconfirming evidence.
4. Demonstrate that future recommendation references actual case IDs.
5. Verify that an unresolved hypothesis is not represented as confirmed.
