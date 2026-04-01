import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router, start_cache_refresher
from .core.publisher import publisher
from .core.binance_client import binance_client
from .streams.websocket_manager import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting gas-binance-service...")
    await publisher.connect()
    await binance_client.load_markets()
    start_cache_refresher()   # start background ticker cache refresh (every 5s)
    await ws_manager.start()
    yield
    # Shutdown
    logger.info("Shutting down gas-binance-service...")
    await ws_manager.stop()
    await binance_client.close()
    await publisher.disconnect()

app = FastAPI(title="GAS Binance Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=9612, reload=True)
