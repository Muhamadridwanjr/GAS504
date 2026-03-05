"""
FastAPI entry point for gas-screener-service.
"""
from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.security.middleware import InternalKeyMiddleware


from src.config import settings
from src.cache.redis_cache import RedisCache
from src.core.orchestrator import ScreenerOrchestrator
from src.api.routes import router as screener_router
from src.api.models import HealthResponse
from src.lib.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s on port %d [%s]", settings.SERVICE_NAME, settings.PORT, settings.ENVIRONMENT)

    cache = RedisCache()
    await cache.connect()

    orchestrator = ScreenerOrchestrator(cache=cache)

    app.state.cache = cache
    app.state.orchestrator = orchestrator

    logger.info("%s ready ✓", settings.SERVICE_NAME)
    yield

    await cache.close()
    logger.info("%s shutdown complete.", settings.SERVICE_NAME)


app = FastAPI(
    title="gas-screener-service",
    description="Parallel asset screener using indicator and SMC engines.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
# Internal security — must be last (runs first due to starlette ordering)
app.add_middleware(InternalKeyMiddleware)


app.include_router(screener_router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    return HealthResponse(status="ok", service=settings.SERVICE_NAME, version="1.0.0", environment=settings.ENVIRONMENT)
