from fastapi import APIRouter, Depends, HTTPException
from src.api.models import AnalysisRequest, AnalysisResponse, EmbedRequest, EmbedResponse
from src.api.dependencies import get_user_id
from src.core.orchestrator import orchestrator
from src.rag.vector_store import vector_store
from src.core.exceptions import ModelNotFoundError, OrchestratorException
from src.lib.logger import setup_logger
import uuid

logger = setup_logger(__name__)

router = APIRouter(prefix="", tags=["analyze"])

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(request: AnalysisRequest, user_id: str = Depends(get_user_id)):
    """
    Endpoint utama untuk menerima prompt dari pengguna (API Gateway).
    """
    logger.info(f"Received /analyze request for type: {request.type}")
    try:
        result = await orchestrator.analyze(
            prompt=request.prompt,
            ai_type=request.type,
            user_id=user_id,
            context=request.context,
            model_params=request.model_params
        )
        return result
    except ModelNotFoundError as e:
        logger.error(f"Model error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except OrchestratorException as e:
         logger.error(f"Orchestration error: {str(e)}")
         raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /analyze: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/embed", response_model=EmbedResponse)
async def embed_endpoint(request: EmbedRequest):
    """
    (Opsional) Menambahkan dokumen ke RAG vector database. 
    Idealnya memiliki proteksi API Key tersendiri.
    """
    logger.info(f"Received /embed request with {len(request.documents)} documents.")
    
    ids = request.ids or [str(uuid.uuid4()) for _ in request.documents]
    success = vector_store.add(
        collection_name=request.collection,
        documents=request.documents,
        ids=ids,
        metadatas=request.metadatas
    )
    
    if not success:
         raise HTTPException(status_code=500, detail="Failed to embed documents into Vector DB")
         
    return EmbedResponse(success=True, message="Documents successfully embedded", count=len(request.documents))
    
@router.get("/health")
async def health_check():
    """Endpoint health check sederhana."""
    return {"status": "ok", "service": "gas-ai-orchestrator"}
