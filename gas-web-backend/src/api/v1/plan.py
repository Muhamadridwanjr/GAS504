from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user

router = APIRouter(tags=["Trading Plan"], dependencies=[Depends(get_current_user)])

@router.get("/")
async def get_trading_plan(user_id: str = Depends(get_current_user)):
    return {"plan": "Current mock trading plan"}

@router.post("/")
async def create_trading_plan(user_id: str = Depends(get_current_user)):
    return {"message": "Plan created"}

@router.put("/")
async def update_trading_plan(user_id: str = Depends(get_current_user)):
    return {"message": "Plan updated"}

@router.post("/ai-generate")
async def generate_ai_plan(user_id: str = Depends(get_current_user)):
    # ULTIMATE ONLY
    return {"message": "AI generated plan via LLM endpoint"}
