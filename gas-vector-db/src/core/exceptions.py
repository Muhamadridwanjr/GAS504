from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

class VectorDBException(Exception):
    """Base exception for gas-vector-db."""
    pass

class CollectionNotFoundException(HTTPException):
    def __init__(self, collection_name: str):
        super().__init__(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Collection '{collection_name}' not found."
        )

class ChromaConnectionError(HTTPException):
    def __init__(self, detail: str = "Failed to connect to ChromaDB"):
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class InvalidRequestException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST,
            detail=detail
        )
