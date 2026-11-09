# API Contracts — first vertical slice

Status: implemented development API; contracts are being stabilised. Prefix: `/api/v1`.

Interactive OpenAPI is exposed at `/docs` while the backend is running.

## Health

### GET /health
Returns service process status, database configuration label, whether the Hindsight API key is configured, and the configured bank ID. This is not yet a dependency readiness probe: it does not perform a live DB or Hindsight request.

## Cases

### GET /api/v1/cases
Lists cases ordered by creation time (newest first). Includes supplier, component, lot and corrective actions.

### GET /api/v1/cases/{case_id}
Returns one canonical case including its actions.

### POST /api/v1/cases — 201
Create a defect case. Request:

```json
{
  "supplier_code": "SUP-C",
  "supplier_name": "Supplier C",
  "component_code": "BMS-CONN",
  "component_name": "BMS Connector",
  "lot_code": "C301",
  "symptoms": "Intermittent open-circuit readings during vibration testing",
  "description": "Failure during end-of-line validation",
  "severity": "high"
}
```

Severity is `low | medium | high | critical`. Supplier/component/lot master rows are reused by code where present; they are created when absent. New case IDs use `LOT-NEW-<UUID>`.

### POST /api/v1/demo/seed
Idempotently seeds the three synthetic canonical POC cases into the SQL database. It does not retain anything in Hindsight. Never use this endpoint with real production data.

## Investigation

### POST /api/v1/cases/{case_id}/investigate
1. Rejects a case already marked VERIFIED.
2. Calls Hindsight Recall using symptom/component/supplier/lot context.
3. Extracts candidate case codes from recall results and resolves them against canonical SQL rows.
4. Builds a bounded evidence packet and calls Hindsight Reflect.
5. Persists the narrative and returns canonical evidence cards, unmatched memory references and unvalidated cited case-code warnings.

Response includes `id`, `case_id`, `query`, `result_text`, `memory_hit_count`, `evidence_cases`, `unlinked_case_codes`, `citation_warnings`, and `created_at`.

This first slice returns narrative text, not the typed recommendation object proposed in earlier draft contracts. Do not describe it as field-level evidence-grounded or calibrated reasoning yet.

## Corrective actions and QA

### POST /api/v1/cases/{case_id}/actions — 201
Request: `{"description":"..." }`. Adds an action and moves the case to `AWAITING_QA`. Verified cases reject new actions.

### POST /api/v1/cases/{case_id}/verify — 201
Request:

```json
{
  "action_id": "action-uuid",
  "action_outcome": "effective",
  "root_cause_status": "confirmed",
  "confirmed_root_cause": "Insufficient crimp height",
  "notes": "Follow-up sample passed",
  "verified_by": "QA Engineer"
}
```

- `action_outcome`: `effective | ineffective | inconclusive`.
- `root_cause_status`: `confirmed | suspected | unknown | disputed`.
- When cause status is confirmed, a non-whitespace `confirmed_root_cause` is mandatory.
- The action must belong to the case.
- Case becomes VERIFIED only when outcome is effective AND root cause is confirmed. Otherwise it returns to INVESTIGATING.
- Verification is committed before Hindsight Retain. The response exposes memory-sync status and any safe error summary.

### POST /api/v1/cases/{case_id}/memory-sync/retry
Retries the newest failed or pending memory-sync record using the canonical verification and action rows. Returns current sync status. This is a manual retry, not a background worker.

## Current limitations / future contract work
- No auth, organisation scope, permissions, idempotency keys or rate limiting.
- No case timeline route, investigation GET route or related-cases route yet.
- No consistent error envelope beyond FastAPI's standard errors.
- Health endpoint needs separate liveness and dependency readiness checks.
- Typed recommendation schema, field-level evidence refs, and structured fact/hypothesis/recommendation arrays are not yet implemented.
