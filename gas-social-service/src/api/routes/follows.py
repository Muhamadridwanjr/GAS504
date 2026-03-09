from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.api.dependencies import get_current_user_id
from src.api.models import FollowResponse, FollowListResponse, FollowStatusResponse
from src.core.follow_service import FollowService

router = APIRouter(prefix="/follow", tags=["Follow"])


@router.post("/{user_id}", response_model=FollowResponse, status_code=201)
async def follow_user(
    user_id: str = Path(..., description="ID of the user to follow"),
    current_user: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Follow a user. Returns the created follow relationship."""
    svc = FollowService(db)
    return await svc.follow_user(follower_id=current_user, followee_id=user_id)


@router.delete("/{user_id}", status_code=204)
async def unfollow_user(
    user_id: str = Path(..., description="ID of the user to unfollow"),
    current_user: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Unfollow a user."""
    svc = FollowService(db)
    await svc.unfollow_user(follower_id=current_user, followee_id=user_id)


@router.get("/{user_id}/status", response_model=FollowStatusResponse)
async def check_follow_status(
    user_id: str = Path(..., description="ID of the user to check"),
    current_user: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Check whether the current user is following the specified user."""
    svc = FollowService(db)
    is_following = await svc.check_follow_status(
        follower_id=current_user, followee_id=user_id
    )
    return FollowStatusResponse(is_following=is_following)


@router.get("/followers/me", response_model=FollowListResponse, tags=["Social"])
async def get_my_followers(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of users following you."""
    svc = FollowService(db)
    return await svc.get_followers(user_id=current_user, limit=limit, offset=offset)


@router.get("/following/me", response_model=FollowListResponse, tags=["Social"])
async def get_my_following(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of users you are following."""
    svc = FollowService(db)
    return await svc.get_following(user_id=current_user, limit=limit, offset=offset)
