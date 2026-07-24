from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Convert Railway/Heroku-style postgres URL to async SQLAlchemy driver."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Discount Wheel"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://wheel:wheel@postgres:5432/discount_wheel"
    redis_url: str | None = "redis://redis:6379/0"

    telegram_bot_token: str = ""
    # Skip Telegram signature check only for local browser testing
    allow_dev_auth: bool = False

    # Campaign window (ISO datetime strings, optional)
    campaign_start: str | None = None
    campaign_end: str | None = None

    cors_origins: str = "*"

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_db_url(cls, value: str) -> str:
        return normalize_database_url(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
