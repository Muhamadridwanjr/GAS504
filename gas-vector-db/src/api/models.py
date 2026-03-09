from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class CollectionCreate(BaseModel):
    name: str
    dimension: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class CollectionResponse(BaseModel):
    name: str
    count: int
    dimension: Optional[int] = None

class DocumentItem(BaseModel):
    id: str
    embedding: List[float]
    metadata: Optional[Dict[str, Any]] = None
    text: Optional[str] = None

class DocumentUpsert(BaseModel):
    documents: List[DocumentItem]

class QueryRequest(BaseModel):
    embedding: List[float]
    filter: Optional[Dict[str, Any]] = None
    top_k: int = 10
    include_metadata: bool = True
    include_documents: bool = False

class MatchItem(BaseModel):
    id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    document: Optional[str] = None

class QueryResponse(BaseModel):
    matches: List[MatchItem]
