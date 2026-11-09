# LotLens Test Report

**Report type:** Automated backend/API verification and manual acceptance checklist  
**Application version:** Phase 2 — first investigation vertical slice  
**Branch:** `main` (merged from `feature/phase-2-vertical-slice` through PR #8 on 9 November 2026)  
**Test data:** Synthetic POC records only; no production manufacturing data  
**Report status:** Backend automated tests passed in CI and in the project owner's local environment; live integration and browser acceptance remain pending

## 1. Objective

Verify that the first LotLens investigation workflow preserves canonical manufacturing records, enforces QA lifecycle rules, limits historical evidence to database-backed cases, and handles Hindsight service failures without losing a saved QA verification.

This report distinguishes automated checks from manual acceptance steps. A passing automated test suite does not imply that a live Hindsight account, PostgreSQL deployment, or full browser workflow has been verified.

## 2. Test environment

| Item | Configuration |
|---|---|
| Backend runtime in CI | Python 3.12.16 |
| Local test environment | Windows PowerShell, project virtual environment (`.venv`); exact Python version not recorded |
| API framework | FastAPI |
| Database under automated API tests | Isolated temporary SQLite database per test |
| Test runner | pytest 9.2.0 in CI; local pytest version not recorded |
| External Hindsight dependency | Deterministic in-process test double; no live API calls |
| Frontend build | Node.js 22, TypeScript and Vite |
| CI workflows | `.github/workflows/backend-ci.yml` and `.github/workflows/frontend-ci.yml` |

## 3. Automated test coverage

The suite combines domain/schema tests, API integration tests, and CORS middleware tests.

| Test ID | Area | Verification | Expected result |
|---|---|---|---|
| DOM-01 | Case reference parsing | Supported POC and UUID case-code parsing | Only supported case-code formats are extracted |
| DOM-02 | QA schema | Confirmed root cause omitted | Validation rejects the payload |
| DOM-03 | QA schema | Unknown root cause | Payload is accepted without a confirmed cause |
| DOM-04 | QA schema | Whitespace-only confirmed cause | Validation rejects the payload |
| DOM-05 | QA schema | Whitespace around cause/verifier | Values are trimmed |
| DOM-06 | Case reference parsing | New UUID case-code shape | UUID case code is extracted |
| DOM-07 | Case reference parsing | Short or unrelated reference tokens | Tokens are rejected |
| DOM-08 | Evidence construction | Canonical and unlinked IDs in memory | Only canonical cases become evidence; unlinked IDs are flagged |
| DOM-09 | Demo fixture | Repeated seed and missing QA verification | Seed is idempotent and missing verification is backfilled |
| API-01 | Defect intake | Create a new case and retrieve it | API returns a unique case code and persisted supplier/component/lot data |
| API-02 | Validation | Invalid case and blank corrective action | API returns HTTP 422 |
| API-03 | Corrective action | Record an engineer action | Case moves to AWAITING_QA |
| API-04 | Lifecycle guard | Add action or investigate an already verified case | API returns HTTP 409 |
| API-05 | QA ownership | Verify a case using another case's action | API returns HTTP 404 |
| API-06 | Successful QA | Effective action plus confirmed root cause | Case becomes VERIFIED and Retain is invoked |
| API-07 | QA negative outcomes | Ineffective/inconclusive action or unconfirmed/disputed cause | Case remains INVESTIGATING across four parameter combinations |
| API-08 | Memory failure | Hindsight Retain fails after QA commit | Verification remains saved and sync status is failed |
| API-09 | Memory recovery | Retry a failed Retain after service recovery | Sync status changes to synced |
| API-10 | Evidence integrity | Recall canonical and unlinked case IDs; Reflect mentions an unknown ID | Canonical evidence is returned; unlinked and unvalidated IDs are warned |
| API-11 | Dependency handling | Hindsight is not configured | Investigation returns HTTP 503 |
| API-12 | Dependency handling | Recall times out | Investigation returns HTTP 502 |
| API-13 | Dependency handling | Reflect fails | Investigation returns HTTP 502 |
| API-14 | Memory retry guard | Retry when no pending/failed sync exists | API returns HTTP 404 |
| CORS-01 | Browser preflight | Required localhost and loopback origins are configured | Both local Vite origins appear in the configured allowlist |
| CORS-02 | Browser preflight | localhost Vite origin | Preflight returns HTTP 200 and matching allow-origin header |
| CORS-03 | Browser preflight | 127.0.0.1 Vite origin | Preflight returns HTTP 200 and matching allow-origin header |
| CORS-04 | Browser preflight | Unlisted external origin | Preflight is rejected |
| CI-01 | Static validation | Compile backend application and test modules | Python compilation succeeds |
| CI-02 | Frontend build | TypeScript check and Vite production build | Build succeeds |

**Automated CI result:** 29 tests passed. The four QA negative-outcome combinations are executed as separate pytest cases.

## 4. Synthetic test dataset

The automated API tests use the seeded synthetic POC cases:

- **LOT-POC-001 — Supplier A / lot A101:** insufficient crimp height is recorded as confirmed; the corrective action is effective.
- **LOT-POC-002 — Supplier A / lot A115:** symptoms resemble POC-001, but connector reseating/rework was ineffective and the root cause remains unknown.
- **LOT-POC-003 — Supplier B / lot B204:** similar symptoms have a distinct confirmed cause—terminal plating discontinuity/corrosion—with a different corrective action.

These records intentionally test the distinction between similar symptoms and different root causes. They are fixtures, not evidence of real-world system accuracy.

## 5. Execution record

| Check | Command / source | Result |
|---|---|---|
| Backend compile | `PYTHONPATH=. python -m compileall -q app tests` in CI | **Passed** |
| Backend automated tests (CI) | `PYTHONPATH=. python -m pytest -q tests` | **29 passed in 3.73 seconds** |
| Backend automated tests (local) | `$env:PYTHONPATH = "backend"; python -m pytest backend/tests -v` | **Passed; confirmed by project owner. Local console transcript and runtime were not retained in this report.** |
| Frontend production build | `npm run build` via GitHub Actions | **Passed** in 1.69 seconds on the cleaned PR head |
| Live Hindsight smoke test | Real development bank | Not run |
| Full local browser acceptance | Owner's Windows development environment | Pending |

**Latest pre-merge CI commit:** `803b6b6abc66d0953abbb5de509afee08d34c4aa`  
**Backend CI execution:** 9 November 2026, workflow run [42627097297](https://github.com/Deepak-Reddy-56/lotlens/actions/runs/42627097297) — 29 tests passed in 3.73 seconds.  
**Frontend build execution:** 9 November 2026, workflow run [42627097227](https://github.com/Deepak-Reddy-56/lotlens/actions/runs/42627097227) — production build passed in 1.69 seconds.  
**Merge commit:** `d4e45bdf8e5faf67e11d3be1df7d80b1ab359868`.

Both checks completed successfully on the cleaned pull-request head before PR #8 was squash-merged into `main`. The project owner also confirmed a successful local Windows pytest run; the terminal transcript and exact local runtime were not archived.

## 6. Manual acceptance checklist

Run and record these checks separately after starting the backend and frontend with the owner's development Hindsight configuration:

1. Open the dashboard and confirm the browser can call `/health` and `/api/v1/cases` without CORS errors.
2. Load demo data and confirm all three synthetic cases appear.
3. Open LOT-POC-002 and run an investigation with the configured development Hindsight bank.
4. Confirm recalled evidence is linked to canonical case records and inspect any unlinked-reference/citation warnings.
5. Record a corrective action and verify that the case moves to AWAITING_QA.
6. Submit QA verification with an effective outcome and confirmed root cause; confirm the case becomes VERIFIED.
7. In a separate test case, submit an ineffective or inconclusive outcome and confirm the case does not become VERIFIED.
8. Confirm the verification and Hindsight memory-sync status are displayed. Retry only when a failed/pending sync exists.

Record the date, environment, tester, case ID, observed result, and screenshot/reference for each manual check.

## 7. Limitations

The current automated suite does not establish:

- Live Hindsight API correctness, relevance quality, or production latency.
- PostgreSQL integration or concurrent-write behaviour.
- Full browser end-to-end behaviour across the React UI and backend.
- Authentication, role-based access control, or tenant isolation.
- Production readiness, deployment security, or reliability on real manufacturing data.

The three seeded records are too small for a statistically meaningful retrieval benchmark. A separate curated dataset of at least 20 queries is needed before publishing retrieval metrics such as Recall@3.

## 8. Conclusion

The first LotLens vertical slice passes the current automated backend compile and test checks in CI, with 29 pytest cases passing. The project owner also confirmed that the backend pytest suite completed successfully in the local Windows virtual environment. The frontend TypeScript/Vite build passed in GitHub Actions.

These results validate the covered domain rules, API behaviour, selected Hindsight failure modes, and local CORS middleware behaviour. They do not establish that the full UI workflow has been exercised against a live Hindsight bank. A live Hindsight smoke test and owner-run browser acceptance remain outstanding. The system remains a local development build and must not be exposed publicly or used with confidential production data until the security and operational release blockers are addressed.
