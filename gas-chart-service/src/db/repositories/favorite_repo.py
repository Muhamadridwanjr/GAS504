from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import FavoriteIndicator

class FavoriteRepo:
    def __init__(self, session: AsyncSession): self.session = session

    async def list_by_user(self, user_id: str):
        q = select(FavoriteIndicator).where(FavoriteIndicator.user_id == user_id)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def add(self, user_id: str, indicator: str):
        f = FavoriteIndicator(user_id=user_id, indicator=indicator)
        self.session.add(f); await self.session.commit(); await self.session.refresh(f)
        return f

    async def remove(self, user_id: str, indicator: str):
        q = select(FavoriteIndicator).where(and_(FavoriteIndicator.user_id == user_id, FavoriteIndicator.indicator == indicator))
        result = await self.session.execute(q)
        obj = result.scalar_one_or_none()
        if obj: await self.session.delete(obj); await self.session.commit(); return True
        return False
