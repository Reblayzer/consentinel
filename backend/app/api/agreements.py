"""Usage-agreement endpoints — the lawful basis a dataset relies on.

A usage agreement records *why* a dataset may process personal data (its GDPR
Article 6 lawful basis) and how long it is retained. Only data owners (or admins)
may attach one, and doing so is recorded in the audit trail.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import UsageAgreementCreate, UsageAgreementRead
from app.core.security import Principal, require_roles
from app.db.session import get_db
from app.domain.enums import Role
from app.domain.models import Dataset, UsageAgreement
from app.services.audit import record_audit

router = APIRouter(prefix="/datasets/{dataset_id}/agreements", tags=["usage agreements"])


def _get_dataset_or_404(db: Session, dataset_id: int) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dataset not found")
    return dataset


@router.post("", response_model=UsageAgreementRead, status_code=status.HTTP_201_CREATED)
def add_agreement(
    dataset_id: int,
    payload: UsageAgreementCreate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_roles(Role.DATA_OWNER)),
) -> UsageAgreement:
    _get_dataset_or_404(db, dataset_id)
    agreement = UsageAgreement(
        dataset_id=dataset_id,
        purpose=payload.purpose,
        legal_basis=payload.legal_basis,
        retention_days=payload.retention_days,
    )
    db.add(agreement)
    record_audit(
        db,
        actor=principal.actor,
        action="usage_agreement.created",
        entity_type="dataset",
        entity_id=dataset_id,
        detail={
            "legal_basis": payload.legal_basis.value,
            "retention_days": payload.retention_days,
        },
    )
    db.commit()
    db.refresh(agreement)
    return agreement


@router.get("", response_model=list[UsageAgreementRead])
def list_agreements(dataset_id: int, db: Session = Depends(get_db)) -> list[UsageAgreement]:
    _get_dataset_or_404(db, dataset_id)
    return list(
        db.scalars(
            select(UsageAgreement)
            .where(UsageAgreement.dataset_id == dataset_id)
            .order_by(UsageAgreement.id)
        )
    )
