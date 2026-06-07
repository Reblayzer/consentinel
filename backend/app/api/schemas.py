"""Pydantic request/response models — the API's JSON contract."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import LegalBasis, PIICategory, RequestStatus, RequestType


class FieldSample(BaseModel):
    """A source column plus a few example values, used to classify it."""

    name: str = Field(examples=["email"])
    sample_values: list[str] = Field(default_factory=list, examples=[["a@lego.dk", "b@lego.dk"]])


class DatasetCreate(BaseModel):
    """The manifest a data owner submits to register a dataset."""

    name: str = Field(examples=["crm.customers"])
    description: str = ""
    owner: str = Field(examples=["marketing-data-team"])
    source_system: str = Field(examples=["snowflake"])
    fields: list[FieldSample] = Field(default_factory=list)


class FieldRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    pii_category: PIICategory
    confidence: float
    rationale: str


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    owner: str
    source_system: str
    created_at: datetime
    contains_personal_data: bool
    fields: list[FieldRead]


# --- Usage agreements -------------------------------------------------------


class UsageAgreementCreate(BaseModel):
    purpose: str = Field(examples=["Customer marketing analytics"])
    legal_basis: LegalBasis = Field(examples=[LegalBasis.CONSENT])
    retention_days: int = Field(gt=0, examples=[365])


class UsageAgreementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    purpose: str
    legal_basis: LegalBasis
    retention_days: int
    created_at: datetime


# --- Compliance requests ----------------------------------------------------


class ComplianceRequestCreate(BaseModel):
    request_type: RequestType = Field(examples=[RequestType.ERASURE])
    subject_ref: str = Field(examples=["jens@lego.dk"])
    dataset_id: int | None = None
    reason: str = ""


class ComplianceRequestDecision(BaseModel):
    note: str = ""


class ComplianceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_type: RequestType
    subject_ref: str
    dataset_id: int | None
    reason: str
    status: RequestStatus
    requested_by: str
    decided_by: str | None
    decision_note: str | None
    created_at: datetime
    resolved_at: datetime | None


# --- Audit ------------------------------------------------------------------


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor: str
    action: str
    entity_type: str
    entity_id: int | None
    detail: str
    created_at: datetime
