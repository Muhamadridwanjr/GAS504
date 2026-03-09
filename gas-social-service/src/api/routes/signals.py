from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.api.dependencies import get_current_user_id
from src.api.models import InsiderSignalRequest
from src.core.signal_service import SignalService

router = APIRouter(prefix="/signals", tags=["Signals"])


@router.post("/insider", status_code=201)
async def post_insider_signal(
    payload: InsiderSignalRequest,
    current_user: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Post a new insider signal.
    Signal is saved via gas-signal-service and followers are notified.
    """
    svc = SignalService(db)
    return await svc.post_insider_signal(
        user_id=current_user,
        payload=payload.model_dump(exclude_none=True),
    )
