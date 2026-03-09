from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.api.v1 import health, billing, checkout
from src.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(checkout.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "status": "running"}
