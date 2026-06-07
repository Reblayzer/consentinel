"""Audit-trail helper.

Every governance action (filing, approving, completing a request; attaching a
usage agreement) records an :class:`~app.domain.models.AuditEvent`. The caller
is responsible for committing the surrounding transaction, so the audit record
and the change it describes commit atomically together.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.domain.models import AuditEvent


def record_audit(
    db: Session,
    *,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    detail: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=json.dumps(detail or {}),
    )
    db.add(event)
    return event
