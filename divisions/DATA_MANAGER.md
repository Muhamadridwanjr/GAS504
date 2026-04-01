# DATA_MANAGER.md — Data Division
# WIN 2 | Services: MT5 · scrapers · RAG · realtime

## SERVICES
gas-mt5-websocket            :8110  ← CRITICAL (EA connects here) (healthy ✅)
gas-mt5-data-service         :8100  (healthy ✅)
gas-market-data-processor    :8010  (healthy ✅)
gas-data-ingestor            :9604  (healthy ✅)
gas-calendar-news-service    :9601  ← ecocal scraper 05:00 WIB (healthy ✅)
gas-fundamental-data-service :9603  (healthy ✅)
gas-vector-db                :9004
gas-rag-technical            :9001
gas-rag-macro                :9002
gas-realtime-hub             :8111  ← CRITICAL (WS broadcast) (healthy ✅)

## WORKERS
data_pipeline_agent · data_cleaning_agent · vector_db_agent
rag_agent · market_data_agent

## AUTO-SCAN
```bash
echo "=== DATA SCAN ===" && date
for p in 8110 8100 9601 9603 9004 9001 9002 8111; do
  curl -s --max-time 1 localhost:$p/health 2>/dev/null | grep -c "ok" > /dev/null \
    && echo "✅ :$p" || echo "❌ :$p"
done
docker logs gas-calendar-news-service --tail=10 2>/dev/null
cat /root/gasstrategyai/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## DATA FLOW
MT5 EA → mt5-websocket:8110 → market-data-processor:8010
       → data-ingestor:9604 → vector-db:9004 → rag:9001/9002
       → realtime-hub:8111 → frontend WS

## ECOCAL: cron 05:00 WIB → gas-calendar-news-service:9601
## BINANCE: gas-binance-service:9612 → Redis market:ticks (healthy ✅)
