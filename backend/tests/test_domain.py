from app.services.hindsight_service import CASE_CODE_PATTERN
from app.schemas import VerificationCreate


def test_case_code_pattern_extracts_only_supported_case_codes():
    text = "LOT-POC-001 and LOT-POC-003; ignore LOT-POC-2 and OTHER-001"
    assert CASE_CODE_PATTERN.findall(text) == ["LOT-POC-001", "LOT-POC-003"]


def test_verification_requires_root_cause_when_marked_confirmed():
    try:
        VerificationCreate(
            action_id="action-1",
            action_outcome="effective",
            root_cause_status="confirmed",
            verified_by="QA Engineer",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Confirmed root cause must be provided")


def test_verification_allows_unknown_root_cause():
    result = VerificationCreate(
        action_id="action-1",
        action_outcome="ineffective",
        root_cause_status="unknown",
        verified_by="QA Engineer",
    )
    assert result.confirmed_root_cause is None


def test_verification_rejects_whitespace_only_confirmed_root_cause():
    try:
        VerificationCreate(
            action_id="action-1",
            action_outcome="effective",
            root_cause_status="confirmed",
            confirmed_root_cause="   ",
            verified_by="QA Engineer",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Whitespace-only root cause must be rejected")


def test_verification_trims_confirmed_root_cause_and_verifier():
    result = VerificationCreate(
        action_id="action-1",
        action_outcome="effective",
        root_cause_status="confirmed",
        confirmed_root_cause="  Insufficient crimp height.  ",
        verified_by="  QA Engineer  ",
    )
    assert result.confirmed_root_cause == "Insufficient crimp height."
    assert result.verified_by == "QA Engineer"


def test_case_code_pattern_supports_new_uuid_case_codes():
    code = "LOT-NEW-0123456789ABCDEF0123456789ABCDEF"
    assert CASE_CODE_PATTERN.findall(code) == [code]


def test_case_code_pattern_rejects_short_or_non_lot_tokens():
    text = "LOT-POC-2 LOT-NEW-AB OTHER-001"
    assert CASE_CODE_PATTERN.findall(text) == []


def test_investigation_context_exposes_only_canonical_case_codes():
    from types import SimpleNamespace

    from app.services.hindsight_service import MemoryHit
    from app.services.investigation_service import build_investigation_context

    def make_case(code):
        return SimpleNamespace(
            case_code=code,
            supplier=SimpleNamespace(code="SUP-A", name="Supplier A"),
            component=SimpleNamespace(code="BMS-CONN", name="BMS Connector"),
            lot=SimpleNamespace(code="A101"),
            symptoms="Intermittent open circuit during vibration testing",
            description="Synthetic test fixture",
            severity="high",
            status="INVESTIGATING",
            root_cause_status="unknown",
            root_cause=None,
            actions=[],
        )

    current = make_case("LOT-NEW-0123456789ABCDEF0123456789ABCDEF")
    canonical = make_case("LOT-POC-001")
    hits = [
        MemoryHit(
            text="Historical case LOT-POC-001 and untrusted reference LOT-POC-999",
            memory_type="world",
            case_codes=["LOT-POC-001", "LOT-POC-999"],
        )
    ]

    context = build_investigation_context(current, hits, [current, canonical])

    assert context.evidence_case_codes == ["LOT-POC-001"]
    assert context.unlinked_case_codes == ["LOT-POC-999"]
    assert "LOT-POC-999" in context.prompt
    assert "do not cite as evidence" in context.prompt


def test_demo_seed_is_idempotent_and_backfills_qa_verifications():
    import asyncio

    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.models import Base, CorrectiveAction, DefectCase, Verification
    from app.routers.cases import seed_demo_cases

    async def scenario():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)

            session_factory = async_sessionmaker(engine, expire_on_commit=False)
            async with session_factory() as session:
                first = await seed_demo_cases(session)
                assert first["created"] == 3
                assert first["backfilled_verifications"] == 3

                case_result = await session.execute(
                    select(DefectCase).where(DefectCase.case_code == "LOT-POC-001")
                )
                case = case_result.scalar_one()
                verification_result = await session.execute(
                    select(Verification).where(Verification.case_id == case.id)
                )
                verification = verification_result.scalar_one()
                await session.delete(verification)
                await session.commit()

                second = await seed_demo_cases(session)
                assert second["created"] == 0
                assert second["backfilled_verifications"] == 1

                verification_rows = await session.execute(select(Verification))
                assert len(verification_rows.scalars().all()) == 3

                action_rows = await session.execute(select(CorrectiveAction))
                assert len(action_rows.scalars().all()) == 3

                third = await seed_demo_cases(session)
                assert third["created"] == 0
                assert third["backfilled_verifications"] == 0

                verification_rows = await session.execute(select(Verification))
                assert len(verification_rows.scalars().all()) == 3
        finally:
            await engine.dispose()

    asyncio.run(scenario())
