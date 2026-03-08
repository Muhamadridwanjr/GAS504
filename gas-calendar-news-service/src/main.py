"""FastAPI entry point for gas-calendar-news-service."""
from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.security.middleware import InternalKeyMiddleware

from src.config import settings
from src.db.database import init_db
from src.cache.redis_cache import RedisCache
from src.api.routes import router
from src.api.models import HealthResponse
from src.lib.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s on port %d [%s]", settings.SERVICE_NAME, settings.PORT, settings.ENVIRONMENT)
    await init_db()
    cache = RedisCache(); await cache.connect()
    app.state.cache = cache
    logger.info("%s ready", settings.SERVICE_NAME)

    # Start background scheduler: ingest yesterday → +7 days, refresh every 6h
    from src.ingestion.scheduler import start_scheduler
    task = asyncio.create_task(start_scheduler(interval_hours=6))
    app.state.scheduler_task = task
    logger.info("🗓 Calendar scheduler started (refresh every 6h)")

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await cache.close()

app = FastAPI(title="gas-calendar-news-service", description="News & Macro Hub with ecocal.", version="1.0.0", lifespan=lifespan, docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
# Internal security — must be last (runs first due to starlette ordering)
app.add_middleware(InternalKeyMiddleware)

app.include_router(router)

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    return HealthResponse(status="ok", service=settings.SERVICE_NAME, version="1.0.0", environment=settings.ENVIRONMENT)
