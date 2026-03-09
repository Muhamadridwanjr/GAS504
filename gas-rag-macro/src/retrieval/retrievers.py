"""
Higher-level retrieval logic for gas-rag-macro.
Provides convenience wrappers over VectorStore.
"""
from __future__ import annotations

from src.retrieval.vector_store import VectorStore
from src.lib.logger import get_logger

logger = get_logger(__name__)


class MacroRetriever:
    """
    Semantic retriever for macro analysis documents.
    Filters by symbol metadata and ranks by relevance.
    """

    def __init__(self, vector_store: VectorStore):
        self._vs = vector_store

    async def retrieve(
        self,
        query: str,
        symbol: str | None = None,
        n_results: int = 5,
    ) -> list[dict]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Natural language query.
            symbol: Optional trading symbol filter.
            n_results: Number of results.

        Returns:
            List of document dicts with 'content' and 'metadata'.
        """
        return await self._vs.similarity_search(
            query=query,
            n_results=n_results,
            filter_symbol=symbol,
        )
