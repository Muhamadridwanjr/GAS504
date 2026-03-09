from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from src.db.models import Trade, TradeStatus
from uuid import UUID
from datetime import datetime, timezone


class TradeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_trade(self, **kwargs) -> Trade:
        trade = Trade(**kwargs)
        self.session.add(trade)
        await self.session.commit()
        await self.session.refresh(trade)
        return trade

    async def get_trade_by_id(self, trade_id: UUID) -> Trade | None:
        result = await self.session.execute(
            select(Trade).where(
                and_(Trade.id == trade_id, Trade.deleted_at.is_(None))
            )
        )
        return result.scalars().first()

    async def get_trades(
        self,
        user_id: UUID,
        symbol: str = None,
        status: str = None,
        from_date: datetime = None,
        to_date: datetime = None,
        sort: str = "-entry_time",
        limit: int = 50,
        offset: int = 0,
    ):
        query = select(Trade).where(
            and_(Trade.user_id == user_id, Trade.deleted_at.is_(None))
        )

        conditions = []
        if symbol:
            conditions.append(Trade.symbol == symbol.upper())
        if status:
            try:
                conditions.append(Trade.status == TradeStatus(status.upper()))
            except ValueError:
                pass
        if from_date:
            conditions.append(Trade.entry_time >= from_date)
        if to_date:
            conditions.append(Trade.entry_time <= to_date)

        if conditions:
            query = query.where(and_(*conditions))

        # Sorting
        if sort.startswith("-"):
            col = getattr(Trade, sort[1:], Trade.entry_time)
            query = query.order_by(desc(col))
        else:
            col = getattr(Trade, sort, Trade.entry_time)
            query = query.order_by(col)

        # Count total
        count_query = select(func.count(Trade.id)).where(
            and_(Trade.user_id == user_id, Trade.deleted_at.is_(None))
        )
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Paginate
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        trades = result.scalars().all()

        return trades, total

    async def update_trade(self, trade_id: UUID, **kwargs) -> Trade | None:
        trade = await self.get_trade_by_id(trade_id)
        if not trade:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(trade, key):
                setattr(trade, key, value)
        trade.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(trade)
        return trade

    async def soft_delete_trade(self, trade_id: UUID) -> bool:
        trade = await self.get_trade_by_id(trade_id)
        if not trade:
            return False
        trade.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True

    async def get_closed_trades_for_stats(
        self,
        user_id: UUID,
        symbol: str = None,
        from_date: datetime = None,
        to_date: datetime = None,
    ) -> list[Trade]:
        """Get all closed trades for statistics calculation."""
        query = select(Trade).where(
            and_(
                Trade.user_id == user_id,
                Trade.status == TradeStatus.CLOSED,
                Trade.deleted_at.is_(None),
            )
        )

        conditions = []
        if symbol:
            conditions.append(Trade.symbol == symbol.upper())
        if from_date:
            conditions.append(Trade.entry_time >= from_date)
        if to_date:
            conditions.append(Trade.entry_time <= to_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Trade.entry_time)
        result = await self.session.execute(query)
        return result.scalars().all()
