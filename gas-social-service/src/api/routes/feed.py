from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.api.dependencies import get_current_user_id
from src.api.models import FeedResponse
from src.core.feed_service import FeedService

router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("", response_model=FeedResponse)
async def get_feed(
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    from_ts: Optional[str] = Query(None, alias="from", description="ISO timestamp filter"),
    current_user: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the social feed for the current user.
    Returns inside signals from users being followed, sorted by newest first.
    """
    svc = FeedService(db)
    return await svc.get_feed(
        user_id=current_user,
        limit=limit,
        offset=offset,
        from_ts=from_ts,
    )
