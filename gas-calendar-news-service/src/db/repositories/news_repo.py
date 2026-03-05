from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import News

class NewsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_news(self, limit: int = 50):
        q = select(News).order_by(News.published_at.desc()).limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all())
