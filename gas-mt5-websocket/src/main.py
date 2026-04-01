from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.tick import router as tick_router
from src.lib.logger import log
from contextlib import asynccontextmanager
from src.redis_client.client import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.connect()
    log.info("Gas MT5 WebSocket Service started")
    yield
    # Shutdown
    await redis_client.close()
    log.info("Gas MT5 WebSocket Service stopped")

app = FastAPI(
    title="GAS MT5 WebSocket Service",
    description="Service untuk menerima data tick dari EA dan meneruskannya ke realtime hub.",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes are included via router
app.include_router(tick_router, prefix="/mt5")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "gas-mt5-websocket", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8110, reload=True)
