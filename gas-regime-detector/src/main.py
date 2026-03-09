from fastapi import FastAPI
from src.api.routes import router
from src.cache.redis_cache import cache
from src.config import settings
from src.lib.logger import logger

app = FastAPI(
    title="GAS Regime Detector",
    description="Detects market regime (trending, ranging, high-volatility) using rule-based or ML approaches",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting GAS Regime Detector...")
    await cache.connect()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down GAS Regime Detector...")
    await cache.disconnect()

app.include_router(router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "gas-regime-detector",
        "redis_connected": cache.redis is not None,
        "method": settings.regime_method
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=(settings.environment == "development"))
