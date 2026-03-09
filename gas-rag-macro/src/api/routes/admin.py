"""
Admin routes for gas-rag-macro.
POST /knowledge/update – trigger manual re-indexing of knowledge base.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from src.api.models import KnowledgeUpdateResponse
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/knowledge", tags=["Admin"])


def _check_internal_key(request: Request) -> None:
    key = request.headers.get("X-API-Key", "")
    if key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden – invalid internal API key")


@router.post("/update", response_model=KnowledgeUpdateResponse)
async def update_knowledge(request: Request):
    """
    Trigger a manual re-index of the knowledge base from disk.
    Requires X-API-Key header matching INTERNAL_API_KEY.
    """
    _check_internal_key(request)
    vector_store = request.app.state.vector_store

    try:
        from src.knowledge.indexer import index_knowledge_base
        count = await index_knowledge_base(vector_store)
    except Exception as exc:
        logger.error("knowledge.update.error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Indexing failed: {exc}")

    return KnowledgeUpdateResponse(
        status="ok",
        message="Knowledge base updated successfully",
        documents_indexed=count,
    )
