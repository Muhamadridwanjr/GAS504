from src.db.repositories.analysis_repo import AnalysisRepository
from src.redis.client import redis_client
from src.core.exceptions import AnalysisNotFoundError
from uuid import UUID
from src.lib.logger import logger


class AnalysisService:
    def __init__(self, repo: AnalysisRepository):
        self.repo = repo

    async def create_analysis(self, data: dict):
        """Create a new analysis entry."""
        analysis = await self.repo.create_analysis(**data)

        # Publish event
        await redis_client.publish_event("journal:analysis:new", {
            "id": str(analysis.id),
            "user_id": str(analysis.user_id),
            "symbol": analysis.symbol,
            "signal": analysis.signal.value,
        })

        logger.info(f"Analysis created: {analysis.id} for user {analysis.user_id}")
        return analysis

    async def get_analysis(self, analysis_id: UUID, user_id: UUID):
        """Get a single analysis by ID, scoped to user."""
        analysis = await self.repo.get_analysis_by_id(analysis_id)
        if not analysis:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        if str(analysis.user_id) != str(user_id):
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        return analysis

    async def list_analyses(self, user_id: UUID, filters: dict):
        """List analyses for a user with filters."""
        analyses, total = await self.repo.get_analyses(
            user_id=user_id,
            symbol=filters.get("symbol"),
            timeframe=filters.get("timeframe"),
            limit=filters.get("limit", 50),
            offset=filters.get("offset", 0),
        )
        return analyses, total

    async def delete_analysis(self, analysis_id: UUID, user_id: UUID):
        """Soft delete an analysis."""
        analysis = await self.repo.get_analysis_by_id(analysis_id)
        if not analysis:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        if str(analysis.user_id) != str(user_id):
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        return await self.repo.soft_delete_analysis(analysis_id)
