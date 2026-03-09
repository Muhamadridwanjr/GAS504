from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import profiles, health
from src.config import settings
from src.utils.logger import logger
import time

app = FastAPI(
    title=settings.APP_NAME,
    description="GAS User Service - Profil & Data Pengguna",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=int(duration * 1000),
        user_id=getattr(request.state, "user_id", None)
    )
    return response

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])

@app.on_event("startup")
async def startup_event():
    logger.info("service_started", app_name=settings.APP_NAME, debug=settings.DEBUG)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
