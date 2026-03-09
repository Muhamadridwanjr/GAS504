#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

# Ensure destination directory exists
mkdir -p src/models/protobuf

# Try to run python -m grpc_tools.protoc if installed
if python -c "import grpc_tools" &> /dev/null; then
    python -m grpc_tools.protoc -Iproto --python_out=src/models/protobuf --grpc_python_out=src/models/protobuf proto/indicator.proto
    
    # Fix imports in generated files to be absolute (Python 3 issue with protoc)
    sed -i -E 's/^import indicator_pb2 as indicator__pb2/from . import indicator_pb2 as indicator__pb2/' src/models/protobuf/indicator_pb2_grpc.py
    echo "gRPC classes generated successfully."
else
    echo "grpc_tools not found! Please install it via pip install grpcio-tools"
    exit 1
fi
