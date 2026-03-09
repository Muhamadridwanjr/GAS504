import uvicorn
from fastapi import FastAPI
from src.api.routes import router
from src.config import settings

app = FastAPI(
    title="GAS Terminal Service",
    description="Bloomberg-like Financial Command Center for the GAS Ecosystem"
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "gas-terminal-service"
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=(settings.environment == "development")
    )
