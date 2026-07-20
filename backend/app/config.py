from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()
