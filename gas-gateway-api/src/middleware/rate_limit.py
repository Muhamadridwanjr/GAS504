from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.services.redis_client import redis_client
from src.utils.logger import logger
import time

RATE_LIMIT = 10000 # requests
WINDOW = 60 # seconds

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Identify client (User ID from JWT or IP)
        client_id = "unknown"
        if request.client:
            client_id = request.client.host
            
        if hasattr(request.state, "user"):
            client_id = request.state.user.get("sub", client_id)

        key = f"rate_limit:{client_id}"
        
        try:
            # Check if redis is actually connected
            if not redis_client.client:
                return await call_next(request)

            current = await redis_client.get(key)
            
            if current and int(current) >= RATE_LIMIT:
                logger.warning("Rate limit exceeded", client_id=client_id, path=request.url.path)
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

            # Sliding window implementation (simple version with incr + expire)
            pipe = await redis_client.pipeline()
            await pipe.incr(key)
            await pipe.expire(key, WINDOW)
            await pipe.execute()
            
        except HTTPException:
            raise
        except Exception as e:
            # Don't block request if Redis is down, but log error
            logger.error("Rate limit middleware error", error=str(e))
            return await call_next(request)

        return await call_next(request)
