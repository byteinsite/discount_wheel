"""Weighted prize selection and promo/angle helpers."""

from __future__ import annotations

import random
import secrets
import string
from dataclasses import dataclass


@dataclass(frozen=True)
class Prize:
    discount: int  # 0 = no win
    weight: int
    promo_prefix: str | None = None


# Spec weights (sum = 100)
PRIZES: tuple[Prize, ...] = (
    Prize(discount=5, weight=30, promo_prefix="SALE"),
    Prize(discount=10, weight=25, promo_prefix="SALE"),
    Prize(discount=15, weight=20, promo_prefix="SALE"),
    Prize(discount=20, weight=12, promo_prefix="WELCOME"),
    Prize(discount=25, weight=8, promo_prefix="VIP"),
    Prize(discount=30, weight=5, promo_prefix="MEGA"),
)

# Visual segments on the wheel (order matters for angle → prize mapping).
# "0" = без выигрыша — сегмент на колесе; чтобы выдавать его, добавьте Prize с weight > 0.
WHEEL_SEGMENTS: tuple[int, ...] = (5, 10, 15, 20, 25, 30, 0)


def choose_prize(rng: random.Random | None = None) -> Prize:
    rng = rng or random.SystemRandom()
    active = [p for p in PRIZES if p.weight > 0]
    weights = [p.weight for p in active]
    return rng.choices(active, weights=weights, k=1)[0]


def generate_promo_code(discount: int, prefix: str | None) -> str | None:
    if discount <= 0 or not prefix:
        return None
    suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"{prefix}{discount}-{suffix}"


def compute_spin_angle(discount: int, full_spins: int = 5) -> int:
    """Return total rotation in degrees so the wheel lands on the winning segment.

    Pointer is fixed at the top. Segments are drawn clockwise from -90° (top).
    """
    try:
        index = WHEEL_SEGMENTS.index(discount)
    except ValueError:
        index = len(WHEEL_SEGMENTS) - 1

    segment_count = len(WHEEL_SEGMENTS)
    segment_deg = 360 / segment_count
    center = index * segment_deg + segment_deg / 2
    landing = (360 - center) % 360
    jitter = random.uniform(-segment_deg * 0.35, segment_deg * 0.35)
    return int(full_spins * 360 + landing + jitter)
