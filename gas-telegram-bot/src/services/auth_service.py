"""
GAS Bot Auth Service
Handles:
  - Generating link codes (Telegram → GAS account linking)
  - Checking linked accounts
  - Plan gating (only ultimate/ultra allowed)
"""
import secrets
import string
import time
from src.services.redis_client import get_redis
from src.config import BOT_ALLOWED_PLANS

LINK_CODE_TTL = 900  # 15 minutes


def _make_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def generate_link_code(tg_user_id: int) -> str:
    """Create a short-lived link code and return it."""
    r = await get_redis()
    code = _make_code(8)
    await r.set(f"tg:link:{code}", str(tg_user_id), ex=LINK_CODE_TTL)
    return code


async def get_gas_user_id(tg_user_id: int) -> str | None:
    """Return GAS user_id if this Telegram account is linked, else None."""
    r = await get_redis()
    return await r.get(f"tg:bind:{tg_user_id}")


async def get_user_plan(gas_user_id: str) -> str:
    r = await get_redis()
    plan = await r.get(f"user:{gas_user_id}:plan") or "free"
    # Auto-expire trial
    if plan == "trial":
        trial_exp = int((await r.get(f"user:{gas_user_id}:trial_expires_at")) or 0)
        if trial_exp and time.time() > trial_exp:
            await r.set(f"user:{gas_user_id}:plan", "free")
            plan = "free"
    return plan


async def get_user_credits(gas_user_id: str) -> int:
    r = await get_redis()
    raw = await r.get(f"user:{gas_user_id}:credits")
    return int(raw) if raw else 0


async def get_user_xp(gas_user_id: str) -> int:
    r = await get_redis()
    raw = await r.get(f"user:{gas_user_id}:xp")
    return int(raw) if raw else 0


async def get_booster(gas_user_id: str) -> str:
    r = await get_redis()
    return await r.get(f"user:{gas_user_id}:booster") or ""


async def check_bot_access(tg_user_id: int) -> tuple[str | None, str | None]:
    """
    Returns (gas_user_id, plan) if linked and plan is allowed.
    Returns (gas_user_id, plan) even if plan is not allowed — caller decides what to show.
    Returns (None, None) if not linked.
    """
    gas_user_id = await get_gas_user_id(tg_user_id)
    if not gas_user_id:
        return None, None
    plan = await get_user_plan(gas_user_id)
    return gas_user_id, plan


def is_plan_allowed(plan: str) -> bool:
    return plan in BOT_ALLOWED_PLANS
