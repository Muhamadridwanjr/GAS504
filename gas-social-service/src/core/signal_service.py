import asyncio
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.signal_client import signal_client
from src.clients.notification_client import notification_client
from src.db.repositories.follow_repo import FollowRepository
from src.core.exceptions import SignalServiceError
from src.lib.logger import logger


class SignalService:
    """Business logic for posting insider signals and notifying followers."""

    def __init__(self, db: AsyncSession):
        self.follow_repo = FollowRepository(db)

    async def post_insider_signal(
        self, user_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Post an insider signal for user_id.
        1. Calls gas-signal-service to persist the signal.
        2. Fetches all followers.
        3. Sends notifications to each follower asynchronously.
        """
        # 1. Save signal via signal service
        try:
            signal_data = await signal_client.create_insider_signal(user_id, payload)
        except Exception as e:
            logger.error(f"Failed to create insider signal: {e}")
            raise SignalServiceError(str(e))

        signal_id = signal_data.get("id", "")
        symbol = payload.get("symbol", "")

        # 2. Get all follower IDs
        follower_ids: List[str] = await self.follow_repo.get_follower_ids(user_id)
        logger.info(
            f"Signal {signal_id} posted by {user_id}. Notifying {len(follower_ids)} followers."
        )

        # 3. Fan-out notifications (fire-and-forget, non-critical)
        async def notify(follower_id: str):
            await notification_client.send_notification(
                user_id=follower_id,
                notification_type="new_insider_signal",
                data={
                    "signal_id": signal_id,
                    "posted_by": user_id,
                    "symbol": symbol,
                },
            )

        # Run notifications concurrently (best effort)
        await asyncio.gather(*[notify(fid) for fid in follower_ids], return_exceptions=True)

        return signal_data
