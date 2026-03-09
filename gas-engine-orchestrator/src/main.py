from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.api.middleware import ExceptionMiddleware, JWTAuthMiddleware, RequestLogMiddleware
from src.lib.logger import log

app = FastAPI(
    title="GAS Engine Orchestrator",
    description="Orkestrasi alur analisis teknikal dan SMC",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan spesifik asal (e.g. ['http://localhost:3000']) di prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(ExceptionMiddleware)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(JWTAuthMiddleware)

# Include routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    log.info("GAS Engine Orchestrator starting up...")
    
@app.on_event("shutdown")
async def shutdown_event():
    log.info("GAS Engine Orchestrator shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8105, reload=True)
