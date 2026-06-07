"""Dataset registration & lookup endpoints.

Registering a dataset runs every declared column through the PII classifier, so
the manifest is annotated with personal-data findings the moment it is created.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import DatasetCreate, DatasetRead
from app.db.session import get_db
from app.domain.models import DataField, Dataset
from app.pii.classifier import classify_field

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
def register_dataset(payload: DatasetCreate, db: Session = Depends(get_db)) -> Dataset:
    """Register a dataset manifest and auto-classify each field for PII."""
    dataset = Dataset(
        name=payload.name,
        description=payload.description,
        owner=payload.owner,
        source_system=payload.source_system,
    )
    for field in payload.fields:
        result = classify_field(field.name, field.sample_values)
        dataset.fields.append(
            DataField(
                name=field.name,
                pii_category=result.category,
                confidence=result.confidence,
                rationale=result.rationale,
            )
        )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetRead])
def list_datasets(db: Session = Depends(get_db)) -> list[Dataset]:
    return list(db.scalars(select(Dataset).order_by(Dataset.created_at.desc())))


@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dataset not found")
    return dataset
