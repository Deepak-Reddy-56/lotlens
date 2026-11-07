from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import (
    AuditEvent,
    Component,
    CorrectiveAction,
    DefectCase,
    Investigation,
    MemorySync,
    ProductionLot,
    Supplier,
    Verification,
)
from app.schemas import (
    ActionCreate,
    ActionOut,
    CaseCreate,
    CaseOut,
    HistoricalCaseOut,
    InvestigationOut,
    VerificationCreate,
    VerificationOut,
)
from app.services.hindsight_service import HindsightService
from app.services.investigation_service import build_investigation_context

router = APIRouter(prefix="/api/v1", tags=["LotLens"])
CODE_RE = re.compile(r"^LOT-[A-Z0-9]{2,}-[A-Z0-9]{3,}(?:-[A-Z0-9]{3,})*$")


def case_query():
    return select(DefectCase).options(
        selectinload(DefectCase.supplier),
        selectinload(DefectCase.component),
        selectinload(DefectCase.lot),
        selectinload(DefectCase.actions),
    )


async def load_case(session: AsyncSession, case_id: str) -> DefectCase:
    result = await session.execute(case_query().where(DefectCase.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="Defect case not found")
    return case


def to_historical(case: DefectCase) -> HistoricalCaseOut:
    return HistoricalCaseOut(
        case_code=case.case_code,
        supplier_code=case.supplier.code,
        supplier_name=case.supplier.name,
        component_code=case.component.code,
        component_name=case.component.name,
        lot_code=case.lot.code,
        symptoms=case.symptoms,
        root_cause_status=case.root_cause_status,
        root_cause=case.root_cause,
        status=case.status,
        actions=[
            ActionOut.model_validate(action)
            for action in case.actions
        ],
    )


@router.get("/cases", response_model=list[CaseOut])
async def list_cases(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        case_query().order_by(DefectCase.created_at.desc())
    )
    return result.scalars().unique().all()


@router.post("/cases", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
async def create_case(payload: CaseCreate, session: AsyncSession = Depends(get_session)):
    supplier_result = await session.execute(
        select(Supplier).where(Supplier.code == payload.supplier_code)
    )
    supplier = supplier_result.scalar_one_or_none()
    if supplier is None:
        supplier = Supplier(code=payload.supplier_code, name=payload.supplier_name)
        session.add(supplier)
        await session.flush()

    component_result = await session.execute(
        select(Component).where(Component.code == payload.component_code)
    )
    component = component_result.scalar_one_or_none()
    if component is None:
        component = Component(
            code=payload.component_code, name=payload.component_name
        )
        session.add(component)
        await session.flush()

    lot_result = await session.execute(
        select(ProductionLot).where(
            ProductionLot.code == payload.lot_code,
            ProductionLot.supplier_id == supplier.id,
            ProductionLot.component_id == component.id,
        )
    )
    lot = lot_result.scalar_one_or_none()
    if lot is None:
        lot = ProductionLot(
            code=payload.lot_code,
            supplier_id=supplier.id,
            component_id=component.id,
        )
        session.add(lot)
        await session.flush()

    case_code = f"LOT-NEW-{uuid.uuid4().hex.upper()}"
    case = DefectCase(
        case_code=case_code,
        supplier_id=supplier.id,
        component_id=component.id,
        lot_id=lot.id,
        symptoms=payload.symptoms,
        description=payload.description,
        severity=payload.severity,
        status="OPEN",
        root_cause_status="unknown",
    )
    session.add(case)
    await session.flush()
    session.add(
        AuditEvent(
            case_id=case.id,
            actor="system",
            event_type="case_created",
            detail=f"Created {case.case_code}",
        )
    )
    await session.commit()
    return await load_case(session, case.id)


@router.get("/cases/{case_id}", response_model=CaseOut)
async def get_case(case_id: str, session: AsyncSession = Depends(get_session)):
    return await load_case(session, case_id)


@router.post(
    "/demo/seed",
    response_model=dict,
    summary="Seed canonical DB records matching the Hindsight POC cases",
)
async def seed_demo_cases(session: AsyncSession = Depends(get_session)):
    seed = [
        {
            "case_code": "LOT-POC-001",
            "supplier_code": "SUP-A",
            "supplier_name": "Supplier A",
            "lot_code": "A101",
            "symptoms": "Intermittent open-circuit readings during vibration testing.",
            "description": "BMS connector underperforms during vibration test.",
            "severity": "high",
            "status": "VERIFIED",
            "root_cause_status": "confirmed",
            "root_cause": "Insufficient crimp height.",
            "action": "Recalibrate the crimp tool and add a crimp-height sampling check.",
            "outcome": "effective",
        },
        {
            "case_code": "LOT-POC-002",
            "supplier_code": "SUP-A",
            "supplier_name": "Supplier A",
            "lot_code": "A115",
            "symptoms": "Intermittent open-circuit readings during vibration testing.",
            "description": "Failure recurred after connector reseating and rework.",
            "severity": "high",
            "status": "INVESTIGATING",
            "root_cause_status": "unknown",
            "root_cause": None,
            "action": "Connector reseating and rework.",
            "outcome": "ineffective",
        },
        {
            "case_code": "LOT-POC-003",
            "supplier_code": "SUP-B",
            "supplier_name": "Supplier B",
            "lot_code": "B204",
            "symptoms": "Intermittent open-circuit readings during vibration testing.",
            "description": "Terminal plating discontinuity caused contact surface corrosion.",
            "severity": "high",
            "status": "VERIFIED",
            "root_cause_status": "confirmed",
            "root_cause": "Localized terminal plating discontinuity causing contact surface corrosion.",
            "action": "Reject affected terminal lot and tighten incoming plating-continuity inspection.",
            "outcome": "effective",
        },
    ]
    created = 0
    for item in seed:
        existing = await session.execute(
            select(DefectCase).where(DefectCase.case_code == item["case_code"])
        )
        if existing.scalar_one_or_none():
            continue

        supplier_result = await session.execute(
            select(Supplier).where(Supplier.code == item["supplier_code"])
        )
        supplier = supplier_result.scalar_one_or_none()
        if supplier is None:
            supplier = Supplier(code=item["supplier_code"], name=item["supplier_name"])
            session.add(supplier)
            await session.flush()

        component_result = await session.execute(
            select(Component).where(Component.code == "BMS-CONN")
        )
        component = component_result.scalar_one_or_none()
        if component is None:
            component = Component(code="BMS-CONN", name="BMS Connector")
            session.add(component)
            await session.flush()

        lot_result = await session.execute(
            select(ProductionLot).where(
                ProductionLot.code == item["lot_code"],
                ProductionLot.supplier_id == supplier.id,
                ProductionLot.component_id == component.id,
            )
        )
        lot = lot_result.scalar_one_or_none()
        if lot is None:
            lot = ProductionLot(
                code=item["lot_code"],
                supplier_id=supplier.id,
                component_id=component.id,
            )
            session.add(lot)
            await session.flush()

        case = DefectCase(
            case_code=item["case_code"],
            supplier_id=supplier.id,
            component_id=component.id,
            lot_id=lot.id,
            symptoms=item["symptoms"],
            description=item["description"],
            severity=item["severity"],
            status=item["status"],
            root_cause_status=item["root_cause_status"],
            root_cause=item["root_cause"],
        )
        session.add(case)
        await session.flush()
        action = CorrectiveAction(
            case_id=case.id,
            description=item["action"],
            outcome=item["outcome"],
        )
        session.add(action)
        session.add(
            AuditEvent(
                case_id=case.id,
                actor="demo-seeder",
                event_type="demo_case_seeded",
                detail="Synthetic POC case. Not real manufacturing data.",
            )
        )
        created += 1

    await session.commit()
    return {
        "created": created,
        "total_seed_cases": len(seed),
        "note": "Synthetic canonical records only. This endpoint does not write to Hindsight.",
    }


@router.post("/cases/{case_id}/investigate", response_model=InvestigationOut)
async def investigate_case(
    case_id: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    case = await load_case(session, case_id)
    if case.status == "VERIFIED":
        raise HTTPException(
            status_code=409,
            detail="This case is verified. Create a new linked investigation instead of reopening it.",
        )
    hindsight: HindsightService | None = getattr(request.app.state, "hindsight", None)
    if hindsight is None:
        raise HTTPException(
            status_code=503,
            detail="Hindsight is not configured. Set HINDSIGHT_API_KEY in the backend environment.",
        )

    case.status = "INVESTIGATING"
    query = (
        f"Find historical manufacturing investigations relevant to {case.symptoms}. "
        f"Current component: {case.component.name}; supplier: {case.supplier.name}; "
        f"lot: {case.lot.code}. Return canonical case codes and distinguish confirmed "
        "root causes, ineffective actions and unresolved investigations."
    )
    try:
        hits = await hindsight.recall(query)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Hindsight Recall failed: {type(exc).__name__}"
        ) from exc

    recalled_codes = sorted(
        {code for hit in hits for code in hit.case_codes if CODE_RE.match(code)}
    )
    historical_cases: list[DefectCase] = []
    if recalled_codes:
        result = await session.execute(
            case_query().where(DefectCase.case_code.in_(recalled_codes))
        )
        historical_cases = result.scalars().unique().all()

    validated_codes = {item.case_code for item in historical_cases}
    unlinked_codes = sorted(set(recalled_codes) - validated_codes)

    # Include current case in the canonical evidence packet, but don't list it as history.
    all_cases = [case] + [
        item for item in historical_cases if item.id != case.id
    ]
    context = build_investigation_context(case, hits, all_cases)

    try:
        answer = await hindsight.reflect(context.prompt)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Hindsight Reflect failed: {type(exc).__name__}"
        ) from exc

    mentioned_codes = set(re.findall(r"\bLOT-[A-Z0-9]{2,}-[A-Z0-9]{3,}(?:-[A-Z0-9]{3,})*\b", answer))
    allowed_codes = {case.case_code for case in all_cases}
    citation_warnings = sorted(mentioned_codes - allowed_codes)

    investigation = Investigation(
        case_id=case.id,
        query=query,
        result_text=answer,
        memory_hit_count=len(hits),
        evidence_case_codes=context.evidence_case_codes,
        unlinked_case_codes=unlinked_codes,
    )
    session.add(investigation)
    session.add(
        AuditEvent(
            case_id=case.id,
            actor="agent",
            event_type="investigation_generated",
            detail=f"Recall hits={len(hits)}; validated history={len(context.evidence_case_codes)}",
        )
    )
    await session.commit()

    return InvestigationOut(
        id=investigation.id,
        case_id=case.id,
        query=query,
        result_text=answer,
        memory_hit_count=len(hits),
        evidence_cases=[
            to_historical(item)
            for item in historical_cases
            if item.id != case.id
        ],
        unlinked_case_codes=unlinked_codes,
        citation_warnings=citation_warnings,
        created_at=investigation.created_at,
    )


@router.post(
    "/cases/{case_id}/actions",
    response_model=ActionOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_action(
    case_id: str,
    payload: ActionCreate,
    session: AsyncSession = Depends(get_session),
):
    case = await load_case(session, case_id)
    if case.status == "VERIFIED":
        raise HTTPException(status_code=409, detail="Verified cases cannot accept new actions")
    action = CorrectiveAction(case_id=case.id, description=payload.description)
    case.status = "AWAITING_QA"
    session.add(action)
    session.add(
        AuditEvent(
            case_id=case.id,
            actor="engineer",
            event_type="corrective_action_proposed",
            detail=payload.description,
        )
    )
    await session.commit()
    await session.refresh(action)
    return action


@router.post(
    "/cases/{case_id}/memory-sync/retry",
    response_model=dict,
    summary="Retry a failed verified-outcome memory write",
)
async def retry_memory_sync(
    case_id: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    case = await load_case(session, case_id)
    hindsight: HindsightService | None = getattr(request.app.state, "hindsight", None)
    if hindsight is None:
        raise HTTPException(status_code=503, detail="Hindsight is not configured")

    sync_result = await session.execute(
        select(MemorySync)
        .where(MemorySync.case_id == case.id, MemorySync.status.in_(["failed", "pending"]))
        .order_by(MemorySync.created_at.desc())
        .limit(1)
    )
    sync = sync_result.scalar_one_or_none()
    if sync is None:
        raise HTTPException(status_code=404, detail="No failed or pending memory sync found")

    verification_result = await session.execute(
        select(Verification).where(Verification.id == sync.verification_id)
    )
    verification = verification_result.scalar_one_or_none()
    if verification is None:
        raise HTTPException(status_code=409, detail="Verification record is missing")

    action_result = await session.execute(
        select(CorrectiveAction).where(CorrectiveAction.id == verification.action_id)
    )
    action = action_result.scalar_one_or_none()
    if action is None:
        raise HTTPException(status_code=409, detail="Corrective action record is missing")

    memory_content = (
        f"Canonical case ID: {case.case_code}. "
        f"Supplier: {case.supplier.name} ({case.supplier.code}). "
        f"Component: {case.component.name} ({case.component.code}). "
        f"Lot: {case.lot.code}. Symptoms: {case.symptoms}. "
        f"Investigation: {case.description}. "
        f"Root-cause status: {case.root_cause_status}. "
        f"Confirmed root cause: {case.root_cause or 'not confirmed'}. "
        f"Corrective action: {action.description}. "
        f"Action outcome: {action.outcome}. "
        f"QA verifier: {verification.verified_by}. "
        f"QA notes: {verification.notes}. "
        "This is a QA-verified LotLens investigation outcome."
    )
    try:
        await hindsight.retain_verified_outcome(
            case_code=case.case_code,
            content=memory_content,
            verification_id=verification.id,
        )
        sync.status = "synced"
        sync.error_message = None
    except Exception as exc:
        sync.status = "failed"
        sync.error_message = type(exc).__name__
        await session.commit()
        raise HTTPException(
            status_code=502,
            detail="Hindsight memory retry failed. The QA verification remains saved.",
        ) from exc

    await session.commit()
    return {"case_code": case.case_code, "memory_sync_status": sync.status}


@router.post(
    "/cases/{case_id}/verify",
    response_model=VerificationOut,
    status_code=status.HTTP_201_CREATED,
)
async def verify_action(
    case_id: str,
    payload: VerificationCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    case = await load_case(session, case_id)
    action_result = await session.execute(
        select(CorrectiveAction).where(
            CorrectiveAction.id == payload.action_id,
            CorrectiveAction.case_id == case.id,
        )
    )
    action = action_result.scalar_one_or_none()
    if action is None:
        raise HTTPException(status_code=404, detail="Corrective action not found for this case")
    if case.status == "VERIFIED":
        raise HTTPException(status_code=409, detail="Case is already verified")

    action.outcome = payload.action_outcome
    case.root_cause_status = payload.root_cause_status
    case.root_cause = (
        payload.confirmed_root_cause
        if payload.root_cause_status == "confirmed"
        else None
    )
    case.status = (
        "VERIFIED"
        if payload.action_outcome == "effective" and payload.root_cause_status == "confirmed"
        else "INVESTIGATING"
    )

    verification = Verification(
        case_id=case.id,
        action_id=action.id,
        action_outcome=payload.action_outcome,
        root_cause_status=payload.root_cause_status,
        confirmed_root_cause=payload.confirmed_root_cause,
        notes=payload.notes,
        verified_by=payload.verified_by,
    )
    session.add(verification)
    await session.flush()

    sync = MemorySync(verification_id=verification.id, case_id=case.id, status="pending")
    session.add(sync)
    session.add(
        AuditEvent(
            case_id=case.id,
            actor=payload.verified_by,
            event_type="qa_verified",
            detail=(
                f"Action outcome={payload.action_outcome}; "
                f"root cause status={payload.root_cause_status}"
            ),
        )
    )
    await session.commit()
    await session.refresh(verification)
    await session.refresh(sync)

    hindsight: HindsightService | None = getattr(request.app.state, "hindsight", None)
    sync_error = None
    if hindsight is None:
        sync.status = "failed"
        sync.error_message = "Hindsight is not configured"
        sync_error = sync.error_message
    else:
        memory_content = (
            f"Canonical case ID: {case.case_code}. "
            f"Supplier: {case.supplier.name} ({case.supplier.code}). "
            f"Component: {case.component.name} ({case.component.code}). "
            f"Lot: {case.lot.code}. Symptoms: {case.symptoms}. "
            f"Investigation: {case.description}. "
            f"Root-cause status: {case.root_cause_status}. "
            f"Confirmed root cause: {case.root_cause or 'not confirmed'}. "
            f"Corrective action: {action.description}. "
            f"Action outcome: {action.outcome}. "
            f"QA verifier: {verification.verified_by}. "
            f"QA notes: {verification.notes}. "
            "This is a QA-verified LotLens investigation outcome."
        )
        try:
            await hindsight.retain_verified_outcome(
                case_code=case.case_code,
                content=memory_content,
                verification_id=verification.id,
            )
            sync.status = "synced"
        except Exception as exc:
            sync.status = "failed"
            sync.error_message = type(exc).__name__
            sync_error = (
                "The verification was saved, but Hindsight memory sync failed. "
                "Retry after checking the Hindsight service."
            )
    await session.commit()

    return VerificationOut(
        id=verification.id,
        case_id=case.id,
        action_id=action.id,
        action_outcome=verification.action_outcome,
        root_cause_status=verification.root_cause_status,
        confirmed_root_cause=verification.confirmed_root_cause,
        verified_by=verification.verified_by,
        memory_sync_status=sync.status,
        memory_sync_error=sync_error,
        created_at=verification.created_at,
    )
