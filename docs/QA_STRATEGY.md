# QA Strategy — LotLens

## Critical invariants
1. No case closes without authorised QA verification.
2. A model cannot mutate case state directly.
3. Every cited historical case/evidence reference resolves to an accessible canonical record.
4. Similar symptoms do not automatically imply same root cause.
5. Pending/unverified hypotheses are never presented as confirmed.
6. Memory sync failure does not roll back or corrupt a committed case.
7. Cross-organisation access is denied.
8. Hindsight/LLM failure produces a safe, clear degraded state.

## Acceptance scenarios
- New case, no memory matches: report evidence gap and offer general next steps clearly labelled.
- Similar case with verified effective action: retrieve and explain why relevant.
- Similar symptom but different verified cause: surface disconfirming case and differences.
- Previously ineffective corrective action: warn against repeating it without new evidence.
- Contradictory cases: present conflict and request human review.
- Unverified historical case: label as provisional.
- Hindsight unavailable: case intake/detail remains available; investigation indicates unavailable memory.
- Duplicate verification/retry: no duplicate business event.
- User from another organisation: cannot access case or memory.
- Malformed model JSON or fabricated case ID: reject/repair safely, never display as evidence.

## Release gates
- All critical invariants pass.
- Critical user journeys pass end-to-end.
- No known critical/high security issue.
- Evaluation benchmark recorded with query-level results.
- Demo path reproducible from seeded synthetic data.
