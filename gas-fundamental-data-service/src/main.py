"""FastAPI entry point for gas-fundamental-data-service."""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.security.middleware import InternalKeyMiddleware

from src.config import settings
from src.db.database import init_db
from src.cache.redis_cache import RedisCache
from src.api.routes import router as fund_router
from src.api.models import HealthResponse
from src.lib.logger import get_logger, setup_logging
from src.ingestion.scheduler import start_scheduler, stop_scheduler

setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s on port %d [%s]", settings.SERVICE_NAME, settings.PORT, settings.ENVIRONMENT)
    await init_db()
    cache = RedisCache()
    await cache.connect()
    app.state.cache = cache
    start_scheduler()
    logger.info("%s ready", settings.SERVICE_NAME)
    yield
    stop_scheduler()
    await cache.close()
    logger.info("%s shutdown.", settings.SERVICE_NAME)

app = FastAPI(title="gas-fundamental-data-service", description="Macro Database: interest rates, GDP, gold reserves.", version="1.0.0", lifespan=lifespan, docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
# Internal security — must be last (runs first due to starlette ordering)
app.add_middleware(InternalKeyMiddleware)

app.include_router(fund_router)

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    return HealthResponse(status="ok", service=settings.SERVICE_NAME, version="1.0.0", environment=settings.ENVIRONMENT)
