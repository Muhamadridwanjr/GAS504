#!/bin/bash

# ============================================================
# GAS Resource Management Script
# ============================================================
# Usage: ./manage_resources.sh [CORE|LIGHT|FULL|STOP_HEAVY]
# ============================================================

GROUP=$1

CORE_SERVICES="gas-redis gas-user-db gas-auth-service gas-gateway-api gas-terminal-backend gas-mt5-websocket gas-signal-service gas-term-service gas-mt5-data-service nginx-proxy gas-terminal-frontend gas-user-service gas-billing-service"

HEAVY_SERVICES="gas-fundamental-data-service gas-ai-orchestrator gas-statarb-engine gas-quant-backtester gas-feature-engine gas-correlation gas-regime-detector gas-pattern-detector gas-trend-engine gas-orderflow gas-risk-engine gas-market-phase gas-rag-macro gas-rag-technical gas-social-service gas-screener-service gas-tradingplan-service gas-calendar-news-service"

case $GROUP in
    "CORE")
        echo "Starting CORE services only..."
        docker start $CORE_SERVICES
        echo "Stopping non-core services..."
        docker stop $HEAVY_SERVICES
        ;;
    "LIGHT")
        echo "Starting CORE + Essential Analyze services..."
        docker start $CORE_SERVICES gas-alert-engine gas-notification-service gas-strategy-core
        docker stop $HEAVY_SERVICES
        ;;
    "FULL")
        echo "Starting ALL services (Warning: High RAM usage)..."
        docker start $CORE_SERVICES $HEAVY_SERVICES gas-alert-engine gas-notification-service gas-strategy-core
        ;;
    "STOP_HEAVY")
        echo "Stopping heaviest services to free up RAM..."
        docker stop $HEAVY_SERVICES
        ;;
    *)
        echo "Usage: $0 [CORE|LIGHT|FULL|STOP_HEAVY]"
        exit 1
        ;;
esac

echo "Done. Current resource usage:"
docker stats --no-stream
