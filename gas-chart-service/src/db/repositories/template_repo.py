from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import ChartTemplate

class TemplateRepo:
    def __init__(self, session: AsyncSession): self.session = session

    async def list_by_user(self, user_id: str):
        q = select(ChartTemplate).where(ChartTemplate.user_id == user_id).order_by(ChartTemplate.created_at.desc())
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_by_id(self, user_id: str, tmpl_id: int):
        q = select(ChartTemplate).where(ChartTemplate.user_id == user_id, ChartTemplate.id == tmpl_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def create(self, user_id: str, name: str, layout: dict):
        t = ChartTemplate(user_id=user_id, name=name, layout=layout)
        self.session.add(t); await self.session.commit(); await self.session.refresh(t)
        return t

    async def update(self, tmpl, **kwargs):
        for k, v in kwargs.items():
            if v is not None and hasattr(tmpl, k): setattr(tmpl, k, v)
        await self.session.commit(); await self.session.refresh(tmpl)
        return tmpl

    async def delete(self, tmpl):
        await self.session.delete(tmpl); await self.session.commit()
