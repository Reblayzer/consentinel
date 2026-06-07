"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from app.api import agreements, audit, datasets, requests
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Data-governance & compliance portal — dataset manifests, automatic PII "
            "classification, and right-to-be-forgotten workflows."
        ),
    )

    # Convenient for local dev on SQLite: create tables on boot. The Postgres
    # (containerised) deployment owns its schema through Alembic migrations, so
    # we skip create_all there to keep a single source of schema truth.
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)

    app.include_router(datasets.router)
    app.include_router(agreements.router)
    app.include_router(requests.router)
    app.include_router(audit.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
