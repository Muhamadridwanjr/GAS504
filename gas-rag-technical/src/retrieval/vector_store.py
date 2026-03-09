"""
Vector store interface – wraps ChromaDB (default) / FAISS.
Provides add, query, and delete operations on the knowledge base.
"""
from __future__ import annotations
import os
from typing import Any
from src.config import settings
from src.core.exceptions import VectorStoreError
from src.lib.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    Abstraction over the underlying vector database.
    Supports chroma (HTTP client), faiss (local), or mocked for testing.
    """

    def __init__(self) -> None:
        self._collection_name = settings.VECTOR_DB_COLLECTION
        self._client: Any = None
        self._collection: Any = None
        self._faiss_index: Any = None
        self._faiss_docs: list[dict] = []

    # ─── Lifecycle ────────────────────────────────────────────────────────

    async def initialize(self) -> None:
        """Connect to the chosen vector database backend."""
        db_type = settings.VECTOR_DB_TYPE
        if db_type == "chroma":
            await self._init_chroma()
        elif db_type == "faiss":
            await self._init_faiss()
        else:
            raise VectorStoreError(f"Unsupported VECTOR_DB_TYPE: {db_type}")
        logger.info("VectorStore initialized [type=%s, collection=%s]", db_type, self._collection_name)

    async def _init_chroma(self) -> None:
        try:
            import chromadb
            self._client = chromadb.HttpClient(
                host=settings.VECTOR_DB_URL.replace("http://", "").split(":")[0],
                port=int(settings.VECTOR_DB_URL.split(":")[-1]),
            )
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            # Dev fallback: use local in-memory Chroma
            logger.warning("HTTP Chroma unavailable, using in-memory. Reason: %s", exc)
            try:
                import chromadb
                self._client = chromadb.EphemeralClient()
                self._collection = self._client.get_or_create_collection(name=self._collection_name)
            except ImportError:
                logger.warning("chromadb not installed – VectorStore will be disabled.")

    async def _init_faiss(self) -> None:
        try:
            import faiss  # noqa: F401
            self._faiss_docs = []
        except ImportError:
            logger.warning("faiss-cpu not installed – VectorStore will be disabled.")

    # ─── Operations ───────────────────────────────────────────────────────

    async def add_documents(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> None:
        """Upsert documents into the vector store."""
        if self._collection is None:
            logger.warning("VectorStore not available – skipping add.")
            return
        metadatas = metadatas or [{}] * len(texts)
        ids = ids or [f"doc_{i}" for i in range(len(texts))]
        try:
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
        except Exception as exc:
            raise VectorStoreError(f"Failed to add documents: {exc}") from exc

    async def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Semantic search: return top-n most similar documents.

        Returns:
            List of dicts with 'text', 'metadata', 'score' keys.
        """
        if self._collection is None:
            return []
        try:
            kwargs: dict[str, Any] = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"],
            }
            if where:
                kwargs["where"] = where

            results = self._collection.query(**kwargs)
            docs = []
            for i, text in enumerate(results["documents"][0]):
                score = 1.0 - (results["distances"][0][i] / 2)   # cosine -> similarity
                docs.append({
                    "text": text,
                    "metadata": results["metadatas"][0][i],
                    "score": round(score, 4),
                    "relevance": round(score, 4),
                    "source": results["metadatas"][0][i].get("source", "Unknown"),
                    "title": results["metadatas"][0][i].get("title", "Document"),
                })
            return docs
        except Exception as exc:
            logger.error("VectorStore query failed: %s", exc)
            return []

    async def get_stats(self) -> dict[str, Any]:
        if self._collection is None:
            return {"type": settings.VECTOR_DB_TYPE, "count": 0, "status": "unavailable"}
        try:
            count = self._collection.count()
            return {"type": settings.VECTOR_DB_TYPE, "count": count, "status": "ok"}
        except Exception:
            return {"type": settings.VECTOR_DB_TYPE, "count": -1, "status": "error"}
