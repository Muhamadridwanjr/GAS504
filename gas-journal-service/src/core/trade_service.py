from src.db.repositories.trade_repo import TradeRepository
from src.redis.client import redis_client
from src.core.exceptions import TradeNotFoundError
from uuid import UUID
from src.lib.logger import logger


class TradeService:
    def __init__(self, repo: TradeRepository):
        self.repo = repo

    async def create_trade(self, data: dict):
        """Create a new trade entry."""
        trade = await self.repo.create_trade(**data)

        # Invalidate stats cache for this user
        await redis_client.invalidate(f"stats:{data['user_id']}:*")

        # Publish event
        await redis_client.publish_event("journal:trade:new", {
            "id": str(trade.id),
            "user_id": str(trade.user_id),
            "symbol": trade.symbol,
            "action": trade.action.value,
            "status": trade.status.value,
        })

        logger.info(f"Trade created: {trade.id} for user {trade.user_id}")
        return trade

    async def get_trade(self, trade_id: UUID, user_id: UUID):
        """Get a single trade by ID, scoped to user."""
        trade = await self.repo.get_trade_by_id(trade_id)
        if not trade:
            raise TradeNotFoundError(f"Trade {trade_id} not found")
        if str(trade.user_id) != str(user_id):
            raise TradeNotFoundError(f"Trade {trade_id} not found")
        return trade

    async def get_trade_internal(self, trade_id: UUID):
        """Get a single trade by ID (internal - no user scope)."""
        trade = await self.repo.get_trade_by_id(trade_id)
        if not trade:
            raise TradeNotFoundError(f"Trade {trade_id} not found")
        return trade

    async def list_trades(self, user_id: UUID, filters: dict):
        """List trades for a user with filters."""
        trades, total = await self.repo.get_trades(
            user_id=user_id,
            symbol=filters.get("symbol"),
            status=filters.get("status"),
            from_date=filters.get("from_date"),
            to_date=filters.get("to_date"),
            sort=filters.get("sort", "-entry_time"),
            limit=filters.get("limit", 50),
            offset=filters.get("offset", 0),
        )
        return trades, total

    async def update_trade(self, trade_id: UUID, data: dict):
        """Update a trade (e.g. close it)."""
        trade = await self.repo.update_trade(trade_id, **data)
        if not trade:
            raise TradeNotFoundError(f"Trade {trade_id} not found")

        # Invalidate stats cache
        await redis_client.invalidate(f"stats:{trade.user_id}:*")

        logger.info(f"Trade updated: {trade_id}")
        return trade

    async def delete_trade(self, trade_id: UUID, user_id: UUID):
        """Soft delete a trade."""
        trade = await self.repo.get_trade_by_id(trade_id)
        if not trade:
            raise TradeNotFoundError(f"Trade {trade_id} not found")
        if str(trade.user_id) != str(user_id):
            raise TradeNotFoundError(f"Trade {trade_id} not found")

        success = await self.repo.soft_delete_trade(trade_id)
        if success:
            await redis_client.invalidate(f"stats:{user_id}:*")
        return success
