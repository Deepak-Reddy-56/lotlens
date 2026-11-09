from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.database import get_session
from app.models import Base
from app.routers.cases import router
from app.services.hindsight_service import MemoryHit


class FakeHindsight:
    """Deterministic Hindsight substitute; tests never call the real service."""

    def __init__(self) -> None:
        self.hits: list[MemoryHit] = []
        self.answer = "No additional historical evidence was found."
        self.recall_error: Exception | None = None
        self.reflect_error: Exception | None = None
        self.retain_error: Exception | None = None
        self.last_query: str | None = None
        self.last_prompt: str | None = None
        self.retain_calls: list[dict[str, str]] = []

    async def recall(self, query: str) -> list[MemoryHit]:
        self.last_query = query
        if self.recall_error:
            raise self.recall_error
        return self.hits

    async def reflect(self, query: str) -> str:
        self.last_prompt = query
        if self.reflect_error:
            raise self.reflect_error
        return self.answer

    async def retain_verified_outcome(
        self, *, case_code: str, content: str, verification_id: str
    ) -> None:
        self.retain_calls.append(
            {
                "case_code": case_code,
                "content": content,
                "verification_id": verification_id,
            }
        )
        if self.retain_error:
            raise self.retain_error


@pytest.fixture
def api_env(tmp_path: Path) -> Iterator[tuple[TestClient, FakeHindsight]]:
    """Fresh file-backed SQLite database and isolated FastAPI test application."""
    database_path = tmp_path / "lotlens-api-test.sqlite3"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )

    async def create_schema() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(create_schema())
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_session() -> AsyncGenerator:
        async with session_factory() as session:
            yield session

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = override_session
    hindsight = FakeHindsight()
    app.state.hindsight = hindsight

    try:
        with TestClient(app) as client:
            yield client, hindsight
    finally:
        asyncio.run(engine.dispose())


def seeded_cases(client: TestClient) -> dict[str, dict]:
    response = client.post("/api/v1/demo/seed")
    assert response.status_code == 200, response.text
    assert response.json()["created"] == 3
    rows = client.get("/api/v1/cases")
    assert rows.status_code == 200, rows.text
    return {row["case_code"]: row for row in rows.json()}


def verification_payload(
    action_id: str,
    *,
    outcome: str = "effective",
    root_status: str = "confirmed",
    root_cause: str | None = "Insufficient crimp height.",
) -> dict[str, str | None]:
    return {
        "action_id": action_id,
        "action_outcome": outcome,
        "root_cause_status": root_status,
        "confirmed_root_cause": root_cause if root_status == "confirmed" else None,
        "verified_by": "QA Engineer",
        "notes": "Controlled integration-test verification.",
    }


