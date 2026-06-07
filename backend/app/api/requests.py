"""Compliance-request endpoints: right-to-be-forgotten and access requests.

Lifecycle:

    pending ──approve──► approved ──complete──► completed
       │
       └──reject──► rejected   (terminal)

Any authenticated principal may file a request (a data subject acting for
themselves). Only data stewards (or admins) may approve, reject, or complete
one. Every transition is written to the audit trail.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import (
    ComplianceRequestCreate,
    ComplianceRequestDecision,
    ComplianceRequestRead,
)
from app.core.security import Principal, get_principal, require_roles
from app.db.session import get_db
from app.domain.enums import RequestStatus, Role
from app.domain.models import ComplianceRequest, Dataset
from app.services.audit import record_audit

router = APIRouter(prefix="/requests", tags=["compliance requests"])


def _get_request_or_404(db: Session, request_id: int) -> ComplianceRequest:
    request = db.get(ComplianceRequest, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="request not found")
    return request


def _require_status(request: ComplianceRequest, expected: RequestStatus) -> None:
    if request.status != expected:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"request is '{request.status.value}', expected '{expected.value}'",
        )


@router.post("", response_model=ComplianceRequestRead, status_code=status.HTTP_201_CREATED)
def file_request(
    payload: ComplianceRequestCreate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_principal),
) -> ComplianceRequest:
    if payload.dataset_id is not None and db.get(Dataset, payload.dataset_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dataset not found")

    request = ComplianceRequest(
        request_type=payload.request_type,
        subject_ref=payload.subject_ref,
        dataset_id=payload.dataset_id,
        reason=payload.reason,
        requested_by=principal.actor,
    )
    db.add(request)
    db.flush()  # assign an id before auditing
    record_audit(
        db,
        actor=principal.actor,
        action="request.filed",
        entity_type="compliance_request",
        entity_id=request.id,
        detail={"type": request.request_type.value, "subject_ref": request.subject_ref},
    )
    db.commit()
    db.refresh(request)
    return request


@router.get("", response_model=list[ComplianceRequestRead])
def list_requests(
    db: Session = Depends(get_db),
    status_filter: RequestStatus | None = Query(default=None, alias="status"),
) -> list[ComplianceRequest]:
    stmt = select(ComplianceRequest).order_by(ComplianceRequest.created_at.desc())
    if status_filter is not None:
        stmt = stmt.where(ComplianceRequest.status == status_filter)
    return list(db.scalars(stmt))


@router.get("/{request_id}", response_model=ComplianceRequestRead)
def get_request(request_id: int, db: Session = Depends(get_db)) -> ComplianceRequest:
    return _get_request_or_404(db, request_id)


@router.post("/{request_id}/approve", response_model=ComplianceRequestRead)
def approve_request(
    request_id: int,
    payload: ComplianceRequestDecision,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_roles(Role.DATA_STEWARD)),
) -> ComplianceRequest:
    request = _get_request_or_404(db, request_id)
    _require_status(request, RequestStatus.PENDING)
    request.status = RequestStatus.APPROVED
    request.decided_by = principal.actor
    request.decision_note = payload.note
    record_audit(
        db,
        actor=principal.actor,
        action="request.approved",
        entity_type="compliance_request",
        entity_id=request.id,
        detail={"note": payload.note},
    )
    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/reject", response_model=ComplianceRequestRead)
def reject_request(
    request_id: int,
    payload: ComplianceRequestDecision,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_roles(Role.DATA_STEWARD)),
) -> ComplianceRequest:
    request = _get_request_or_404(db, request_id)
    _require_status(request, RequestStatus.PENDING)
    request.status = RequestStatus.REJECTED
    request.decided_by = principal.actor
    request.decision_note = payload.note
    request.resolved_at = datetime.now(UTC)
    record_audit(
        db,
        actor=principal.actor,
        action="request.rejected",
        entity_type="compliance_request",
        entity_id=request.id,
        detail={"note": payload.note},
    )
    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/complete", response_model=ComplianceRequestRead)
def complete_request(
    request_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_roles(Role.DATA_STEWARD)),
) -> ComplianceRequest:
    """Mark an approved request as carried out (e.g. erasure executed)."""
    request = _get_request_or_404(db, request_id)
    _require_status(request, RequestStatus.APPROVED)
    request.status = RequestStatus.COMPLETED
    request.resolved_at = datetime.now(UTC)
    record_audit(
        db,
        actor=principal.actor,
        action="request.completed",
        entity_type="compliance_request",
        entity_id=request.id,
    )
    db.commit()
    db.refresh(request)
    return request
