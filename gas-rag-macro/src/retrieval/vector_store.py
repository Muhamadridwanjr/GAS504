"""
Vector store interface for gas-rag-macro.
Wraps ChromaDB client for document storage and similarity search.
"""
from __future__ import annotations
import hashlib
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    Chroma-backed vector store for macro analysis documents.

    Provides:
        - initialize(): Connect to Chroma and create/get collection.
        - add_documents(): Embed and store documents.
        - similarity_search(): Semantic retrieval by query.
    """

    def __init__(self):
        self._client: chromadb.AsyncHttpClient | None = None
        self._collection = None

    async def initialize(self) -> None:
        """Connect to Chroma and get or create the collection."""
        try:
            self._client = await chromadb.AsyncHttpClient(
                host=settings.VECTOR_DB_URL.replace("http://", "").split(":")[0],
                port=int(settings.VECTOR_DB_URL.split(":")[-1]),
            )
            self._collection = await self._client.get_or_create_collection(
                name=settings.VECTOR_DB_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
            count = await self._collection.count()
            logger.info(
                "vector_store.initialized",
                collection=settings.VECTOR_DB_COLLECTION,
                doc_count=count,
            )
        except Exception as exc:
            logger.warning("vector_store.init_failed", error=str(exc))
            self._client = None
            self._collection = None

    async def add_documents(self, documents: list[dict]) -> int:
        """
        Add a list of documents to the collection.

        Each document dict must have 'content' and optional 'metadata'.
        Returns number of documents added.
        """
        if not self._collection or not documents:
            return 0

        ids, texts, metadatas = [], [], []
        for doc in documents:
            content = doc.get("content", "")
            if not content:
                continue
            doc_id = hashlib.md5(content.encode()).hexdigest()
            ids.append(doc_id)
            texts.append(content)
            metadatas.append(doc.get("metadata", {}))

        if not ids:
            return 0

        try:
            await self._collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
            )
            logger.info("vector_store.add_documents", count=len(ids))
            return len(ids)
        except Exception as exc:
            logger.error("vector_store.add_documents.error", error=str(exc))
            return 0

    async def similarity_search(
        self,
        query: str,
        n_results: int = 5,
        filter_symbol: str | None = None,
    ) -> list[dict]:
        """
        Semantic similarity search.

        Args:
            query: Natural language query string.
            n_results: Number of results to return.
            filter_symbol: Optional symbol to filter by metadata.

        Returns:
            List of dicts with 'content' and 'metadata'.
        """
        if not self._collection:
            return []

        try:
            where = {"symbol": filter_symbol} if filter_symbol else None
            results = await self._collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
            docs = []
            for i, doc in enumerate(results.get("documents", [[]])[0]):
                metadata = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
                docs.append({"content": doc, "metadata": metadata})
            return docs
        except Exception as exc:
            logger.warning("vector_store.search.error", error=str(exc))
            return []
