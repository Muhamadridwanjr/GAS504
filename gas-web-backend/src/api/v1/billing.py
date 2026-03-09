from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user

router = APIRouter(tags=["Billing View"], dependencies=[Depends(get_current_user)])

@router.get("/billing/status")
async def get_billing_status(user_id: str = Depends(get_current_user)):
    return {"plan": "ULTIMATE", "quota": 5, "boost": 10, "level": "VIP"}

@router.get("/billing/history")
async def get_billing_history(user_id: str = Depends(get_current_user)):
    return []

@router.get("/billing/usage")
async def get_billing_usage(user_id: str = Depends(get_current_user)):
    return []
