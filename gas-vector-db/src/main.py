from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import settings
from src.lib.logger import logger
from src.core.vector_store import VectorStore
from src.api.routes import collections, documents, query

import logging

# Set up logging for Uvicorn
logging.getLogger("uvicorn.error").setLevel(settings.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting gas-vector-db service...")
    try:
        app.state.store = VectorStore()
        logger.info("VectorStore initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize VectorStore: {e}")
        # Could choose to not start the app if DB connection fails right away
    yield
    logger.info("Shutting down gas-vector-db service...")

app = FastAPI(
    title="GAS Vector DB",
    description="Vector database service based on ChromaDB for long-term memory.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(collections.router)
app.include_router(documents.router)
app.include_router(query.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
