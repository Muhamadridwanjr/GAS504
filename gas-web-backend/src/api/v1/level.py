from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user

router = APIRouter(tags=["Level Progression"], dependencies=[Depends(get_current_user)])

@router.get("/level")
async def get_user_level(user_id: str = Depends(get_current_user)):
    return {"level": 15, "points": 1500, "unlocked_features": ["basic_ai", "tcg_access"]}
