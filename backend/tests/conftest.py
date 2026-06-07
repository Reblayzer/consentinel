"""Shared test fixtures.

Each test gets an isolated in-memory SQLite database wired into the app through
a ``get_db`` dependency override, so tests never touch a real database or each
other's state.
"""

import os

# Point the app at an in-memory DB *before* it is imported, so importing
# ``app.main`` (which creates tables on boot) never writes a stray .db file.
os.environ["CONSENTINEL_DATABASE_URL"] = "sqlite://"
os.environ["CONSENTINEL_ENVIRONMENT"] = "test"

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.domain.models  # noqa: E402,F401  (register models on Base.metadata)
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client() -> Iterator[TestClient]:
    # A single shared in-memory connection (StaticPool) keeps the schema alive
    # for the whole test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Iterator[object]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
