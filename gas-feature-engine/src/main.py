from fastapi import FastAPI
from src.api.routes import router
from src.cache.redis_cache import cache
from src.config import settings
from src.lib.logger import logger

app = FastAPI(
    title="GAS Feature Engine",
    description="Transforms raw OHLC data into numeric features for quant engines",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting GAS Feature Engine...")
    await cache.connect()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down GAS Feature Engine...")
    await cache.disconnect()

app.include_router(router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "gas-feature-engine",
        "redis_connected": cache.redis is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=(settings.environment == "development"))
