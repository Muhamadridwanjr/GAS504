"""Repository for fundamental data CRUD."""
from __future__ import annotations
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from src.db.models import FundamentalData
from src.lib.logger import get_logger

logger = get_logger(__name__)

class FundamentalRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_data(self, symbol: str, indicator: str, from_time: int | None = None,
                       to_time: int | None = None, limit: int = 100) -> list[FundamentalData]:
        q = select(FundamentalData).where(
            and_(FundamentalData.symbol == symbol, FundamentalData.indicator == indicator))
        if from_time: q = q.where(FundamentalData.time >= from_time)
        if to_time: q = q.where(FundamentalData.time <= to_time)
        q = q.order_by(FundamentalData.time.desc()).limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def upsert(self, symbol: str, indicator: str, time: int, value: float,
                     unit: str = "", source: str = "") -> FundamentalData:
        stmt = insert(FundamentalData).values(
            symbol=symbol, indicator=indicator, time=time, value=value, unit=unit, source=source
        ).on_conflict_do_update(
            index_elements=["symbol", "indicator", "time"],
            set_=dict(value=value, unit=unit, source=source)
        ).returning(FundamentalData)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete(self, record_id: int) -> bool:
        q = select(FundamentalData).where(FundamentalData.id == record_id)
        result = await self.session.execute(q)
        obj = result.scalar_one_or_none()
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        return False
