"""
Retrieval strategies: semantic search + temporal + hybrid.
Wraps VectorStore with higher-level query logic.
"""
from __future__ import annotations
from typing import Any
from src.retrieval.vector_store import VectorStore
from src.retrieval.embeddings import get_embedding
from src.lib.logger import get_logger

logger = get_logger(__name__)


class TechnicalRetriever:
    """
    High-level retriever with semantic, temporal, and symbol filtering.
    """

    def __init__(self, store: VectorStore) -> None:
        self._store = store

    async def retrieve(
        self,
        query: str,
        symbol: str | None = None,
        timeframe: str | None = None,
        limit: int = 5,
        provider_preference: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant documents using semantic similarity.

        Args:
            query: Natural language query.
            symbol: Filter by trading symbol (e.g. XAUUSD).
            timeframe: Filter by timeframe (e.g. H4).
            limit: Number of documents to return.

        Returns:
            List of document dicts with text, source, relevance score.
        """
        try:
            embedding = await get_embedding(query, provider_preference)
        except Exception as exc:
            logger.error("Embedding failed: %s – returning empty retrieval", exc)
            return []

        # Build metadata filter for Chroma
        where: dict[str, Any] | None = None
        if symbol or timeframe:
            conditions = []
            if symbol:
                conditions.append({"symbol": {"$eq": symbol.upper()}})
            if timeframe:
                conditions.append({"timeframe": {"$eq": timeframe.upper()}})
            if len(conditions) == 1:
                where = conditions[0]
            else:
                where = {"$and": conditions}

        docs = await self._store.query(
            query_embedding=embedding,
            n_results=limit,
            where=where,
        )
        logger.info(
            "Retrieved %d docs for query='%s' symbol=%s tf=%s",
            len(docs), query[:50], symbol, timeframe,
        )
        return docs
