from fastapi import FastAPI, Depends, Query
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.api.routes import signals
from src.core.billing_client import billing_client
from src.redis.client import redis_client
from src.db.database import engine, Base, get_db
from src.db.models import Signal
from src.lib.logger import logger
from src.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start
    logger.info("Starting GAS Signal Service...")
    
    # Initialize DB (Auto create tables for development/quickstart)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    await redis_client.connect()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await redis_client.disconnect()
    await billing_client.close()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

app.include_router(signals.router)

@app.get("/signal/latest", tags=["Public"])
async def get_latest_signal(
    pair: str = Query("XAUUSD", description="Trading symbol"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get the latest active signal for a pair.
    No auth required – used by terminal-backend overview and EA polling.
    """
    try:
        result = await session.execute(
            select(Signal)
            .where(Signal.symbol == pair, Signal.is_active == True)
            .order_by(desc(Signal.created_at))
            .limit(1)
        )
        signal = result.scalars().first()
        if not signal:
            return {"error": "no_signal", "pair": pair}

        meta = signal.metadata_info or {}
        return {
            "id": str(signal.id),
            "pair": signal.symbol,
            "type": signal.action.value,
            "action": signal.action.value,
            "grade": meta.get("grade", "B+"),
            "level": meta.get("level", "WAIT SETUP"),
            "entry": str(signal.entry_price),
            "sl": str(signal.stop_loss),
            "tp1": str(signal.take_profit),
            "tp2": str(meta.get("tp2", signal.take_profit)),
            "confidence": int((signal.confidence or 0.65) * 10),
            "rr": meta.get("rr", "1:2.0"),
            "timeframe": signal.timeframe or "M15",
            "timestamp": signal.created_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching latest signal: {e}")
        return {"error": "db_error", "detail": str(e)}


@app.get("/health", tags=["System"])
async def health_check():
    # Verify minimal deps
    redis_ok = await redis_client.redis.ping() if redis_client.redis else False
    return {
        "status": "ok",
        "redis_connected": redis_ok
    }
