from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.models import DefectCase
from app.services.hindsight_service import MemoryHit


@dataclass
class InvestigationContext:
    prompt: str
    evidence_case_codes: list[str]
    unlinked_case_codes: list[str]


def case_summary(case: DefectCase) -> str:
    return (
        f"Case {case.case_code}: Supplier {case.supplier.code} ({case.supplier.name}); "
        f"component {case.component.code} ({case.component.name}); lot {case.lot.code}; "
        f"symptoms: {case.symptoms}; description: {case.description}; "
        f"severity: {case.severity}; status: {case.status}; "
        f"root-cause status: {case.root_cause_status}; "
        f"root cause: {case.root_cause or 'not confirmed'}; "
        f"actions: "
        + "; ".join(
            f"{action.description} [outcome={action.outcome}]"
            for action in case.actions
        )
    )


def build_investigation_context(
    current_case: DefectCase,
    hits: Sequence[MemoryHit],
    validated_cases: Sequence[DefectCase],
) -> InvestigationContext:
    validated_codes = {case.case_code for case in validated_cases}
    recalled_codes = {
        code
        for hit in hits
        for code in hit.case_codes
    }
    evidence_codes = sorted(validated_codes - {current_case.case_code})
    unlinked_codes = sorted(recalled_codes - validated_codes)

    summaries = "\n".join(
        f"- {case_summary(case)}" for case in validated_cases
    ) or "- No recalled case references could be matched to canonical records."

    prompt = f"""
You are LotLens, a manufacturing quality investigation assistant.
Analyse the current defect using ONLY the canonical case records below as factual evidence.
Hindsight memory is retrieval context, not an authoritative database. Do not invent cases,
suppliers, batch facts, corrective actions, test results or root causes.

CURRENT CASE (canonical record):
{case_summary(current_case)}

HISTORICAL CASES VALIDATED AGAINST THE APPLICATION DATABASE:
{summaries}

STRICT EVIDENCE RULES:
1. A matching symptom does not prove a shared root cause.
2. An ineffective corrective action proves only that the action was ineffective; it does not
   prove a different cause or rule out another hypothesis.
3. Mark causes as confirmed only when the canonical record explicitly marks them confirmed.
4. Do not transfer one supplier's corrective action to another supplier without documented
   cross-supplier evidence and an approved validation plan.
5. Prefer staged investigation using available process records and measurements before
   proposing expensive laboratory analysis. Specialised tests must be conditional and
   require engineer approval.
6. Cite only the case codes present in the canonical records above. If evidence is missing,
   state that it is missing.
7. Separate known facts, hypotheses, disconfirming evidence, and recommended next steps.
8. Do not claim a case is closed or an action is verified unless the canonical record says so.

Respond in concise Markdown with these sections:
- Current-case assessment
- Relevant historical evidence (cite case codes)
- What is known vs unknown
- Recommended staged investigation
- Risks and human approvals required

Current case: {current_case.case_code}
Allowed historical case codes: {", ".join(evidence_codes) or "none"}
Recalled but unlinked case codes (do not cite as evidence): {", ".join(unlinked_codes) or "none"}
""".strip()

    return InvestigationContext(
        prompt=prompt,
        evidence_case_codes=evidence_codes,
        unlinked_case_codes=unlinked_codes,
    )
