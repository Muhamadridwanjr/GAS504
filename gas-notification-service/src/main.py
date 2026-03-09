import uvicorn
from fastapi import FastAPI
from src.api.routes import router
from src.config import settings

app = FastAPI(title="GAS Notification Service")

# Include routes
app.include_router(router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "gas-notification-service"
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=(settings.environment == "development")
    )
