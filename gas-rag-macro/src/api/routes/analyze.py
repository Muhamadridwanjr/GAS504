"""
Analyze routes for gas-rag-macro.
POST /macro/analyze  – main RAG analysis endpoint
GET  /providers      – list available AI providers
"""
from __future__ import annotations
import uuid
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from src.api.models import (
    MacroAnalyzeRequest,
    MacroAnalyzeResponse,
    ProvidersResponse,
    ProviderInfo,
)
from src.api.dependencies import get_user_id
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/macro", tags=["Macro Analysis"])


@router.post("/analyze", response_model=MacroAnalyzeResponse)
async def analyze(
    body: MacroAnalyzeRequest,
    request: Request,
    user_id: str = Depends(get_user_id),
):
    """
    Run a macroeconomic RAG analysis for a given trading symbol.

    The pipeline:
    1. Fetch latest news articles.
    2. Fetch upcoming economic calendar events.
    3. Fetch current market price data.
    4. Retrieve semantically similar documents from the vector store.
    5. Build context and generate analysis via the selected AI provider.
    6. Return structured response with summary, sentiment, key factors, etc.
    """
    engine = request.app.state.rag_engine
    start = time.monotonic()

    logger.info("macro.analyze", symbol=body.symbol, user_id=user_id or "anonymous")

    try:
        result = await engine.analyze(body)
    except Exception as exc:
        logger.error("macro.analyze.error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    elapsed_ms = int((time.monotonic() - start) * 1000)
    result.processing_time_ms = elapsed_ms
    return result


@router.get("/providers", response_model=ProvidersResponse, tags=["Info"])
async def list_providers():
    """Return a list of configured AI providers and their availability."""
    providers = [
        ProviderInfo(
            name="openai",
            available=bool(settings.OPENAI_API_KEY),
            model=settings.OPENAI_MODEL,
        ),
        ProviderInfo(
            name="vertex",
            available=bool(settings.VERTEX_PROJECT_ID and settings.GOOGLE_APPLICATION_CREDENTIALS),
            model=settings.VERTEX_MODEL,
        ),
    ]
    return ProvidersResponse(providers=providers, default=settings.DEFAULT_PROVIDER)
