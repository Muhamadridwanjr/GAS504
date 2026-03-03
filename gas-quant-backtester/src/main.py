from fastapi import FastAPI
from src.api.routes import router
from src.db.database import init_db
from src.data.cache import cache
from src.config import settings
from src.lib.logger import logger

app = FastAPI(
    title="GAS Quant Backtester",
    description="Engine backtesting quant strategy dengan history data.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting GAS Quant Backtester...")
    # Initialize SQLite database
    await init_db()
    # Connect to Redis via Cache
    await cache.connect()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down GAS Quant Backtester...")
    await cache.disconnect()

app.include_router(router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "gas-quant-backtester",
        "redis_connected": cache.redis is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=(settings.environment == "development"))
