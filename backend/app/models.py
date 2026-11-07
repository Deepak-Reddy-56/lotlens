from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    cases: Mapped[list["DefectCase"]] = relationship(back_populates="supplier")


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    cases: Mapped[list["DefectCase"]] = relationship(back_populates="component")


class ProductionLot(Base):
    __tablename__ = "production_lots"
    __table_args__ = (UniqueConstraint("code", "supplier_id", "component_id", name="uq_lot_supplier_component"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(80), index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"))
    cases: Mapped[list["DefectCase"]] = relationship(back_populates="lot")


class DefectCase(Base):
    __tablename__ = "defect_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_code: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"))
    lot_id: Mapped[int] = mapped_column(ForeignKey("production_lots.id"))
    symptoms: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default="OPEN", index=True)
    root_cause_status: Mapped[str] = mapped_column(String(24), default="unknown")
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    supplier: Mapped[Supplier] = relationship(back_populates="cases")
    component: Mapped[Component] = relationship(back_populates="cases")
    lot: Mapped[ProductionLot] = relationship(back_populates="cases")
    actions: Mapped[list["CorrectiveAction"]] = relationship(
        back_populates="case", cascade="all, delete-orphan",\n        order_by="(CorrectiveAction.created_at, CorrectiveAction.id)"\n    )\n    investigations: Mapped[list["Investigation"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    verifications: Mapped[list["Verification"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("defect_cases.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    outcome: Mapped[str] = mapped_column(String(24), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    case: Mapped[DefectCase] = relationship(back_populates="actions")


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("defect_cases.id"), index=True)
    query: Mapped[str] = mapped_column(Text)
    result_text: Mapped[str] = mapped_column(Text)
    memory_hit_count: Mapped[int] = mapped_column(Integer, default=0)
    evidence_case_codes: Mapped[list[str]] = mapped_column(JSON, default=list)
    unlinked_case_codes: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    case: Mapped[DefectCase] = relationship(back_populates="investigations")


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("defect_cases.id"), index=True)
    action_id: Mapped[str] = mapped_column(ForeignKey("corrective_actions.id"))
    action_outcome: Mapped[str] = mapped_column(String(24))
    root_cause_status: Mapped[str] = mapped_column(String(24), default="unknown")
    confirmed_root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    verified_by: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    case: Mapped[DefectCase] = relationship(back_populates="verifications")


class MemorySync(Base):
    __tablename__ = "memory_syncs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    verification_id: Mapped[str] = mapped_column(
        ForeignKey("verifications.id"), unique=True
    )
    case_id: Mapped[str] = mapped_column(ForeignKey("defect_cases.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(ForeignKey("defect_cases.id"), index=True)
    actor: Mapped[str] = mapped_column(String(120))
    event_type: Mapped[str] = mapped_column(String(60))
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
