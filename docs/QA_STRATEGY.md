# QA Strategy — LotLens

Status: first-slice invariants implemented in API validation and workflows; this is not a production release sign-off.

## Product trust invariants

1. SQL database is canonical for supplier, lot, case, action, root-cause and QA verification facts.
2. Hindsight is derived experience memory, never the system of record.
3. No similar symptom alone proves a shared root cause.
4. Ineffective rework proves only that the attempted action was ineffective.
5. Unknown/suspected causes must not be rendered as confirmed.
6. Only canonical case records resolved from memory references may be returned as historical evidence cards.
7. Unlinked memory codes and unvalidated Reflect citations must be visible as warnings.
8. Case becomes VERIFIED only when QA records an effective action AND a confirmed, non-empty root cause.
9. QA verification is saved even if Hindsight Retain fails; memory sync status must be visible and retryable.
10. Human engineers decide which corrective action to try; QA records outcomes. The agent does not execute manufacturing changes.

## Implemented checks in current branch

- Pydantic validates severity, action outcome, root-cause status and required fields.
- Confirmed root-cause text is trimmed; whitespace-only values are rejected.
- A verification must reference an action belonging to the same case.
- Verified cases reject new actions and new investigation calls.
- Case-code references are resolved against canonical SQL rows before they are passed to Reflect as historical evidence.
- Citation warnings and unlinked memory references are returned.
- Memory retain happens after the SQL verification commit, and failure is recorded separately.

## Known gaps / release blockers

- Authentication, role-based permissions and organisation/tenant isolation are absent. Do not expose this API publicly or use real confidential manufacturing data.
- `verified_by` is currently a submitted string, not an authenticated identity. It is not an access-control boundary.
- Reflect returns narrative Markdown. Structured field-level source citations and typed claim validation are not yet implemented.
- No durable outbox/automatic reconciliation; a crash after DB commit may leave a pending memory sync requiring manual retry.
- Demo data is synthetic and must be labelled as such.
- No Alembic migrations, retention policy, privacy review, rate limits or production threat model yet.

## Acceptance scenarios

| Scenario | Expected behaviour | Current status |
|---|---|---|
| Similar symptom, confirmed earlier cause | Show earlier cause only for its canonical case | Hindsight POC passed; app integration CI passes, runtime demo pending |
| Similar symptom, unknown cause | Keep root cause unknown; ineffective action is not a diagnosis | Hindsight POC passed |
| Same symptom, different confirmed causes | Keep causes attached to their own cases | Three-case synthetic Reflect test passed |
| Unlinked recalled case code | Do not display it as canonical evidence | API implements lookup + unlinked warning |
| Reflect invents a case ID | Return citation warning | API implements code warning |
| Blank confirmed-cause field | Reject request | Schema validation implemented |
| Effective action + confirmed root cause | Case becomes VERIFIED | Lifecycle implemented |
| Ineffective/inconclusive action or unknown cause | Case remains INVESTIGATING | Lifecycle implemented |
| Hindsight unavailable during verification | Preserve SQL verification; mark sync failed | Implemented; live failure injection pending |
| Cross-tenant user | Deny access | Not implemented; release blocker |

## Release gate
Do not use as a shared or production system until authentication/tenant scoping, migrations, field-level provenance, durable memory sync, API/E2E tests and security review are completed. Demo only with synthetic data and a local/private environment.
