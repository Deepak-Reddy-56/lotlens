# Testing Strategy — LotLens

Status: initial CI baseline exists. Evaluation targets remain provisional until measured.

## Current automated checks

Backend GitHub Actions:
- Python 3.12 dependency install
- Python compile check
- Pytest domain tests: valid case-code parsing, confirmed cause required, unknown cause allowed, whitespace-only confirmed cause rejected, confirmed cause/verifier trimming.

Frontend GitHub Actions:
- Node.js 22
- npm install
- TypeScript + Vite production build

These checks do not yet prove a full API-to-Hindsight-to-browser journey.

## Test layers to add

1. Unit: lifecycle transition matrix, canonical case-code parser, evidence packet builder, schema validation, memory payload format.
2. Database integration: fresh SQLite and PostgreSQL schema, supplier/lot uniqueness, eager-loaded actions ordering, transaction rollback.
3. API integration: case create/list, demo seed idempotency, investigation with mocked Recall/Reflect, action ownership, QA verification, memory sync failure and retry.
4. Hindsight adapter: mock SDK tests plus a separately labelled live sandbox smoke test.
5. E2E: defect intake → Recall → canonical validation → Reflect → engineer action → QA verification → Retain → later Recall.
6. Regression: fixed synthetic benchmark containing same symptom/different causes, unconfirmed root causes, ineffective actions, stale memories, unlinked references and contradictory evidence.

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

## Failure injection

- Hindsight 401/402/404, timeout and 5xx.
- DB commit failure before memory write.
- Memory write timeout after DB commit.
- Duplicate QA submit and manual retry.
- Empty/malformed Reflect response and unknown case references.
- More than one corrective action for a case; QA selects the intended action.
- PostgreSQL unavailable on startup and during request.
