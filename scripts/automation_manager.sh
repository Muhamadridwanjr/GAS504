#!/bin/bash

# ============================================================
# GAS Automation Manager
# ============================================================
# Handles scheduled wake-up and sleep for heavy services.
# ============================================================

MODE=$1
WORKING_DIR="/root/gasstrategyai"

cd $WORKING_DIR

case $MODE in
    "MACRO_SYNC")
        echo "$(date): Starting Macro Data Sync (tedata)..."
        docker start gas-fundamental-data-service
        # Give it time to run its internal scheduler (starts 90s after launch)
        # and complete the scrape cycle (usually 5-10 mins)
        sleep 600
        docker stop gas-fundamental-data-service
        echo "$(date): Macro Data Sync Complete. Service stopped."
        ;;
    
    "BRIEFING_SYNC")
        echo "$(date): Starting Morning Briefing Sync..."
        # Briefing requires these for AI Analysis
        docker start gas-fundamental-data-service gas-ai-orchestrator gas-strategy-core
        # Wait for the 06:30 WIB job to complete (runs in strategy-core)
        sleep 900
        docker stop gas-fundamental-data-service gas-ai-orchestrator
        echo "$(date): Morning Briefing Sync Complete. Services stopped."
        ;;

    "NEWS_PULSE")
        echo "$(date): High Impact News Detected. Waking up analysis services..."
        docker start gas-ai-orchestrator gas-strategy-core gas-signal-service gas-risk-engine gas-pattern-detector
        # Stay awake for the news duration + results processing
        sleep 1800
        docker stop gas-ai-orchestrator gas-risk-engine gas-pattern-detector
        echo "$(date): News cycle complete. Services returned to sleep."
        ;;

    "CLEANUP")
        echo "$(date): Running resource cleanup..."
        docker system prune -f --volumes
        ;;

    *)
        echo "Usage: $0 [MACRO_SYNC|BRIEFING_SYNC|NEWS_PULSE|CLEANUP]"
        exit 1
        ;;
esac
