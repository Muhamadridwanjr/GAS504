from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import auth, health
from src.config import settings
from src.utils.logger import logger
from src.core.database import engine, Base
from src.models.user import User  # import so table is registered

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("service_started", app_name=settings.APP_NAME, port=settings.PORT)
    yield
    logger.info("service_shutting_down")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/v1", tags=["Health"])
app.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])


@app.get("/")
async def root():
    return {"message": "GAS Auth Service is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
