from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.config import Settings
from app.models.user import Spin, User
from app.services.prizes import choose_prize, compute_spin_angle, generate_promo_code


def ensure_campaign_active(settings: Settings) -> None:
    now = datetime.now(timezone.utc)
    if settings.campaign_start:
        start = datetime.fromisoformat(settings.campaign_start)
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if now < start:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign has not started yet")
    if settings.campaign_end:
        end = datetime.fromisoformat(settings.campaign_end)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if now > end:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign has ended")


async def get_user_with_spin(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(
        select(User).options(selectinload(User.spin)).where(User.id == user_id)
    )
    user = result.scalar_one()
    return user


async def perform_spin(session: AsyncSession, user: User, settings: Settings) -> Spin:
    ensure_campaign_active(settings)

    fresh = await get_user_with_spin(session, user.id)
    if fresh.spin is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already spun")

    prize = choose_prize()
    promo = generate_promo_code(prize.discount, prize.promo_prefix)
    angle = compute_spin_angle(prize.discount)

    spin = Spin(
        user_id=fresh.id,
        discount=prize.discount,
        promo_code=promo,
        angle=angle,
    )
    session.add(spin)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already spun") from exc

    await session.refresh(spin)
    return spin
