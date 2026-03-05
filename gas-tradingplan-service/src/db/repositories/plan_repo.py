from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import TradingPlan
from src.config import settings

class PlanRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _base_query(self, user_id: str):
        q = select(TradingPlan).where(TradingPlan.user_id == user_id)
        if settings.SOFT_DELETE:
            q = q.where(TradingPlan.deleted_at.is_(None))
        return q

    async def create(self, user_id: str, **kwargs) -> TradingPlan:
        plan = TradingPlan(user_id=user_id, **kwargs)
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_by_id(self, user_id: str, plan_id: int) -> TradingPlan | None:
        q = self._base_query(user_id).where(TradingPlan.id == plan_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def list_plans(self, user_id: str, status=None, symbol=None, from_date=None, to_date=None, limit=50, offset=0):
        q = self._base_query(user_id)
        if status: q = q.where(TradingPlan.status == status)
        if symbol: q = q.where(TradingPlan.symbol == symbol.upper())
        if from_date: q = q.where(TradingPlan.plan_date >= from_date)
        if to_date: q = q.where(TradingPlan.plan_date <= to_date)
        q = q.order_by(TradingPlan.plan_date.desc()).offset(offset).limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def update(self, plan: TradingPlan, **kwargs) -> TradingPlan:
        for k, v in kwargs.items():
            if v is not None and hasattr(plan, k): setattr(plan, k, v)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def delete(self, plan: TradingPlan):
        if settings.SOFT_DELETE:
            plan.deleted_at = datetime.now(timezone.utc)
            await self.session.commit()
        else:
            await self.session.delete(plan)
            await self.session.commit()

    async def set_status(self, plan: TradingPlan, status: str) -> TradingPlan:
        plan.status = status
        await self.session.commit()
        await self.session.refresh(plan)
        return plan
