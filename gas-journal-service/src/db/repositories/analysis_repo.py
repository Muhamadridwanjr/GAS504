from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from src.db.models import Analysis
from uuid import UUID
from datetime import datetime, timezone


class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_analysis(self, **kwargs) -> Analysis:
        analysis = Analysis(**kwargs)
        self.session.add(analysis)
        await self.session.commit()
        await self.session.refresh(analysis)
        return analysis

    async def get_analysis_by_id(self, analysis_id: UUID) -> Analysis | None:
        result = await self.session.execute(
            select(Analysis).where(
                and_(Analysis.id == analysis_id, Analysis.deleted_at.is_(None))
            )
        )
        return result.scalars().first()

    async def get_analyses(
        self,
        user_id: UUID,
        symbol: str = None,
        timeframe: str = None,
        limit: int = 50,
        offset: int = 0,
    ):
        query = select(Analysis).where(
            and_(Analysis.user_id == user_id, Analysis.deleted_at.is_(None))
        )

        conditions = []
        if symbol:
            conditions.append(Analysis.symbol == symbol.upper())
        if timeframe:
            conditions.append(Analysis.timeframe == timeframe)

        if conditions:
            query = query.where(and_(*conditions))

        # Count
        count_query = select(func.count(Analysis.id)).where(
            and_(Analysis.user_id == user_id, Analysis.deleted_at.is_(None))
        )
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Paginate
        query = query.order_by(desc(Analysis.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(query)
        analyses = result.scalars().all()

        return analyses, total

    async def soft_delete_analysis(self, analysis_id: UUID) -> bool:
        analysis = await self.get_analysis_by_id(analysis_id)
        if not analysis:
            return False
        analysis.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True
