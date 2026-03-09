import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import analyze
from src.config import settings
from src.lib.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="GAS AI Orchestrator API",
    description="Orchestrator untuk merutekan permintaan prediksi AI ke klien model yang tepat berdasarkan type",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set environment restricted origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)

@app.on_event("startup")
async def startup_event():
    logger.info(f"GAS AI Orchestrator started on PORT: {settings.port}")
    logger.info(f"Environment: {settings.environment}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("GAS AI Orchestrator shutting down")
