from fastapi import APIRouter, Depends
from typing import List
from src.api.models import CollectionCreate, CollectionResponse
from src.core.vector_store import VectorStore
from src.api.dependencies import get_store

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.get("", response_model=List[CollectionResponse])
def get_collections(store: VectorStore = Depends(get_store)):
    return store.list_collections()

@router.post("", status_code=201)
def create_collection(request: CollectionCreate, store: VectorStore = Depends(get_store)):
    store.create_collection(
        name=request.name,
        dimension=request.dimension,
        metadata=request.metadata
    )
    return {"status": "created", "name": request.name}

@router.delete("/{name}")
def delete_collection(name: str, store: VectorStore = Depends(get_store)):
    store.delete_collection(name)
    return {"status": "deleted"}
