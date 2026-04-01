import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .utils.logger import logger
from .api.v1 import health, public, dashboard, journal, plan, analysis, tcg, billing, level, certificate, notifications, booster, payments
from .api.v1 import erc20_payments, support, admin, leaderboard
from .api.v1 import agent as agent_module
from .api.v1 import polymarket as polymarket_module
from .api.v1 import memecoin as memecoin_module
from .api.v1 import telegram as telegram_module

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend for Frontend - GAS Web",
    version="1.0.0",
)

# CORS Middleware (sesuaikan dengan kebutuhan production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_erc20_poller_task = None

@app.on_event("startup")
async def startup_event():
    global _erc20_poller_task
    logger.info("Application starting up", app_name=settings.APP_NAME, port=settings.PORT)
    # Start ERC20 USDT payment poller in background
    _erc20_poller_task = asyncio.create_task(erc20_payments.start_erc20_poller())
    logger.info("ERC20 USDT payment poller scheduled")

@app.on_event("shutdown")
async def shutdown_event():
    global _erc20_poller_task
    if _erc20_poller_task:
        _erc20_poller_task.cancel()
    logger.info("Application shutting down")

# Include Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(public.router, prefix="/api/v1/public")
app.include_router(dashboard.router, prefix="/api/v1/dashboard")
app.include_router(journal.router, prefix="/api/v1/journal")
app.include_router(plan.router, prefix="/api/v1/plan")
app.include_router(analysis.router, prefix="/api/v1/analysis")
app.include_router(tcg.router, prefix="/api/v1/tcg")
app.include_router(billing.router, prefix="/api/v1")  # /api/v1/billing/* inside module
app.include_router(level.router, prefix="/api/v1/user")
app.include_router(certificate.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(booster.router, prefix="/api/v1/booster")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(erc20_payments.router, prefix="/api/v1")
app.include_router(support.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(leaderboard.router, prefix="/api/v1")
app.include_router(agent_module.router, prefix="/api/v1")
app.include_router(polymarket_module.router, prefix="/api/v1")
app.include_router(memecoin_module.router, prefix="/api/v1")
app.include_router(telegram_module.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}
