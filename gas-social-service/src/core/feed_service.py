from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.signal_client import signal_client
from src.db.repositories.follow_repo import FollowRepository
from src.lib.logger import logger


class FeedService:
    """Business logic for building the social feed."""

    def __init__(self, db: AsyncSession):
        self.follow_repo = FollowRepository(db)

    async def get_feed(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        from_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build a social feed for user_id by:
        1. Getting all users that user_id follows.
        2. Fetching their insider signals from gas-signal-service.
        3. Returning the combined, sorted feed.
        """
        # 1. Get following IDs
        following_ids = await self.follow_repo.get_following_ids(user_id)

        if not following_ids:
            logger.debug(f"User {user_id} is not following anyone – empty feed.")
            return {"total": 0, "limit": limit, "offset": offset, "data": []}

        # 2. Fetch insider signals for those users
        result = await signal_client.get_insider_signals(
            user_ids=following_ids,
            limit=limit,
            offset=offset,
            from_ts=from_ts,
        )

        return {
            "total": result.get("total", 0),
            "limit": limit,
            "offset": offset,
            "data": result.get("data", []),
        }
