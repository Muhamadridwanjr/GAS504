from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user

router = APIRouter(tags=["TCG Integration"], dependencies=[Depends(get_current_user)])

@router.get("/profile")
async def get_tcg_profile(user_id: str = Depends(get_current_user)):
    return {"level": 10, "collection_count": 25}

@router.get("/cards")
async def get_tcg_cards(user_id: str = Depends(get_current_user)):
    return []

@router.post("/equip")
async def equip_card(user_id: str = Depends(get_current_user)):
    return {"message": "Card equipped successfully"}
