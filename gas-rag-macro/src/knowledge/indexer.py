"""
Background knowledge base indexer for gas-rag-macro.
Periodically loads documents from disk and indexes them into the vector store.
"""
from __future__ import annotations
import asyncio

from src.config import settings
from src.lib.logger import get_logger
from src.knowledge.document_loader import load_documents

logger = get_logger(__name__)


async def index_knowledge_base(vector_store) -> int:
    """
    Load and index all documents from the knowledge base directory.

    Args:
        vector_store: Initialized VectorStore instance.

    Returns:
        Number of document chunks indexed.
    """
    logger.info("indexer.start", path=settings.KNOWLEDGE_BASE_PATH)
    documents = load_documents()
    if not documents:
        logger.info("indexer.no_documents")
        return 0

    count = await vector_store.add_documents(documents)
    logger.info("indexer.complete", indexed=count)
    return count


async def run_background_indexer(vector_store=None) -> None:
    """
    Long-running background task: re-indexes the knowledge base periodically.
    Requires the app state to provide the vector_store.
    This function is intended to be called as an asyncio task from lifespan.

    Args:
        vector_store: VectorStore instance (passed from lifespan context).
    """
    interval = settings.INDEXING_INTERVAL
    logger.info("indexer.background.started", interval_s=interval)

    while True:
        try:
            if vector_store:
                await index_knowledge_base(vector_store)
        except asyncio.CancelledError:
            logger.info("indexer.background.cancelled")
            break
        except Exception as exc:
            logger.error("indexer.background.error", error=str(exc))

        await asyncio.sleep(interval)
