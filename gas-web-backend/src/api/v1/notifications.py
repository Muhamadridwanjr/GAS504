from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user

router = APIRouter(tags=["Notifications Feed"], dependencies=[Depends(get_current_user)])

@router.get("/notifications")
async def get_notifications(user_id: str = Depends(get_current_user)):
    return []
