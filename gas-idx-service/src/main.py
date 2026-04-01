from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

app = FastAPI(
    title="GAS IDX Service",
    description="Indonesian Stock Exchange (IDX) data: OHLCV, indicators, SMC, AI signals",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "gas-idx-service"}
