"""
Background knowledge base indexer.
Loads documents, chunks them, generates embeddings, and upserts into vector store.
Can be run as a one-time init or on a schedule.
"""
from __future__ import annotations
import asyncio
import argparse
import time
from src.config import settings
from src.retrieval.vector_store import VectorStore
from src.retrieval.embeddings import get_embedding
from src.knowledge.document_loader import load_documents
from src.knowledge.chunker import chunk_text
from src.lib.logger import get_logger

logger = get_logger(__name__)


async def index_documents(
    base_path: str | None = None,
    provider_preference: str | None = None,
) -> int:
    """
    Full indexing pipeline: load → chunk → embed → store.

    Returns:
        Number of chunks indexed.
    """
    store = VectorStore()
    await store.initialize()

    docs = load_documents(base_path)
    if not docs:
        logger.info("No documents found to index.")
        return 0

    total = 0
    for doc in docs:
        chunks = chunk_text(doc.text)
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            try:
                embedding = await get_embedding(chunk, provider_preference)
                chunk_id = f"{doc.metadata.get('source', 'doc')}::{i}"
                await store.add_documents(
                    texts=[chunk],
                    embeddings=[embedding],
                    metadatas=[{**doc.metadata, "chunk_index": i}],
                    ids=[chunk_id[:63]],   # Chroma ID length limit
                )
                total += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to index chunk %d of %s: %s", i, doc.metadata.get("source"), exc)

    logger.info("Indexing complete: %d chunks indexed.", total)
    return total


async def run_background_indexer() -> None:
    """Continuously re-index the knowledge base at INDEXING_INTERVAL."""
    while True:
        logger.info("Starting scheduled knowledge base indexing...")
        try:
            await index_documents()
        except Exception as exc:  # noqa: BLE001
            logger.error("Indexing failed: %s", exc)
        await asyncio.sleep(settings.INDEXING_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Knowledge Base Indexer")
    parser.add_argument("--init", action="store_true", help="Run a single indexing pass and exit.")
    args = parser.parse_args()

    if args.init:
        asyncio.run(index_documents())
    else:
        asyncio.run(run_background_indexer())
