from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.routes import follows, signals, feed, internal
from src.db.database import engine, Base
from src.lib.logger import logger
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ─────────────────────────────────────────────────────────────
    logger.info("🚀 Starting GAS Social Service...")

    # Auto-create tables (development convenience — use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables ready")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("🛑 Shutting down GAS Social Service...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "Jantung interaksi sosial antar pengguna GAS. "
        "Mengelola follow, unfollow, sinyal insider, dan feed sosial."
    ),
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(follows.router)
app.include_router(signals.router)
app.include_router(feed.router)
app.include_router(internal.router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint – used by Docker healthcheck and gateway."""
    return {
        "status": "ok",
        "service": "gas-social-service",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint – service info."""
    return {
        "service": "gas-social-service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
