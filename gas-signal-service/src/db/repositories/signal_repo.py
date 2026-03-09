from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from src.db.models import Signal, SignalTier
from uuid import UUID

class SignalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_signal(self, **kwargs) -> Signal:
        signal = Signal(**kwargs)
        self.session.add(signal)
        await self.session.commit()
        await self.session.refresh(signal)
        return signal

    async def get_signal_by_id(self, signal_id: UUID) -> Signal | None:
        result = await self.session.execute(select(Signal).where(Signal.id == signal_id))
        return result.scalars().first()

    async def get_signals(self, allowed_tiers: list[str], symbol: str = None, limit: int = 50, offset: int = 0):
        query = select(Signal)
        
        conditions = []
        if allowed_tiers:
            tier_enums = [SignalTier(t) for t in allowed_tiers if t in [e.value for e in SignalTier]]
            conditions.append(Signal.tier.in_(tier_enums))
        if symbol:
            conditions.append(Signal.symbol == symbol)
            
        if conditions:
            query = query.where(and_(*conditions))
            
        query = query.order_by(desc(Signal.created_at)).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        signals = result.scalars().all()
        
        # count total
        count_query = select(Signal.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = len(count_result.scalars().all())
        
        return signals, total

    async def delete_signal(self, signal_id: UUID) -> bool:
        signal = await self.get_signal_by_id(signal_id)
        if signal:
            await self.session.delete(signal)
            await self.session.commit()
            return True
        return False

    async def expire_signal(self, signal_id: UUID) -> bool:
        signal = await self.get_signal_by_id(signal_id)
        if signal:
            signal.is_active = False
            await self.session.commit()
            return True
        return False
