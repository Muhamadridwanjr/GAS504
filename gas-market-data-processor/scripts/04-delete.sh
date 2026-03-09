#!/bin/bash
echo "Deleting gas-market-data-processor container and volumes..."
docker-compose down -v --rmi all
echo "Done."
