"""
Admin routes – knowledge base management (protected endpoints).
"""
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from src.api.dependencies import verify_internal_key
from src.api.models import KnowledgeStats
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(dependencies=[Depends(verify_internal_key)])


@router.post(
    "/knowledge/update",
    summary="Trigger manual knowledge base re-index",
    tags=["Admin"],
)
async def update_knowledge(background_tasks: BackgroundTasks):
    """Trigger a background re-index of the knowledge base."""
    from src.knowledge.indexer import index_documents

    background_tasks.add_task(index_documents)
    return {"status": "indexing_started", "message": "Knowledge base re-indexing triggered."}


@router.get(
    "/knowledge/stats",
    response_model=KnowledgeStats,
    summary="Knowledge base statistics",
    tags=["Admin"],
)
async def knowledge_stats(request: Request):
    """Return statistics about the current knowledge base."""
    engine = request.app.state.rag_engine
    stats = await engine._store.get_stats()
    return KnowledgeStats(
        document_count=stats.get("count", 0),
        vector_db_type=stats.get("type", "unknown"),
        status=stats.get("status", "unknown"),
    )
