from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .utils.logger import logger
from .api.v1 import health, public, dashboard, journal, plan, analysis, tcg, billing, level, certificate, notifications

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

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up", app_name=settings.APP_NAME, port=settings.PORT)

@app.on_event("shutdown")
async def shutdown_event():
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

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}
