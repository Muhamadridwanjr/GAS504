"""
Embedding generation and vector DB storage client.
"""
from __future__ import annotations

import httpx

from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class VectorEmbedder:
    """Send summaries with embeddings to gas-vector-db."""

    def __init__(self):
        self.vector_db_url = settings.VECTOR_DB_URL.rstrip("/")
        self.collection = settings.VECTOR_DB_COLLECTION

    async def send_summaries(self, summaries: list[dict]) -> int:
        """
        Send a list of summaries to the vector DB.

        Each summary dict should have keys: period_label, text, metadata.

        Returns:
            Number of successfully stored documents.
        """
        if not summaries:
            return 0

        url = f"{self.vector_db_url}/collections/{self.collection}/documents"
        success = 0

        async with httpx.AsyncClient(timeout=30) as client:
            for s in summaries:
                payload = {
                    "id": f"{s['metadata']['symbol']}_{s['period_label']}",
                    "content": s["text"],
                    "metadata": s["metadata"],
                }
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code in (200, 201):
                        success += 1
                    else:
                        logger.warning(
                            "Vector DB returned %d for %s", resp.status_code, payload["id"]
                        )
                except httpx.HTTPError as e:
                    logger.error("Failed to send to vector DB: %s", e)

        logger.info("Stored %d / %d summaries in vector DB", success, len(summaries))
        return success
