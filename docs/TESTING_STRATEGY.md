# Testing Strategy — LotLens

**Status:** Backend domain, API integration and local CORS tests are implemented. The backend suite passed in GitHub Actions and the project owner confirmed a successful local Windows pytest run. Evaluation targets remain provisional until measured on a larger curated dataset.

## Current automated coverage

### Backend CI and local verification

GitHub Actions installs dependencies on Python 3.12, compiles the backend and tests, then runs pytest. The owner has also run the backend pytest suite successfully from the Windows PowerShell virtual environment.

The current suite contains:
- Domain/schema tests for case-code parsing, evidence validation, QA cause validation and demo-seed idempotency.
- API integration tests using a fresh temporary SQLite database per test.
- A deterministic Hindsight test double, covering Recall/Reflect/Retain success and selected failure modes without external network calls.
- CORS preflight tests for the configured localhost and loopback frontend origins, plus rejection of an unlisted origin.

Latest recorded CI run: **29 passed in 3.91 seconds**; compile check passed. Local owner-confirmed pytest run: **passed**; console transcript and runtime were not retained. See docs/TEST_REPORT.md for the execution record and manual acceptance checklist.

### Frontend CI

GitHub Actions uses Node.js 22 and runs npm install followed by the TypeScript and Vite production build. The frontend styling commit's build passed. This is a compile/build check, not a browser E2E test.

## Coverage implemented

1. Unit/domain: canonical case-code extraction, UUID case codes, evidence packet construction, Verification schema validation, root-cause trimming and demo-seed idempotency/backfill.
2. API integration: case creation/retrieval, invalid payload handling, action creation, AWAITING_QA transition, verified-case guards, case/action ownership checks, QA outcome transitions and memory-sync retry.
3. Hindsight failure injection: unconfigured Hindsight, Recall timeout, Reflect failure, Retain failure after database commit, and successful retry.
4. Evidence-integrity checks: only database-resolved historical case codes are returned as evidence; unlinked references and unvalidated case codes from Reflect are reported as warnings.
5. Browser transport: CORS preflight for the two configured local Vite origins and rejection of an unlisted origin.

## Remaining test layers

1. Database integration: PostgreSQL CI service, supplier/lot uniqueness under concurrent requests, transaction rollback, and query ordering under PostgreSQL.
2. Hindsight adapter integration: mocked SDK request/response mapping and a separately labelled live sandbox smoke test using a development bank.
3. Browser E2E: defect intake → Recall → canonical validation → Reflect → engineer action → QA verification → Retain → later Recall.
4. Regression benchmark: a fixed curated dataset containing same-symptom/different-cause records, unknown causes, ineffective actions, stale memories, unlinked references and contradictory evidence.
5. Resilience: DB commit failures, ambiguous Retain timeouts, duplicate QA submissions, malformed/empty Reflect output, and retry concurrency.

## Fixed synthetic fixtures

- LOT-POC-001: Supplier A / A101; insufficient crimp height confirmed; corrective action effective.
- LOT-POC-002: Supplier A / A115; same symptom; reseating/rework ineffective; root cause unconfirmed.
- LOT-POC-003: Supplier B / B204; terminal-plating discontinuity confirmed; distinct corrective action effective.

Do not treat the three-case demonstration as a statistically meaningful benchmark.

## Metrics to record

- Recall@3 per query and mean Recall@3 on a curated fixed test set.
- Canonical reference validity: valid displayed case IDs / all displayed case IDs.
- Unsupported confirmed-root-cause claim rate.
- Correct preservation rate for unconfirmed causes.
- Correct distinction rate for same-symptom/different-cause cases.
- Correct surfacing rate for ineffective actions and disconfirming evidence.
- Memory-sync success/retry rate and duplicate-retain rate.
- API error rate and p50/p95 latency by dependency.

## Provisional targets (not yet measured)

- 100% of displayed case references resolve to canonical records.
- 0 unsupported confirmed-root-cause claims on controlled hard negatives.
- 100% pass for lifecycle invariants.
- Recall@3 >= 80% on at least 20 curated queries before using the metric externally.
- Report query-level results and failure cases; never claim general reliability based only on three seeded examples.

## Failure injection currently covered

- Hindsight not configured (HTTP 503).
- Recall timeout (HTTP 502).
- Reflect error (HTTP 502).
- Retain failure after the QA database commit, with verification preserved and retry successful.
- Unlinked recalled case references and unvalidated case IDs mentioned by Reflect.
- Cross-case corrective-action verification attempt.
- CORS preflight from expected local origins and rejection of an unlisted origin.

Other dependency, transaction and concurrency failures remain on the future test plan.
