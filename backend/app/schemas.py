from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Severity = Literal["low", "medium", "high", "critical"]
CaseStatus = Literal["OPEN", "INVESTIGATING", "AWAITING_QA", "VERIFIED"]
RootCauseStatus = Literal["confirmed", "suspected", "unknown", "disputed"]
ActionOutcome = Literal["pending", "effective", "ineffective", "inconclusive"]


class SupplierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str


class ComponentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str


class LotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str


class CaseCreate(BaseModel):
    supplier_code: str = Field(min_length=2, max_length=40)
    supplier_name: str = Field(min_length=2, max_length=160)
    component_code: str = Field(min_length=2, max_length=60)
    component_name: str = Field(min_length=2, max_length=160)
    lot_code: str = Field(min_length=2, max_length=80)
    symptoms: str = Field(min_length=8, max_length=4000)
    description: str = Field(default="", max_length=8000)
    severity: Severity = "medium"


class ActionCreate(BaseModel):
    description: str = Field(min_length=8, max_length=4000)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 8:
            raise ValueError("description must contain at least 8 non-whitespace characters")
        return value


class ActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    description: str
    outcome: str
    created_at: datetime


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_code: str
    supplier: SupplierOut
    component: ComponentOut
    lot: LotOut
    symptoms: str
    description: str
    severity: str
    status: str
    root_cause_status: str
    root_cause: str | None
    created_at: datetime
    actions: list[ActionOut] = Field(default_factory=list)


class VerificationCreate(BaseModel):
    action_id: str
    action_outcome: Literal["effective", "ineffective", "inconclusive"]
    root_cause_status: RootCauseStatus = "unknown"
    confirmed_root_cause: str | None = Field(default=None, max_length=4000)
    notes: str = Field(default="", max_length=6000)
    verified_by: str = Field(min_length=2, max_length=120)

    @model_validator(mode="after")
    def require_confirmed_cause(self) -> "VerificationCreate":
        if self.confirmed_root_cause is not None:
            self.confirmed_root_cause = self.confirmed_root_cause.strip() or None
        if self.verified_by:
            self.verified_by = self.verified_by.strip()
        if self.root_cause_status == "confirmed" and not self.confirmed_root_cause:
            raise ValueError("confirmed_root_cause is required when status is confirmed")
        if not self.verified_by:
            raise ValueError("verified_by must contain a name")
        return self


class HistoricalCaseOut(BaseModel):
    case_code: str
    supplier_code: str
    supplier_name: str
    component_code: str
    component_name: str
    lot_code: str
    symptoms: str
    root_cause_status: str
    root_cause: str | None
    status: str
    actions: list[ActionOut] = Field(default_factory=list)


class InvestigationOut(BaseModel):
    id: str
    case_id: str
    query: str
    result_text: str
    memory_hit_count: int
    evidence_cases: list[HistoricalCaseOut]
    unlinked_case_codes: list[str]
    citation_warnings: list[str]
    created_at: datetime


class VerificationOut(BaseModel):
    id: str
    case_id: str
    action_id: str
    action_outcome: str
    root_cause_status: str
    confirmed_root_cause: str | None
    verified_by: str
    memory_sync_status: str
    memory_sync_error: str | None
    created_at: datetime


class HealthOut(BaseModel):
    status: str
    database: str
    hindsight_configured: bool
    bank_id: str
