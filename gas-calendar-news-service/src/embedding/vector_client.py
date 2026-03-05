"""Client to send embeddings to gas-vector-db."""
import httpx
from src.config import settings
from src.lib.logger import get_logger
logger = get_logger(__name__)

class VectorClient:
    def __init__(self):
        self.url = settings.VECTOR_DB_URL.rstrip("/")
        self.collection = settings.VECTOR_DB_COLLECTION

    async def store_document(self, doc_id: str, content: str, metadata: dict):
        url = f"{self.url}/collections/{self.collection}/documents"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, json={"id": doc_id, "content": content, "metadata": metadata})
                return resp.status_code in (200, 201)
        except Exception as e:
            logger.error("Vector DB store failed: %s", e)
            return False
