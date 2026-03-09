from fastapi import Request
from src.core.vector_store import VectorStore

def get_store(request: Request) -> VectorStore:
    return request.app.state.store
