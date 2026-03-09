import httpx
from typing import List, Dict, Any
from src.config import settings
from src.lib.logger import logger

class VectorDBClient:
    def __init__(self):
        self.base_url = settings.vector_db_url
        self.collection = settings.vector_db_collection

    async def search_similar(self, features: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        Queries gas-vector-db for similar patterns given a feature vector.
        """
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/collections/{self.collection}/search",
                    json={
                        "vector": features,
                        "top_k": top_k
                    },
                    timeout=5.0
                )
                
            if res.status_code == 200:
                data = res.json()
                # Assuming the vector DB returns a list of matched documents
                return data.get("results", [])
            else:
                logger.error(f"Vector DB search failed: {res.status_code} {res.text}")
                return []
                
        except httpx.ConnectError:
            logger.warning("gas-vector-db unreachable. Running with empty results.")
            return []
        except Exception as e:
            logger.error(f"Error querying vector DB: {e}")
            return []

vector_client = VectorDBClient()
