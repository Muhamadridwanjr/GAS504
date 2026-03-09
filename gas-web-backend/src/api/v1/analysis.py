from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user

router = APIRouter(tags=["Analysis History"], dependencies=[Depends(get_current_user)])

@router.get("/history")
async def get_analysis_history(user_id: str = Depends(get_current_user)):
    return []

@router.get("/{id}")
async def get_analysis_detail(id: str, user_id: str = Depends(get_current_user)):
    return {"id": id, "detail": "Analysis details from signal service"}
