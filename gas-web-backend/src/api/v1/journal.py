from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user

router = APIRouter(tags=["Journal"], dependencies=[Depends(get_current_user)])

@router.get("/")
async def list_journals(user_id: str = Depends(get_current_user)):
    return []

@router.post("/")
async def create_journal(user_id: str = Depends(get_current_user)):
    return {"message": "Journal created"}

@router.put("/{id}")
async def update_journal(id: str, user_id: str = Depends(get_current_user)):
    return {"message": "Journal updated", "id": id}

@router.delete("/{id}")
async def delete_journal(id: str, user_id: str = Depends(get_current_user)):
    return {"message": "Journal deleted", "id": id}

@router.post("/mt5-webhook")
async def mt5_webhook(user_id: str = Depends(get_current_user)):
    # ULTIMATE ONLY
    return {"message": "Auto log from EA successful"}
