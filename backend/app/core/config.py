"""Application settings, loaded from environment variables (12-factor style).

Defaults target zero-setup local development: SQLite, no external services.
Override via ``CONSENTINEL_*`` env vars (or a ``.env`` file) — for example the
Docker stack sets ``CONSENTINEL_DATABASE_URL`` to a Postgres DSN.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CONSENTINEL_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "Consentinel"
    environment: str = "local"

    # SQLite keeps local dev and the test-suite dependency-free. Swap to
    # "postgresql+psycopg://user:pass@host/db" for the containerised stack.
    database_url: str = "sqlite:///./consentinel.db"

    # A field whose PII confidence meets this threshold is treated as personal data.
    pii_flag_threshold: float = 0.5


@lru_cache
def get_settings() -> Settings:
    return Settings()
