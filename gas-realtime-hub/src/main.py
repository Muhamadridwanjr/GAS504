import uvicorn
from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.server.websocket_server:app",
        host="0.0.0.0",
        port=settings.port,
        reload=(settings.environment == "development")
    )
