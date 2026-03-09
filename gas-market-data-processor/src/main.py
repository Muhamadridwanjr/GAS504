from fastapi import FastAPI
from fastapi.responses import JSONResponse
import redis.asyncio as redis

from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="GAS Market Data Processor",
    description="Internal Library Wrapper for Healthcheck and Operations",
    version="1.0.0"
)

# Initialize a global redis client for the app context if needed
redis_client = None

@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD or None,
        db=settings.REDIS_DB,
        decode_responses=True
    )
    logger.info(f"Processor Wrapper Started. Redis client connected to {settings.REDIS_HOST}:{settings.REDIS_PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    global redis_client
    if redis_client:
        await redis_client.aclose()
        logger.info("Processor Wrapper Stopped. Redis connection closed.")

@app.get("/health", tags=["System"])
async def health_check():
    """Healthcheck endpoint for Docker and API Gateway."""
    global redis_client
    try:
        # Check connection to Redis
        await redis_client.ping()
        redis_status = "connected"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "disconnected"
        # We can either return 500 or 200, but to allow Gateway to pass, typically we return 200 with degraded state,
        # or error out if Redis is absolutely critical. Since this is just a processor, we'll return 200 to keep it up.
        # But honestly, returning 503 is more correct for Docker HEALTHCHECK. Let's return 500 if DB is dead.
        return JSONResponse({"status": "Unhealthy", "redis": redis_status}, status_code=500)

    return JSONResponse(
        content={
            "status": "OK",
            "service": "gas-market-data-processor",
            "redis": redis_status,
            "message": "Engine is alive and ready."
        },
        status_code=200
    )
