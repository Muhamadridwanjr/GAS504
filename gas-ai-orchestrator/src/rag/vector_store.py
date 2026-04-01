import httpx
from typing import List, Optional
from src.config import settings
from src.lib.logger import setup_logger

logger = setup_logger(__name__)

BASE_URL = settings.vector_db_url.rstrip("/")
TIMEOUT = 5.0


def _get_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding via OpenAI. Returns None jika key tidak dikonfigurasi."""
    if not settings.openai_api_key:
        return None
    try:
        resp = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={"input": text, "model": "text-embedding-3-small"},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as e:
        logger.warning(f"Embedding generation failed: {e}")
        return None


class VectorStore:
    def __init__(self):
        self._check_connection()

    def _check_connection(self):
        try:
            resp = httpx.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            if resp.status_code == 200:
                logger.info(f"Vector DB connected at {BASE_URL}")
            else:
                logger.warning(f"Vector DB at {BASE_URL} returned HTTP {resp.status_code}")
        except Exception as e:
            logger.warning(f"Vector DB unreachable at {BASE_URL}: {e} — RAG disabled")

    def query(self, collection_name: str, query_text: str, n_results: int = 3) -> List[str]:
        embedding = _get_embedding(query_text)
        if embedding is None:
            logger.debug("No OpenAI key — skipping vector query, returning empty context")
            return []

        try:
            resp = httpx.post(
                f"{BASE_URL}/collections/{collection_name}/query",
                json={
                    "embedding": embedding,
                    "top_k": n_results,
                    "include_documents": True,
                    "include_metadata": False,
                },
                timeout=TIMEOUT,
            )
            if resp.status_code == 404:
                logger.debug(f"Collection '{collection_name}' not found in Vector DB")
                return []
            resp.raise_for_status()
            matches = resp.json().get("matches", [])
            return [m["document"] for m in matches if m.get("document")]
        except Exception as e:
            logger.warning(f"Vector DB query error: {e}")
            return []

    def add(
        self,
        collection_name: str,
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> bool:
        if not documents:
            return True

        items = []
        for i, (doc_id, text) in enumerate(zip(ids, documents)):
            embedding = _get_embedding(text)
            if embedding is None:
                logger.debug("No OpenAI key — skipping vector add")
                return False
            items.append({
                "id": doc_id,
                "embedding": embedding,
                "text": text,
                "metadata": metadatas[i] if metadatas and i < len(metadatas) else None,
            })

        try:
            resp = httpx.post(
                f"{BASE_URL}/collections/{collection_name}/documents",
                json={"documents": items},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"Vector DB add error: {e}")
            return False


vector_store = VectorStore()
