"""
FastAPI entry point for gas-rag-macro.
Initializes vector store, market data client, provider router, RAG engine, and all routes.
"""
from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.retrieval.vector_store import VectorStore
from src.fetchers.market import MarketDataClient
from src.providers.router import ProviderRouter
from src.core.rag_engine import RAGEngine
from src.api.routes import analyze as analyze_router
from src.api.routes import admin as admin_router
from src.api.models import HealthResponse
from src.lib.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info(
        "Starting %s on port %d [%s]",
        settings.SERVICE_NAME,
        settings.PORT,
        settings.ENVIRONMENT,
    )

    # Initialize components
    vector_store = VectorStore()
    await vector_store.initialize()

    market_client = MarketDataClient()
    provider_router = ProviderRouter()

    engine = RAGEngine(
        vector_store=vector_store,
        market_client=market_client,
        provider_router=provider_router,
    )
    await engine.init_cache()

    # Store on app state for dependency injection
    app.state.rag_engine = engine
    app.state.vector_store = vector_store
    app.state.market_client = market_client

    # Start background indexer (non-blocking)
    indexer_task: asyncio.Task | None = None
    if settings.ENVIRONMENT != "testing":
        from src.knowledge.indexer import run_background_indexer
        indexer_task = asyncio.create_task(
            run_background_indexer(vector_store=vector_store)
        )

    logger.info("%s ready ✓", settings.SERVICE_NAME)
    yield

    # Cleanup
    if indexer_task:
        indexer_task.cancel()
    await market_client.close()
    logger.info("%s shutdown complete.", settings.SERVICE_NAME)


app = FastAPI(
    title="gas-rag-macro",
    description=(
        "AI-powered macroeconomic analysis service using Retrieval-Augmented Generation (RAG). "
        "Analyzes news sentiment, economic calendar events, and macro data to provide "
        "structured trading insights. Supports Vertex AI (Gemini) and OpenAI providers."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(analyze_router.router)
app.include_router(admin_router.router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check – returns 200 OK when service is running."""
    return HealthResponse(
        status="ok",
        service=settings.SERVICE_NAME,
        version="1.0.0",
        environment=settings.ENVIRONMENT,
    )
