import uuid
from typing import List, Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Follow


class FollowRepository:
    """Data access layer for follow relationships."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, follower_id: str, followee_id: str) -> Follow:
        """Create a new follow relationship."""
        follow = Follow(
            id=str(uuid.uuid4()),
            follower_id=follower_id,
            followee_id=followee_id,
        )
        self.db.add(follow)
        await self.db.commit()
        await self.db.refresh(follow)
        return follow

    async def delete(self, follower_id: str, followee_id: str) -> bool:
        """Delete a follow relationship. Returns True if deleted."""
        result = await self.db.execute(
            delete(Follow).where(
                Follow.follower_id == follower_id,
                Follow.followee_id == followee_id,
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_followers(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[List[Follow], int]:
        """Get list of followers for a user and total count."""
        total_q = select(func.count(Follow.id)).where(Follow.followee_id == user_id)
        total = (await self.db.execute(total_q)).scalar_one()

        q = (
            select(Follow)
            .where(Follow.followee_id == user_id)
            .order_by(Follow.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self.db.execute(q)).scalars().all()
        return list(rows), total

    async def get_following(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[List[Follow], int]:
        """Get list of users that user_id is following."""
        total_q = select(func.count(Follow.id)).where(Follow.follower_id == user_id)
        total = (await self.db.execute(total_q)).scalar_one()

        q = (
            select(Follow)
            .where(Follow.follower_id == user_id)
            .order_by(Follow.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self.db.execute(q)).scalars().all()
        return list(rows), total

    async def get_following_ids(self, user_id: str) -> List[str]:
        """Get all followee IDs for a user (for feed and notification fan-out)."""
        q = select(Follow.followee_id).where(Follow.follower_id == user_id)
        rows = (await self.db.execute(q)).scalars().all()
        return list(rows)

    async def get_follower_ids(self, user_id: str) -> List[str]:
        """Get all follower IDs for a user."""
        q = select(Follow.follower_id).where(Follow.followee_id == user_id)
        rows = (await self.db.execute(q)).scalars().all()
        return list(rows)

    async def is_following(self, follower_id: str, followee_id: str) -> bool:
        """Check if follower_id is following followee_id."""
        q = select(Follow.id).where(
            Follow.follower_id == follower_id,
            Follow.followee_id == followee_id,
        )
        result = (await self.db.execute(q)).scalar_one_or_none()
        return result is not None
