# API Contracts — Draft

Status: proposed contract; finalise with system designer before coding. Prefix: /api/v1.

## Cases
- POST /cases — create a defect case.
- GET /cases — list/search cases.
- GET /cases/{case_id} — case detail.
- GET /cases/{case_id}/timeline — chronological events.
- POST /cases/{case_id}/investigations — request an investigation.
- GET /investigations/{investigation_id} — investigation status/result.
- POST /cases/{case_id}/actions — record an engineer-approved corrective action.
- POST /cases/{case_id}/verification — QA verification.
- GET /cases/{case_id}/related — validated related historical cases.
- POST /memory-sync/{case_id}/retry — retry derived-memory sync.
- GET /health/live and /health/ready — process/dependency health.

## Recommendation response (logical contract)
```json
{
  "investigation_id": "uuid",
  "case_id": "uuid",
  "summary": "string",
  "candidate_patterns": [],
  "supporting_cases": [
    {"case_id":"uuid","evidence_refs":[],"why_relevant":"string","outcome":"effective|ineffective|inconclusive|pending"}
  ],
  "disconfirming_cases": [],
  "known_differences": [],
  "suggested_next_steps": [],
  "hypotheses": [
    {"description":"string","confidence":"low|medium|high","supporting_refs":[],"limitations":[]}
  ],
  "evidence_gaps": [],
  "requires_human_review": true
}
```

All case references must be validated by the backend before this response is presented. Confidence labels are not calibrated probabilities.

## API rules
- Use consistent error envelope and HTTP status codes.
- Validate request/response schemas.
- Use idempotency keys for investigation/action/verification operations where retries may occur.
- Enforce role and organisation scope on every query.
- Do not expose provider keys or raw sensitive prompts.
- Keep agent/memory operations separate from direct case state mutation.
