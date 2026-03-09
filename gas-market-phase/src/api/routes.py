from fastapi import APIRouter, HTTPException
from typing import List
from src.api.models import PhaseRequest, PhaseResponse
from src.core.detector import PhaseDetector
from src.core.exceptions import PhaseEngineException

router = APIRouter()
detector = PhaseDetector()

@router.post("/phase", response_model=PhaseResponse)
async def get_phase(request: PhaseRequest):
    try:
        return await detector.get_phase(request.symbol, request.timeframe)
    except PhaseEngineException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/phase/batch", response_model=List[PhaseResponse])
async def get_phase_batch(requests: List[PhaseRequest]):
    results = []
    for req in requests:
        try:
            res = await detector.get_phase(req.symbol, req.timeframe)
            results.append(res)
        except Exception as e:
            # Skip or log failing ones in batch
            pass
    return results

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "gas-market-phase"}
