"""Pydantic request/response models — the API's JSON contract."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import PIICategory


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
