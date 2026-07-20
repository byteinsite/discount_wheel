"""Telegram Mini App initData validation.

https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import Settings
from app.models.user import User

AUTH_MAX_AGE_SECONDS = 86400  # 24 hours


@dataclass(frozen=True)
class TelegramUser:
    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


def parse_and_validate_init_data(
    init_data: str,
    bot_token: str,
    *,
    max_age: int = AUTH_MAX_AGE_SECONDS,
) -> TelegramUser:
    if not init_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing initData")

    if not bot_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bot token not configured",
        )

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing hash")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated, received_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid initData signature")

    auth_date = int(parsed.get("auth_date", "0"))
    if max_age and abs(time.time() - auth_date) > max_age:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="initData expired")

    user_raw = parsed.get("user")
    if not user_raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing user in initData")

    try:
        user_data = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user payload") from exc

    return TelegramUser(
        id=int(user_data["id"]),
        username=user_data.get("username"),
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
    )


def parse_dev_init_data(init_data: str) -> TelegramUser:
    """Fallback for local UI testing without Telegram signature."""
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    user_raw = parsed.get("user")
    if user_raw:
        user_data = json.loads(user_raw)
        return TelegramUser(
            id=int(user_data["id"]),
            username=user_data.get("username"),
            first_name=user_data.get("first_name", "Dev"),
            last_name=user_data.get("last_name"),
        )
    return TelegramUser(id=1, username="dev", first_name="Dev", last_name="User")


async def get_or_create_user(session: AsyncSession, tg: TelegramUser) -> User:
    result = await session.execute(
        select(User).options(selectinload(User.spin)).where(User.telegram_id == tg.id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.username = tg.username
        user.first_name = tg.first_name
        user.last_name = tg.last_name
        await session.commit()
        await session.refresh(user, attribute_names=["spin"])
        return user

    user = User(
        telegram_id=tg.id,
        username=tg.username,
        first_name=tg.first_name,
        last_name=tg.last_name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user, attribute_names=["spin"])
    return user


def display_name(user: User) -> str:
    if user.first_name:
        parts = [user.first_name]
        if user.last_name:
            parts.append(user.last_name)
        return " ".join(parts)
    if user.username:
        return user.username
    return f"User {user.telegram_id}"


async def resolve_telegram_user(init_data: str, settings: Settings) -> TelegramUser:
    if settings.allow_dev_auth and (
        not settings.telegram_bot_token or init_data.startswith("dev=") or "hash=" not in init_data
    ):
        return parse_dev_init_data(init_data)
    return parse_and_validate_init_data(init_data, settings.telegram_bot_token)
