import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Extract metadata
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "127.0.0.1"
        
        logger.info("Request started", method=method, path=path, client_ip=client_ip)
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        
        # Log response
        user_id = getattr(request.state, "user", {}).get("sub", "anonymous")
        
        logger.info(
            "Request finished",
            method=method,
            path=path,
            status_code=response.status_code,
            duration=f"{process_time:.4f}s",
            user_id=user_id
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
