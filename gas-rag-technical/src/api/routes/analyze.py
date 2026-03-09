"""
Main analysis routes – POST /analyze, POST /analyze/batch, GET /providers.
"""
from __future__ import annotations
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.api.models import (
    AnalyzeRequest,
    AnalysisResponse,
    BatchAnalyzeRequest,
    ProviderInfo,
)
from src.api.dependencies import get_user_id
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _get_engine(request: Request):
    """Retrieve the shared RAGEngine instance from app state."""
    return request.app.state.rag_engine


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analisis teknikal dengan RAG",
    tags=["Analysis"],
)
async def analyze(
    body: AnalyzeRequest,
    request: Request,
    user_id: str | None = Depends(get_user_id),
):
    """
    Perform AI-powered technical analysis using Retrieval-Augmented Generation.

    - Retrieves relevant documents from the knowledge base
    - Fetches current market data
    - Generates structured analysis via the selected LLM provider
    """
    engine = _get_engine(request)
    logger.info(
        "POST /analyze user=%s symbol=%s tf=%s provider=%s",
        user_id, body.symbol, body.timeframe, body.model_preference,
    )
    try:
        result = await engine.analyze(
            symbol=body.symbol,
            timeframe=body.timeframe,
            query=body.query,
            context=body.context.model_dump() if body.context else {},
            model_preference=body.model_preference,
            include_sources=body.include_sources,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
        )
        return result
    except Exception as exc:
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {exc}",
        ) from exc


@router.post(
    "/analyze/batch",
    summary="Batch analysis untuk multiple simbol",
    tags=["Analysis"],
)
async def batch_analyze(
    body: BatchAnalyzeRequest,
    request: Request,
    user_id: str | None = Depends(get_user_id),
):
    """Run multiple analysis requests concurrently."""
    engine = _get_engine(request)
    if not body.requests:
        raise HTTPException(status_code=400, detail="Empty request list.")
    if len(body.requests) > 10:
        raise HTTPException(status_code=400, detail="Max 10 requests per batch.")

    tasks = [
        engine.analyze(
            symbol=req.symbol,
            timeframe=req.timeframe,
            query=req.query,
            context=req.context.model_dump() if req.context else {},
            model_preference=req.model_preference,
            include_sources=req.include_sources,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
        for req in body.requests
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return {
        "results": [
            r if not isinstance(r, Exception) else {"error": str(r)}
            for r in results
        ]
    }


@router.get("/providers", summary="List provider yang tersedia", tags=["Info"])
async def list_providers(request: Request):
    """Return available LLM providers and their status."""
    from src.config import settings

    providers = [
        ProviderInfo(
            name="openai",
            model=settings.OPENAI_MODEL,
            available=bool(settings.OPENAI_API_KEY),
        ),
        ProviderInfo(
            name="vertex",
            model=settings.VERTEX_MODEL,
            available=bool(settings.VERTEX_PROJECT_ID),
        ),
    ]
    return {"providers": [p.model_dump() for p in providers]}
