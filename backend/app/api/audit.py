"""Audit-trail endpoint.

The audit log is sensitive (it lists who did what to whose data), so reading it
is restricted to data stewards and admins. It is append-only — there is
deliberately no endpoint to edit or delete an event.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import AuditEventRead
from app.core.security import Principal, require_roles
from app.db.session import get_db
from app.domain.enums import Role
from app.domain.models import AuditEvent

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEventRead])
def list_audit_events(
    db: Session = Depends(get_db),
    _: Principal = Depends(require_roles(Role.DATA_STEWARD)),
) -> list[AuditEvent]:
    return list(
        db.scalars(
            select(AuditEvent).order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        )
    )
