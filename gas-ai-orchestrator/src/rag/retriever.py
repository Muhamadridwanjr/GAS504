from typing import List
from src.rag.vector_store import vector_store
from src.lib.logger import setup_logger

logger = setup_logger(__name__)

class Retriever:
    """Class utilitas untuk menyusun konteks (RAG) dari pencarian VectorStore."""
    
    def __init__(self, default_collection: str = "gas_knowledge_base"):
        self.default_collection = default_collection

    def get_context(self, query: str, top_k: int = 3, collection: str = None) -> List[str]:
        """
        Mengambil teks dokumen dari vector DB berdasarkan query string.
        """
        target_collection = collection or self.default_collection
        logger.info(f"Retrieving top {top_k} contexts from {target_collection} for query")
        
        results = vector_store.query(
            collection_name=target_collection,
            query_text=query,
            n_results=top_k
        )
        return results
        
retriever = Retriever()
