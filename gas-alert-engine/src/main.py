import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import alerts, internal
from src.redis.client import redis_client
from src.db.database import engine, Base
from src.core.worker import start_worker
from src.lib.logger import logger
from src.config import settings

# Background task handle
_worker_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _worker_task

    # ── Startup ──────────────────────────────────────────────
    logger.info("Starting GAS Alert Engine...")

    # Initialize DB (auto-create tables for development/quickstart)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")

    # Connect Redis
    await redis_client.connect()

    # Start background worker for market data
    _worker_task = asyncio.create_task(start_worker())
    logger.info("Market data worker started in background")

    yield

    # ── Shutdown ─────────────────────────────────────────────
    logger.info("Shutting down GAS Alert Engine...")
    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    await redis_client.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Mesin pemantau kondisi pasar realtime untuk notifikasi personal pengguna.",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Include routers
app.include_router(alerts.router)
app.include_router(internal.router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    redis_ok = False
    try:
        redis_ok = await redis_client.redis.ping() if redis_client.redis else False
    except Exception:
        redis_ok = False

    return {
        "status": "ok",
        "service": "gas-alert-engine",
        "version": "1.0.0",
        "redis_connected": redis_ok,
        "worker_running": _worker_task is not None and not _worker_task.done() if _worker_task else False,
    }
