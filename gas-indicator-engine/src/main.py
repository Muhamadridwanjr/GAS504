import argparse
import uvicorn
from src.lib.logger import log
from src.lib.config import settings
from src.api.rest_server import app

def start_rest():
    log.info(f"Starting REST API on port {settings.REST_PORT} (Environment: {settings.ENVIRONMENT})")
    uvicorn.run(app, host="0.0.0.0", port=settings.REST_PORT)

def start_grpc():
    log.info(f"Starting gRPC server on port {settings.GRPC_PORT} (Environment: {settings.ENVIRONMENT})")
    from src.api.grpc_server import serve
    serve()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start GAS Indicator Engine")
    parser.add_argument("--mode", type=str, choices=["rest", "grpc", "both"], default="rest", help="Running mode")
    args = parser.parse_args()

    if args.mode == "rest":
        start_rest()
    elif args.mode == "grpc":
        start_grpc()
    else:
        log.error("Running both in same process is not highly recommended via code, use docker-compose or shell script.")
