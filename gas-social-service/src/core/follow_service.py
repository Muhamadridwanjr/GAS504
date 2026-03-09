import asyncio
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.db.repositories.follow_repo import FollowRepository
from src.core.exceptions import AlreadyFollowingError, NotFollowingError, SelfFollowError
from src.lib.logger import logger


class FollowService:
    """Business logic for follow/unfollow operations."""

    def __init__(self, db: AsyncSession):
        self.repo = FollowRepository(db)

    async def follow_user(self, follower_id: str, followee_id: str) -> Dict[str, Any]:
        """Follow a user. Raises SelfFollowError or AlreadyFollowingError."""
        if follower_id == followee_id:
            raise SelfFollowError()
        try:
            follow = await self.repo.create(follower_id, followee_id)
            logger.info(f"User {follower_id} followed {followee_id}")
            return {
                "follower_id": follow.follower_id,
                "followee_id": follow.followee_id,
                "followed_at": follow.created_at.isoformat(),
            }
        except IntegrityError:
            raise AlreadyFollowingError()

    async def unfollow_user(self, follower_id: str, followee_id: str) -> None:
        """Unfollow a user. Raises NotFollowingError if not following."""
        deleted = await self.repo.delete(follower_id, followee_id)
        if not deleted:
            raise NotFollowingError()
        logger.info(f"User {follower_id} unfollowed {followee_id}")

    async def get_followers(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """Get paginated list of followers."""
        rows, total = await self.repo.get_followers(user_id, limit, offset)
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [
                {"user_id": r.follower_id, "followed_at": r.created_at.isoformat()}
                for r in rows
            ],
        }

    async def get_following(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """Get paginated list of users being followed."""
        rows, total = await self.repo.get_following(user_id, limit, offset)
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [
                {"user_id": r.followee_id, "followed_at": r.created_at.isoformat()}
                for r in rows
            ],
        }

    async def check_follow_status(self, follower_id: str, followee_id: str) -> bool:
        """Check if follower_id is following followee_id."""
        return await self.repo.is_following(follower_id, followee_id)

    async def get_follower_ids(self, user_id: str) -> List[str]:
        """Get all follower IDs for a user (used by signal posting fan-out)."""
        return await self.repo.get_follower_ids(user_id)
