from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    init_data: str = Field(..., alias="initData")

    model_config = {"populate_by_name": True}


class AuthResponse(BaseModel):
    ok: bool = True
    telegram_id: int
    name: str
    spinned: bool


class MeResponse(BaseModel):
    name: str
    spinned: bool
    telegram_id: int


class SpinResponse(BaseModel):
    discount: int
    promo: str | None
    angle: int


class ResultResponse(BaseModel):
    discount: int
    promo: str | None


class ErrorResponse(BaseModel):
    detail: str
