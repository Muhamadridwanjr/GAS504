from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database import get_db
from src.core.models import UserCredits
from src.core.pricing_data import PRICING_TIERS
from src.core.schemas import CreditStatus
from src.core.billing_engine import can_perform_analysis
from uuid import UUID

router = APIRouter(prefix="/billing", tags=["billing"])

@router.get("/status/{user_id}", response_model=CreditStatus)
async def get_status(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserCredits).where(UserCredits.user_id == user_id))
    user_credits = result.scalar_one_or_none()
    if not user_credits:
        # Auto-create free tier if not exists
        user_credits = UserCredits(user_id=user_id, tier="free", quota=0, boost=0)
        db.add(user_credits)
        await db.commit()
        await db.refresh(user_credits)

    # Ensure daily reset logic runs even on GET
    can_perform_analysis(user_credits)
    await db.commit()

    return user_credits

@router.get("/tiers")
async def get_tiers():
    return PRICING_TIERS
