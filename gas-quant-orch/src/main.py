from fastapi import FastAPI
from src.api.routes import router
from src.cache.redis_cache import cache
from src.config import settings
from src.lib.logger import logger

app = FastAPI(
    title="GAS Quant Orchestrator",
    description="Main quant layer orchestrator, aggregating signals from various quant engines.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting GAS Quant Orchestrator...")
    await cache.connect()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down GAS Quant Orchestrator...")
    await cache.disconnect()

app.include_router(router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "gas-quant-orchestrator",
        "redis_connected": cache.redis is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=(settings.environment == "development"))