def test_create_case_persists_canonical_supplier_component_and_lot(api_env):
    client, _ = api_env
    payload = {
        "supplier_code": "SUP-T",
        "supplier_name": "Test Supplier",
        "component_code": "BMS-CTRL",
        "component_name": "BMS Controller",
        "lot_code": "T-001",
        "symptoms": "Intermittent voltage drop under load",
        "description": "Created by API integration test.",
        "severity": "high",
    }

    created = client.post("/api/v1/cases", json=payload)

    assert created.status_code == 201, created.text
    result = created.json()
    assert result["case_code"].startswith("LOT-NEW-")
    assert len(result["case_code"].removeprefix("LOT-NEW-")) == 32
    assert result["supplier"] == {"code": "SUP-T", "name": "Test Supplier"}
    assert result["component"] == {"code": "BMS-CTRL", "name": "BMS Controller"}
    assert result["lot"]["code"] == "T-001"
    assert result["status"] == "OPEN"

    fetched = client.get(f"/api/v1/cases/{result['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["case_code"] == result["case_code"]


def test_case_and_action_input_validation_returns_422(api_env):
    client, _ = api_env
    invalid_case = client.post(
        "/api/v1/cases",
        json={
            "supplier_code": "S",
            "supplier_name": "Supplier",
            "component_code": "C",
            "component_name": "Component",
            "lot_code": "L1",
            "symptoms": "short",
            "severity": "urgent",
        },
    )
    assert invalid_case.status_code == 422

    cases = seeded_cases(client)
    case_id = cases["LOT-POC-002"]["id"]
    invalid_action = client.post(
        f"/api/v1/cases/{case_id}/actions", json={"description": "       "}
    )
    assert invalid_action.status_code == 422


def test_action_creation_moves_case_to_awaiting_qa(api_env):
    client, _ = api_env
    cases = seeded_cases(client)
    case_id = cases["LOT-POC-002"]["id"]

    response = client.post(
        f"/api/v1/cases/{case_id}/actions",
        json={"description": "Inspect connector crimp-height samples."},
    )

    assert response.status_code == 201, response.text
    assert response.json()["case_id"] == case_id
    assert response.json()["outcome"] == "pending"
    assert client.get(f"/api/v1/cases/{case_id}").json()["status"] == "AWAITING_QA"


def test_verified_case_rejects_new_action_and_investigation(api_env):
    client, _ = api_env
    cases = seeded_cases(client)
    case_id = cases["LOT-POC-001"]["id"]

    action = client.post(
        f"/api/v1/cases/{case_id}/actions",
        json={"description": "Attempt to change a verified case."},
    )
    investigation = client.post(f"/api/v1/cases/{case_id}/investigate")

    assert action.status_code == 409
    assert investigation.status_code == 409


def test_verification_cannot_use_an_action_from_another_case(api_env):
    client, _ = api_env
    cases = seeded_cases(client)
    source_case = cases["LOT-POC-001"]
    target_case = cases["LOT-POC-002"]
    foreign_action_id = source_case["actions"][0]["id"]

    response = client.post(
        f"/api/v1/cases/{target_case['id']}/verify",
        json=verification_payload(foreign_action_id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Corrective action not found for this case"


def test_effective_action_and_confirmed_cause_verifies_case_and_retains_memory(api_env):
    client, hindsight = api_env
    cases = seeded_cases(client)
    case_id = cases["LOT-POC-002"]["id"]
    action = client.post(
        f"/api/v1/cases/{case_id}/actions",
        json={"description": "Recalibrate crimp tool and measure crimp height."},
    )
    assert action.status_code == 201

    response = client.post(
        f"/api/v1/cases/{case_id}/verify",
        json=verification_payload(action.json()["id"]),
    )

    assert response.status_code == 201, response.text
    result = response.json()
    assert result["action_outcome"] == "effective"
    assert result["root_cause_status"] == "confirmed"
    assert result["memory_sync_status"] == "synced"
    assert result["memory_sync_error"] is None
    assert len(hindsight.retain_calls) == 1
    assert hindsight.retain_calls[0]["case_code"] == "LOT-POC-002"
    assert "Insufficient crimp height." in hindsight.retain_calls[0]["content"]

    saved_case = client.get(f"/api/v1/cases/{case_id}").json()
    assert saved_case["status"] == "VERIFIED"
    assert saved_case["root_cause"] == "Insufficient crimp height."


@pytest.mark.parametrize(
    ("outcome", "root_status"),
    [
        ("ineffective", "unknown"),
        ("inconclusive", "suspected"),
        ("effective", "unknown"),
        ("effective", "disputed"),
    ],
)
def test_non_confirming_qa_results_do_not_verify_case(api_env, outcome, root_status):
    client, _ = api_env
    cases = seeded_cases(client)
    case_id = cases["LOT-POC-002"]["id"]
    action_id = cases["LOT-POC-002"]["actions"][0]["id"]

    response = client.post(
        f"/api/v1/cases/{case_id}/verify",
        json=verification_payload(
            action_id,
            outcome=outcome,
            root_status=root_status,
            root_cause=None,
        ),
    )

    assert response.status_code == 201, response.text
    assert response.json()["root_cause_status"] == root_status
    saved_case = client.get(f"/api/v1/cases/{case_id}").json()
    assert saved_case["status"] == "INVESTIGATING"
    assert saved_case["root_cause"] is None


def test_failed_memory_retain_preserves_qa_and_retry_marks_sync_complete(api_env):
    client, hindsight = api_env
    cases = seeded_cases(client)
    case_id = cases["LOT-POC-002"]["id"]
    action_id = cases["LOT-POC-002"]["actions"][0]["id"]
    hindsight.retain_error = RuntimeError("simulated Hindsight outage")

    verification = client.post(
        f"/api/v1/cases/{case_id}/verify",
        json=verification_payload(action_id),
    )

    assert verification.status_code == 201, verification.text
    assert verification.json()["memory_sync_status"] == "failed"
    assert "Hindsight memory sync failed" in verification.json()["memory_sync_error"]
    assert client.get(f"/api/v1/cases/{case_id}").json()["status"] == "VERIFIED"
    assert len(hindsight.retain_calls) == 1

    hindsight.retain_error = None
    retry = client.post(f"/api/v1/cases/{case_id}/memory-sync/retry")

    assert retry.status_code == 200, retry.text
    assert retry.json() == {
        "case_code": "LOT-POC-002",
        "memory_sync_status": "synced",
    }
    assert len(hindsight.retain_calls) == 2


def test_investigation_uses_only_canonical_recalled_cases_and_warns_on_unknown_ids(api_env):
    client, hindsight = api_env
    cases = seeded_cases(client)
    current_case_id = cases["LOT-POC-002"]["id"]
    hindsight.hits = [
        MemoryHit(
            text="Relevant cases LOT-POC-001, LOT-POC-003 and LOT-POC-999.",
            memory_type="world",
            case_codes=["LOT-POC-001", "LOT-POC-003", "LOT-POC-999"],
        )
    ]
    hindsight.answer = (
        "Compare LOT-POC-001 and LOT-POC-003. "
        "An unsupported record LOT-POC-777 was also mentioned."
    )

    response = client.post(f"/api/v1/cases/{current_case_id}/investigate")

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["memory_hit_count"] == 1
    assert {case["case_code"] for case in result["evidence_cases"]} == {
        "LOT-POC-001",
        "LOT-POC-003",
    }
    assert result["unlinked_case_codes"] == ["LOT-POC-999"]
    assert result["citation_warnings"] == ["LOT-POC-777"]
    assert "do not cite as evidence" in hindsight.last_prompt.lower()
    assert client.get(f"/api/v1/cases/{current_case_id}").json()["status"] == "INVESTIGATING"


def test_investigation_returns_503_when_hindsight_is_not_configured(api_env):
    client, _ = api_env
    cases = seeded_cases(client)
    client.app.state.hindsight = None

    response = client.post(
        f"/api/v1/cases/{cases['LOT-POC-002']['id']}/investigate"
    )

    assert response.status_code == 503
    assert "Hindsight is not configured" in response.json()["detail"]


def test_recall_failure_returns_502_without_claiming_investigation_success(api_env):
    client, hindsight = api_env
    cases = seeded_cases(client)
    hindsight.recall_error = TimeoutError("simulated timeout")

    response = client.post(
        f"/api/v1/cases/{cases['LOT-POC-002']['id']}/investigate"
    )

    assert response.status_code == 502
    assert "Hindsight Recall failed: TimeoutError" in response.json()["detail"]


def test_reflect_failure_returns_502_and_does_not_create_investigation_response(api_env):
    client, hindsight = api_env
    cases = seeded_cases(client)
    hindsight.reflect_error = RuntimeError("simulated Reflect error")

    response = client.post(
        f"/api/v1/cases/{cases['LOT-POC-002']['id']}/investigate"
    )

    assert response.status_code == 502
    assert "Hindsight Reflect failed: RuntimeError" in response.json()["detail"]


def test_retry_returns_404_when_no_pending_or_failed_sync_exists(api_env):
    client, _ = api_env
    cases = seeded_cases(client)

    response = client.post(
        f"/api/v1/cases/{cases['LOT-POC-002']['id']}/memory-sync/retry"
    )

    assert response.status_code == 404
