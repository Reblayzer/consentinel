"""Lightweight role-based access control.

The caller's identity and governance role are read from request headers
(``X-Actor`` / ``X-Role``). This is a deliberately small stand-in for real
authentication. A production deployment would derive the principal from an
OIDC / JWT token issued by the identity provider. Isolating it in one dependency
means swapping in real auth later touches only this module.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from app.domain.enums import Role


@dataclass(frozen=True)
class Principal:
    actor: str
    role: Role


def get_principal(
    x_actor: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
) -> Principal:
    """Resolve the calling principal, or raise 401 if it cannot be determined."""
    if not x_actor or not x_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing X-Actor / X-Role headers",
        )
    try:
        role = Role(x_role)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"unknown role '{x_role}'",
        ) from exc
    return Principal(actor=x_actor, role=role)


def require_roles(*allowed: Role):
    """Dependency factory: allow the request only for one of ``allowed`` roles.

    ``ADMIN`` is always permitted, so it never needs to be listed explicitly.
    """
    permitted = set(allowed) | {Role.ADMIN}

    def _dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.role not in permitted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"role '{principal.role.value}' is not permitted for this action",
            )
        return principal

    return _dependency
