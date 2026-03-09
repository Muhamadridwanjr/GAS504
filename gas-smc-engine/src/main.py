from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from .models.schemas import DetectRequest, DetectResponse
from .mtf.orchestrator import Orchestrator

app = FastAPI(title="GAS SMC Engine", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "gas-smc-engine"}

@app.post("/detect", response_model=DetectResponse)
def detect_smc(request: DetectRequest):
    try:
        orchestrator = Orchestrator()
        result = orchestrator.analyze(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
