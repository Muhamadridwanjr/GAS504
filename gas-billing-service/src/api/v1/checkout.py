from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database import get_db
from src.core.models import UserCredits, Subscription
from src.core.pricing_data import PRICING_TIERS, BOOSTER_PACKS
from src.core.billing_engine import add_xp
from uuid import UUID
from datetime import datetime, timedelta

router = APIRouter(prefix="/checkout", tags=["checkout"])

@router.post("/subscribe")
async def subscribe(user_id: UUID, tier: str, cycle: str = "monthly", db: AsyncSession = Depends(get_db)):
    tier = tier.lower()
    if tier not in PRICING_TIERS:
        raise HTTPException(status_code=400, detail="Invalid tier")

    result = await db.execute(select(UserCredits).where(UserCredits.user_id == user_id))
    user_credits = result.scalar_one_or_none()
    if not user_credits:
        user_credits = UserCredits(user_id=user_id, tier=tier)
        db.add(user_credits)
    else:
        user_credits.tier = tier

    config = PRICING_TIERS[tier]
    user_credits.quota = config["monthly_quota"]

    new_sub = Subscription(
        user_id=user_id,
        tier=tier,
        billing_cycle=cycle,
        end_date=datetime.utcnow() + timedelta(days=365 if cycle == "annual" else 30)
    )
    db.add(new_sub)

    add_xp(user_credits, 50)

    await db.commit()
    return {"status": "success", "message": f"Subscribed to {tier} tier", "tier": tier}

@router.post("/buy-booster")
async def buy_booster(user_id: UUID, pack_id: str, db: AsyncSession = Depends(get_db)):
    if pack_id not in BOOSTER_PACKS:
        raise HTTPException(status_code=400, detail="Invalid booster pack")

    result = await db.execute(select(UserCredits).where(UserCredits.user_id == user_id))
    user_credits = result.scalar_one_or_none()
    if not user_credits:
        raise HTTPException(status_code=404, detail="User not found")

    pack = BOOSTER_PACKS[pack_id]
    user_credits.boost += pack["analyses"]

    add_xp(user_credits, 10 * (1 if pack_id == "single" else 5 if pack_id == "multipack_10" else 20))

    await db.commit()
    return {"status": "success", "message": f"Added {pack['analyses']} analysis credits", "boost": user_credits.boost}
