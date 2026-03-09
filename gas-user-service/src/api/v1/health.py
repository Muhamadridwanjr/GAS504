from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.core.database import get_db
from src.utils.logger import logger

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "service": "gas-user-service", "database": "connected"}
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {"status": "unhealthy", "service": "gas-user-service", "database": "disconnected", "error": str(e)}
