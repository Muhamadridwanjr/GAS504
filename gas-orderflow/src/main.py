import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import router
from src.storage.redis_ts import store
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting GAS Order Flow Engine...")
    await store.connect()
    yield
    logger.info("Shutting down GAS Order Flow Engine...")
    await store.close()

app = FastAPI(title="GAS Order Flow Engine", version="1.0.0", lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
