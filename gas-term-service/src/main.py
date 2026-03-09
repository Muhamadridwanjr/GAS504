import uvicorn
from fastapi import FastAPI
from src.api.routes import router
from src.config import settings
from src.db.database import engine
from src.db.models import Base

app = FastAPI(title="GAS Terminal Service")

@app.on_event("startup")
async def startup():
    # Auto migrate for development (in production use Alembic)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error initializing database: {e}")

app.include_router(router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "gas-term-service"
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=(settings.environment == "development")
    )
