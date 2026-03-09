from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    type: str = Field(..., description="Jenis analisis: 'technical', 'macro', 'general'")
    prompt: str = Field(..., description="Teks pertanyaan atau perintah untuk dianalisis oleh model")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Data tambahan (opsional)")
    model_params: Optional[Dict[str, Any]] = Field(default=None, description="Parameter eksekusi model (opsional)")

class AnalysisResult(BaseModel):
    summary: str
    confidence: float
    levels: Optional[Dict[str, Any]] = None
    model: Optional[str] = None

class AnalysisResponse(BaseModel):
    id: str
    type: str
    result: AnalysisResult
    sources: Optional[List[str]] = []
    created_at: str

class EmbedRequest(BaseModel):
    documents: List[str]
    ids: Optional[List[str]] = None
    metadatas: Optional[List[Dict[str, Any]]] = None
    collection: Optional[str] = "gas_knowledge_base"

class EmbedResponse(BaseModel):
    success: bool
    message: str
    count: int
