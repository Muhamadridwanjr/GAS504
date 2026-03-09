#!/bin/bash
echo "Starting gas-market-data-processor container..."
docker-compose up -d --build
echo "Done. Use 'docker ps' to check status."
