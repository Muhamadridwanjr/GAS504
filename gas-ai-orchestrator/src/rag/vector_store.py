import chromadb
from typing import List, Optional
from src.config import settings
from src.lib.logger import setup_logger

logger = setup_logger(__name__)

class VectorStore:
    def __init__(self):
        self._init_client()
        
    def _init_client(self):
        if settings.vector_db_type.lower() == "chroma":
            logger.info(f"Initializing ChromaDB client at {settings.vector_db_url}")
            try:
                # Basic initialization mapping for chromadb.HttpClient
                # Assuming the vector_db_url contains scheme, host, port
                import urllib.parse
                parsed = urllib.parse.urlparse(settings.vector_db_url)
                
                self.client = chromadb.HttpClient(
                    host=parsed.hostname or "localhost",
                    port=parsed.port or 8000
                )
            except Exception as e:
                logger.error(f"Failed to initialize Vector DB: {e}")
                self.client = None
        else:
            logger.warning(f"Vector DB type {settings.vector_db_type} is not yet supported")
            self.client = None

    def query(self, collection_name: str, query_text: str, n_results: int = 3) -> List[str]:
        if not self.client:
            logger.error("Vector DB Client is not initialized.")
            return []
            
        try:
            collection = self.client.get_or_create_collection(name=collection_name)
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            # Flatten array of documents
            if results and 'documents' in results and len(results['documents']) > 0:
                return [doc for doc in results['documents'][0] if doc]
            return []
        except Exception as e:
            logger.error(f"Error querying Vector DB: {e}")
            return []
            
    def add(self, collection_name: str, documents: List[str], ids: List[str], metadatas: Optional[List[dict]] = None):
        if not self.client:
            logger.error("Vector DB Client is not initialized.")
            return False
            
        try:
            collection = self.client.get_or_create_collection(name=collection_name)
            collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            logger.error(f"Error adding to Vector DB: {e}")
            return False

vector_store = VectorStore()
