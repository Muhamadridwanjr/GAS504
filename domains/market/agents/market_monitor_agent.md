# Market Monitor Agent

## ROLE
The Market Monitor Agent is responsible for continuously tracking the health, availability, and data quality of all market data feeds across the GAS platform. It monitors MT5 WebSocket connections, Binance feed ingestion, and the real-time hub to ensure that downstream analysis services always receive fresh, valid market data. When anomalies are detected — such as stale prices, missing symbols, or feed interruptions — this agent raises alerts and triggers corrective actions including feed reconnection and cache invalidation.

## TASKS
- Poll all active market data feeds every 30 seconds and verify tick freshness
- Detect stale symbols where last tick age exceeds configured threshold (default: 60s for forex, 10s for crypto)
- Monitor Redis market:ticks stream for data volume and timestamp gaps
- Cross-validate prices between MT5 and Binance feeds for overlapping instruments
- Trigger feed reconnection workflows when a data source becomes unresponsive
- Publish health status events to the event bus for downstream consumers
- Maintain a rolling 5-minute tick count per symbol for volume anomaly detection

## TOOLS
- query_redis: Read from Redis streams (market:ticks, market:prices) to inspect latest tick data
- write_redis: Write health status flags and last-seen timestamps to Redis
- check_websocket: Verify WebSocket connection state of mt5-websocket and realtime-hub services
- call_service: HTTP health-check calls to gas-mt5-websocket, gas-binance-service, gas-realtime-hub
- publish_event: Emit market_feed_degraded or market_feed_restored events to the event bus
- send_alert: Dispatch Telegram/notification alerts when feeds go down or data is stale
- metrics_reader: Read Prometheus metrics from gas-observability for tick throughput counters
- read_logs: Tail service logs from gas-mt5-websocket and gas-realtime-hub for error patterns

## WORKFLOW
1. Query Redis key `market:health:last_checked` — if within last 25s, skip run to avoid overlap
2. Fetch all tracked symbols from Redis set `market:symbols:active`
3. For each symbol, read latest tick from `market:ticks:{symbol}` and compute age in seconds
4. If tick age > threshold, call `check_websocket` on the responsible feed service to confirm connectivity
5. If WebSocket is disconnected, call `call_service` POST `/reconnect` on the feed service and write `market:feed:{service}:status = reconnecting` to Redis
6. If WebSocket is connected but data is stale, publish `market_data_stale` event with symbol and age payload
7. Cross-check overlapping symbols (BTCUSDT, ETHUSD) between MT5 and Binance — flag if spread > 0.5%
8. Aggregate per-symbol tick counts over the last 5 minutes from Redis sorted sets
9. Write summary health report to Redis hash `market:health:summary` with per-symbol status flags
10. Publish `market_health_report` event to event bus with overall status (healthy/degraded/critical)

## TRIGGERS
- Schedule: every 30 seconds via cron `*/30 * * * * *`
- Event: `feed_reconnect_requested` — immediately re-runs feed health checks
- Event: `service_restarted` with service tag `mt5-websocket` or `binance-service`
- Webhook: POST `/agents/market-monitor/run` for on-demand execution

## OUTPUTS
- Redis hash `market:health:summary` — per-symbol freshness status and feed health flags
- Event: `market_health_report` — published to event bus every run with overall platform market health
- Event: `market_feed_degraded` — published when any feed exceeds staleness threshold
- Event: `market_feed_restored` — published when a previously degraded feed recovers
- Alert: Telegram notification when feed goes critical (>5 minutes stale)
- Metrics: Updates Prometheus gauge `gas_market_feed_health` per symbol
