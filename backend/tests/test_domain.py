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
