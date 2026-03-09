from fastapi import FastAPI, Depends, Response, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import api_router
from src.core.proxy_handler import forward_request, forward_websocket
from src.config import settings
from src.middleware.auth import AuthMiddleware
from src.middleware.api_key import ApiKeyMiddleware
from src.middleware.rate_limit import RateLimitMiddleware
from src.middleware.logging import LoggingMiddleware
from src.services.redis_client import redis_client
from src.utils.logger import logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting GAS Gateway API")
    try:
        await redis_client.connect()
    except Exception as e:
        logger.error("Startup failed: Redis connection error", error=str(e))
    
    yield
    
    # Shutdown logic
    logger.info("Shutting down GAS Gateway API")
    await redis_client.close()

app = FastAPI(
    title=settings.APP_NAME,
    description="Main Gateway for Golden AI Strategy (GAS) Ecosystem",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Middleware (Order matters: Logging -> Api Key -> Rate Limit -> Auth)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ApiKeyMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Include API Router
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}

@app.api_route("/mt5/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def root_proxy_mt5(request: Request, path: str):
    target_url = f"{settings.MT5_WEBSOCKET_URL}/{path}"
    return await forward_request(request, target_url)

@app.api_route("/terminal/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def root_proxy_terminal(request: Request, path: str):
    target_url = f"{settings.TERMINAL_BACKEND_URL}/terminal/{path}"
    return await forward_request(request, target_url)

@app.websocket("/terminal/ws")
async def terminal_ws_proxy(websocket: WebSocket):
    await websocket.accept()
    # Convert http:// to ws:// for internal target
    target_ws_url = settings.TERMINAL_BACKEND_URL.replace("http://", "ws://") + "/terminal/ws"
    await forward_websocket(websocket, target_ws_url)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health"
    }
