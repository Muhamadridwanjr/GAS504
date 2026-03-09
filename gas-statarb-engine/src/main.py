from fastapi import FastAPI
from src.api.routes import router
from src.cache.redis_cache import cache
from src.core.pair_manager import pair_manager
from src.config import settings
from src.lib.logger import logger

app = FastAPI(
    title="GAS StatArb Engine",
    description="Statistical Arbitrage strategy signals utilizing cointegration and pairs trading.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting GAS StatArb Engine...")
    await cache.connect()
    # Initialize pairs parameters on startup
    await pair_manager.initialize_pairs()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down GAS StatArb Engine...")
    await cache.disconnect()

app.include_router(router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "gas-statarb-engine",
        "redis_connected": cache.redis is not None,
        "active_pairs": len(pair_manager.pairs)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=(settings.environment == "development"))
