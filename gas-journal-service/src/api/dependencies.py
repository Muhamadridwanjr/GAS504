from fastapi import Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.db.database import get_db
from src.db.repositories.trade_repo import TradeRepository
from src.db.repositories.analysis_repo import AnalysisRepository
from src.core.trade_service import TradeService
from src.core.analysis_service import AnalysisService
from src.core.stats_service import StatsService
from src.lib.logger import logger
from typing import Optional
from uuid import UUID


async def get_user_id(x_user_id: Optional[str] = Header(None)) -> UUID:
    """Extract user ID from X-User-ID header (set by gateway after JWT verification)."""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-ID header. Request must go through the gateway."
        )
    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-User-ID format. Must be a valid UUID."
        )


async def verify_internal_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify internal API key for service-to-service communication."""
    if not x_api_key or x_api_key != settings.INTERNAL_API_KEY:
        logger.warning(f"Invalid internal API key attempt")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key."
        )
    return True


def get_trade_service(session: AsyncSession = Depends(get_db)) -> TradeService:
    repo = TradeRepository(session)
    return TradeService(repo)


def get_analysis_service(session: AsyncSession = Depends(get_db)) -> AnalysisService:
    repo = AnalysisRepository(session)
    return AnalysisService(repo)


def get_stats_service(session: AsyncSession = Depends(get_db)) -> StatsService:
    repo = TradeRepository(session)
    return StatsService(repo)
