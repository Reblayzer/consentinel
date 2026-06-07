"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from app.api import datasets
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

    # Convenient for local dev: create tables on boot. The containerised stack
    # uses Alembic migrations instead (introduced in the infrastructure sprint).
    Base.metadata.create_all(bind=engine)

    app.include_router(datasets.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
