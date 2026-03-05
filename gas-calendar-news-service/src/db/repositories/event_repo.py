from __future__ import annotations
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import EconomicEvent
from datetime import datetime

class EventRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_events(self, country: str | None = None, importance: str | None = None,
                         from_date: datetime | None = None, to_date: datetime | None = None, limit: int = 100):
        q = select(EconomicEvent)
        if country: q = q.where(EconomicEvent.country == country.upper())
        if importance: q = q.where(EconomicEvent.importance == importance.lower())
        if from_date: q = q.where(EconomicEvent.time_utc >= from_date)
        if to_date: q = q.where(EconomicEvent.time_utc <= to_date)
        q = q.order_by(EconomicEvent.time_utc.desc()).limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def upsert_event(self, **kwargs) -> EconomicEvent:
        evt = EconomicEvent(**kwargs)
        self.session.add(evt)
        await self.session.commit()
        await self.session.refresh(evt)
        return evt
