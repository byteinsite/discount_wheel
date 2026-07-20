from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import (
    display_name,
    get_or_create_user,
    resolve_telegram_user,
)
from app.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas import AuthRequest, AuthResponse, MeResponse, ResultResponse, SpinResponse
from app.services.spin import get_user_with_spin, perform_spin

router = APIRouter()


async def get_init_data(
    authorization: str | None = Header(default=None),
    x_telegram_init_data: str | None = Header(default=None, alias="X-Telegram-Init-Data"),
) -> str:
    if authorization and authorization.lower().startswith("tma "):
        return authorization[4:].strip()
    if x_telegram_init_data:
        return x_telegram_init_data
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


async def get_current_user(
    init_data: str = Depends(get_init_data),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    tg = await resolve_telegram_user(init_data, settings)
    return await get_or_create_user(session, tg)


@router.post("/auth", response_model=AuthResponse)
async def auth(
    body: AuthRequest,
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    tg = await resolve_telegram_user(body.init_data, settings)
    user = await get_or_create_user(session, tg)
    user = await get_user_with_spin(session, user.id)
    return AuthResponse(
        telegram_id=user.telegram_id,
        name=display_name(user),
        spinned=user.spin is not None,
    )


@router.get("/me", response_model=MeResponse)
async def me(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> MeResponse:
    user = await get_user_with_spin(session, user.id)
    return MeResponse(
        name=display_name(user),
        spinned=user.spin is not None,
        telegram_id=user.telegram_id,
    )


@router.post("/spin", response_model=SpinResponse)
async def spin(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SpinResponse:
    result = await perform_spin(session, user, settings)
    return SpinResponse(
        discount=result.discount,
        promo=result.promo_code,
        angle=result.angle,
    )


@router.get("/result", response_model=ResultResponse)
async def result(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ResultResponse:
    user = await get_user_with_spin(session, user.id)
    if user.spin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No spin yet")
    return ResultResponse(discount=user.spin.discount, promo=user.spin.promo_code)
