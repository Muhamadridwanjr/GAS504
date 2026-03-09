import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.lib.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"→ {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"✗ {request.method} {request.url.path} - Error: {e}")
            raise
        
        # Log response
        process_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({process_time}ms)")
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
