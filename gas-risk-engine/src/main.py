import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import router
from src.cache.redis_cache import cache
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting GAS Risk Engine...")
    await cache.connect()
    yield
    # Shutdown
    logger.info("Shutting down GAS Risk Engine...")
    await cache.close()

app = FastAPI(title="GAS Risk Engine", version="1.0.0", lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
