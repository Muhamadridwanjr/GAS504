#!/bin/bash
set -e

# Start gRPC Server in the background
python src/main.py --mode grpc &

# Start REST Server
exec uvicorn src.main:app --host 0.0.0.0 --port 8203
