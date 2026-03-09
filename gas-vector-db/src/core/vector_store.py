import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from src.config import settings
from src.lib.logger import logger
from src.core.exceptions import CollectionNotFoundException, ChromaConnectionError, InvalidRequestException

class VectorStore:
    def __init__(self):
        try:
            logger.info(f"Connecting to ChromaDB at {settings.CHROMA_HOST}:{settings.CHROMA_PORT} (SSL: {settings.CHROMA_SSL})")
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                ssl=settings.CHROMA_SSL,
                settings=ChromaSettings(allow_reset=True)
            )
            # Ping to verify connection
            self.client.heartbeat()
            logger.info("Successfully connected to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise ChromaConnectionError(f"Connection failed: {str(e)}")

    def list_collections(self) -> List[Dict[str, Any]]:
        try:
            collections = self.client.list_collections()
            results = []
            for col in collections:
                results.append({
                    "name": col.name,
                    "count": col.count(),
                    "dimension": col.metadata.get("hnsw:space") if col.metadata else None
                })
            return results
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            raise ChromaConnectionError(f"Error listing collections: {str(e)}")

    def create_collection(self, name: str, dimension: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        try:
            actual_meta = metadata or {}
            # If we need to enforce a specific space or metric, we can add it here.
            # E.g., actual_meta["hnsw:space"] = "cosine"
            self.client.create_collection(name=name, metadata=actual_meta)
            logger.info(f"Created collection: {name}")
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            raise InvalidRequestException(f"Could not create collection: {str(e)}")

    def delete_collection(self, name: str) -> None:
        try:
            self.client.delete_collection(name)
            logger.info(f"Deleted collection: {name}")
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {e}")
            raise CollectionNotFoundException(name)

    def upsert_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> int:
        try:
            col = self.client.get_collection(collection_name)
        except Exception:
            raise CollectionNotFoundException(collection_name)

        ids = [doc["id"] for doc in documents]
        embeddings = [doc["embedding"] for doc in documents]
        
        # ChromaDB requires non-empty dicts if metadatas are provided
        metadatas = []
        has_metadata = False
        for doc in documents:
            meta = doc.get("metadata")
            if meta and isinstance(meta, dict) and len(meta) > 0:
                metadatas.append(meta)
                has_metadata = True
            else:
                metadatas.append({"_empty": True})
        
        # Or if we want to be clean, if none have metadata, pass None
        if not has_metadata:
            metadatas = None

        # Treat text as optional
        documents_text = [doc.get("text") or "" for doc in documents]

        try:
            col.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text
            )
            logger.info(f"Upserted {len(ids)} documents into {collection_name}")
            return len(ids)
        except Exception as e:
            logger.error(f"Error upserting documents to {collection_name}: {e}")
            raise InvalidRequestException(f"Error upserting documents: {str(e)}")

    def query_collection(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        try:
            col = self.client.get_collection(collection_name)
        except Exception:
            raise CollectionNotFoundException(collection_name)

        if not include:
            include = ["metadatas", "distances"]

        try:
            results = col.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=include
            )
            return results
        except Exception as e:
            logger.error(f"Error querying collection {collection_name}: {e}")
            raise InvalidRequestException(f"Error querying collection: {str(e)}")
