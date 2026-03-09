from fastapi import APIRouter, Depends
from src.api.models import QueryRequest, QueryResponse
from src.core.vector_store import VectorStore
from src.api.dependencies import get_store

router = APIRouter(prefix="/collections/{collection}/query", tags=["Query"])

@router.post("", response_model=QueryResponse)
def query_collection(
    collection: str,
    request: QueryRequest,
    store: VectorStore = Depends(get_store)
):
    include = ["distances"]
    if request.include_metadata:
        include.append("metadatas")
    if request.include_documents:
        include.append("documents")

    results = store.query_collection(
        collection_name=collection,
        query_embeddings=[request.embedding],
        n_results=request.top_k,
        where=request.filter,
        include=include
    )

    matches = []
    
    if results and results.get("ids") and len(results["ids"]) > 0:
        ids_list = results["ids"][0]
        distances_list = results.get("distances", [[]])[0]
        metadatas_list = results.get("metadatas", [[]])[0] if results.get("metadatas") else [None] * len(ids_list)
        documents_list = results.get("documents", [[]])[0] if results.get("documents") else [None] * len(ids_list)

        for i in range(len(ids_list)):
            # Fallbacks in case lengths don't match, though Chroma typically returns consistent lists
            dist = distances_list[i] if i < len(distances_list) else 0.0
            # Calculate a similarity score (1 - normalized distance). This depends on space metric.
            # Assuming cosine distance where smaller is closer.
            score = 1 - dist if dist <= 1 else 0.0

            meta = metadatas_list[i] if i < len(metadatas_list) else None
            doc = documents_list[i] if i < len(documents_list) else None

            matches.append({
                "id": ids_list[i],
                "score": score,
                "metadata": meta,
                "document": doc
            })

    return {"matches": matches}
