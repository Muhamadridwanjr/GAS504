"""
GAS Terminal Backend – Main application.
Aggregator service for the GAS Terminal frontend.
"""
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.services.client import close_client
from src.ws.handler import websocket_endpoint

# ── Routes ──────────────────────────────────────────────────────────
from src.routes.overview import router as overview_router
from src.routes.pairs import router as pairs_router
from src.routes.signal import router as signal_router
from src.routes.news import router as news_router
from src.routes.calendar import router as calendar_router
from src.routes.chart import router as chart_router
from src.routes.preferences import router as preferences_router
from src.routes.terminal import router as terminal_router
from src.routes.ai import router as ai_router
from src.routes.gas import router as gas_router
from src.routes.fundamental import router as fundamental_router
from src.services.redis import redis_service

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
)
logger = structlog.get_logger(__name__)


async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("starting", service=settings.APP_NAME, port=settings.PORT)
    await redis_service.connect()
    yield
    await redis_service.close()
    await close_client()
    logger.info("shutdown", service=settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health check ────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "gas-terminal-backend", "version": "1.0.0"}


# ── Include routers ────────────────────────────────────────────────
app.include_router(overview_router)
app.include_router(pairs_router)
app.include_router(signal_router)
app.include_router(news_router)
app.include_router(calendar_router)
app.include_router(chart_router)
app.include_router(preferences_router)
app.include_router(terminal_router)
app.include_router(ai_router)
app.include_router(gas_router)
app.include_router(fundamental_router)

# ── WebSocket ───────────────────────────────────────────────────────
app.websocket("/terminal/ws")(websocket_endpoint)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=True)
