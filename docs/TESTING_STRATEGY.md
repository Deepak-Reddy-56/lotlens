# Testing Strategy — LotLens

## Test layers
- Unit: domain rules, state transitions, schemas, evidence validation, memory payload mapping.
- Integration: database repositories, Hindsight adapter (mocked and live sandbox), LLM adapter, memory-sync retry.
- API: authentication, authorisation, validation, error envelopes, idempotency.
- E2E: defect intake → investigation → engineer action → QA verification → memory retain → next investigation recall.
- Regression: fixed synthetic benchmark and known failure scenarios.

## Required fixtures
- Verified effective corrective action.
- Verified ineffective corrective action.
- Pending/unverified hypothesis.
- Similar symptoms with different confirmed root causes.
- Contradictory and incomplete cases.
- Cross-organisation cases.
- Duplicate events and provider outages.

## Metrics
- Recall@3 on a fixed set of synthetic investigation queries.
- Percentage of recalled case references that resolve to canonical records.
- Rate of unsupported/fabricated historical claims.
- Correct surfacing of disconfirming cases.
- Correct handling of ineffective actions.
- End-to-end workflow pass rate.
- Latency and error rate per dependency.

## Initial acceptance targets (provisional; validate after baseline)
- 100% validity for displayed historical case references in test set.
- 0 unsupported confirmed-root-cause claims in controlled tests.
- 100% denial of cross-organisation access tests.
- 100% prevention of closing without QA verification.
- Recall@3 target at least 80% on a curated 10-query benchmark; report actual results, do not claim general performance from small synthetic data.
