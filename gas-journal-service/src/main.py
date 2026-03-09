from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import trades, analysis, stats, internal
from src.api.middleware import LoggingMiddleware
from src.redis.client import redis_client
from src.db.database import engine, Base
from src.lib.logger import logger
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting GAS Journal Service...")

    # Initialize DB (auto-create tables for development)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

    await redis_client.connect()

    yield

    # Shutdown
    logger.info("Shutting down GAS Journal Service...")
    await redis_client.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Pencatat riwayat trading dan analisis – GAS Ecosystem",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(LoggingMiddleware)

# Routes
app.include_router(trades.router)
app.include_router(analysis.router)
app.include_router(stats.router)
app.include_router(internal.router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint untuk Docker healthcheck dan monitoring."""
    redis_ok = False
    try:
        redis_ok = await redis_client.redis.ping() if redis_client.redis else False
    except Exception:
        pass

    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
            db_ok = True
    except Exception:
        pass

    status_val = "ok" if (redis_ok and db_ok) else "degraded"
    return {
        "status": status_val,
        "service": "gas-journal-service",
        "version": "1.0.0",
        "redis_connected": redis_ok,
        "database_connected": db_ok,
    }
