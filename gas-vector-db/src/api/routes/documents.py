from fastapi import APIRouter, Depends
from src.api.models import DocumentUpsert
from src.core.vector_store import VectorStore
from src.api.dependencies import get_store

router = APIRouter(prefix="/collections/{collection}/documents", tags=["Documents"])

@router.post("")
def upsert_documents(
    collection: str,
    request: DocumentUpsert,
    store: VectorStore = Depends(get_store)
):
    docs = []
    for d in request.documents:
        docs.append({
            "id": d.id,
            "embedding": d.embedding,
            "metadata": d.metadata,
            "text": d.text
        })
    
    count = store.upsert_documents(collection_name=collection, documents=docs)
    return {"status": "ok", "count": count}
