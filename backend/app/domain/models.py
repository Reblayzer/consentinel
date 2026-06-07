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
from app.domain.enums import PIICategory


def _utcnow() -> datetime:
    return datetime.now(UTC)


# Store enums as their string *values* (e.g. "national_id") in a portable VARCHAR
# column — works identically on SQLite and Postgres and matches the JSON contract.
_pii_enum = SAEnum(
    PIICategory,
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
    pii_category: Mapped[PIICategory] = mapped_column(_pii_enum, default=PIICategory.NONE)
    confidence: Mapped[float] = mapped_column(default=0.0)
    rationale: Mapped[str] = mapped_column(Text, default="")

    dataset: Mapped[Dataset] = relationship(back_populates="fields")
