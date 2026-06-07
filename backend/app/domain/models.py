"""SQLAlchemy ORM models.

Sprint 1 introduces the dataset *manifest* (``Dataset``) and its classified
columns (``DataField``). Later sprints add usage agreements, governance roles,
and compliance requests against these tables.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import LegalBasis, PIICategory, RequestStatus, RequestType


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _str_enum(enum_cls: type) -> SAEnum:
    """Map a StrEnum to a portable VARCHAR storing its string *values*.

    Works identically on SQLite and Postgres and keeps stored values aligned
    with the JSON contract (e.g. "national_id" rather than "NATIONAL_ID").
    """
    return SAEnum(
        enum_cls,
        native_enum=False,
        values_callable=lambda enum: [member.value for member in enum],
    )


class Dataset(Base):
    """A registered dataset manifest submitted by a data owner."""

    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str] = mapped_column(String(200))
    source_system: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    fields: Mapped[list[DataField]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="DataField.id",
    )
    agreements: Mapped[list[UsageAgreement]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="UsageAgreement.id",
    )

    @property
    def contains_personal_data(self) -> bool:
        return any(field.pii_category != PIICategory.NONE for field in self.fields)


class DataField(Base):
    """A single column of a dataset, annotated with its PII classification."""

    __tablename__ = "data_fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    pii_category: Mapped[PIICategory] = mapped_column(
        _str_enum(PIICategory), default=PIICategory.NONE
    )
    confidence: Mapped[float] = mapped_column(default=0.0)
    rationale: Mapped[str] = mapped_column(Text, default="")

    dataset: Mapped[Dataset] = relationship(back_populates="fields")


class UsageAgreement(Base):
    """The lawful basis and retention attached to a dataset's use of personal data."""

    __tablename__ = "usage_agreements"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    purpose: Mapped[str] = mapped_column(Text)
    legal_basis: Mapped[LegalBasis] = mapped_column(_str_enum(LegalBasis))
    retention_days: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)

    dataset: Mapped[Dataset] = relationship(back_populates="agreements")


class ComplianceRequest(Base):
    """A data-subject request (right-to-be-forgotten or access) and its lifecycle."""

    __tablename__ = "compliance_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_type: Mapped[RequestType] = mapped_column(_str_enum(RequestType))
    subject_ref: Mapped[str] = mapped_column(String(200), index=True)
    # Null dataset_id means the request applies to all datasets holding the subject.
    dataset_id: Mapped[int | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[RequestStatus] = mapped_column(
        _str_enum(RequestStatus), default=RequestStatus.PENDING
    )
    requested_by: Mapped[str] = mapped_column(String(200))
    decided_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AuditEvent(Base):
    """An append-only record of a governance action. Never updated or deleted."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(200))
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[int | None] = mapped_column(nullable=True)
    detail: Mapped[str] = mapped_column(Text, default="{}")  # JSON-encoded
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)
