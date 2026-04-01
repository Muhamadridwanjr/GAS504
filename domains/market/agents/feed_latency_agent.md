# Feed Latency Agent

## ROLE
The Feed Latency Agent measures end-to-end latency of market data as it flows from external brokers and exchanges through the GAS ingestion pipeline to final storage and cache. It benchmarks the time from when a tick is generated at the source (MT5 broker or Binance) to when it becomes available in the Redis cache and TimescaleDB, identifies pipeline bottlenecks, and provides latency SLA compliance reports. This agent ensures that analysis engines and trading signals are operating on the most current available market data.

## TASKS
- Measure tick-to-cache latency: time from tick source timestamp to Redis write timestamp
- Measure tick-to-database latency: time from tick source timestamp to TimescaleDB insert timestamp
- Track per-symbol latency percentiles (P50, P95, P99) over rolling 1-hour windows
- Identify pipeline stages introducing the most latency (WebSocket layer, processor, ingestor, DB write)
- Compare MT5 broker tick latency vs Binance API latency for equivalent instruments
- Alert when P95 end-to-end latency exceeds 500ms for any symbol
- Produce hourly latency trend reports for capacity planning

## TOOLS
- query_redis: Read `market:ticks:{symbol}` entries with `received_at` and `source_ts` fields for latency computation
- query_db: Query TimescaleDB for `inserted_at` vs `tick_time` per record to measure DB write latency
- metrics_reader: Read Prometheus histograms `gas_tick_pipeline_latency_seconds` from gas-observability
- write_redis: Write latency percentile results to `market:latency:{symbol}:{stage}` Redis hashes
- call_service: Query `/metrics/latency` endpoints on gas-mt5-websocket and gas-binance-service
- publish_event: Emit `feed_latency_report` and `feed_latency_breach` events to the event bus
- send_alert: Dispatch alerts when latency SLAs are breached
- read_logs: Inspect data-ingestor logs for processing time annotations

## WORKFLOW
1. For each active symbol, read the last 1000 ticks from Redis stream `market:ticks:{symbol}` with metadata
2. Compute per-tick latency: `received_at - source_ts` for each record and aggregate into P50/P95/P99
3. Query TimescaleDB for `SELECT symbol, AVG(inserted_at - tick_time), PERCENTILE_CONT(0.95) ...` over last 1 hour
4. Break down latency by pipeline stage: WebSocket → Processor → Ingestor → DB write using stage timestamps
5. Compare MT5 and Binance latency for XAUUSD/BTCUSDT and flag when Binance is >200ms faster/slower
6. If P95 latency for any symbol exceeds 500ms, publish `feed_latency_breach` event with symbol and value
7. Call `/metrics/latency` on each feed service to get their self-reported processing time
8. Correlate external latency spikes with network or load events from metrics_reader
9. Write per-symbol P50/P95/P99 results to Redis hash `market:latency:{symbol}` with TTL 2 hours
10. Publish `feed_latency_report` event with aggregate platform latency stats and top 5 slowest symbols

## TRIGGERS
- Schedule: every 60 seconds via cron `* * * * *`
- Event: `market_feed_degraded` — immediately measure latency to diagnose feed quality issues
- Event: `high_load_detected` — run latency audit when system load spikes
- Webhook: POST `/agents/feed-latency/run` for on-demand latency profiling

## OUTPUTS
- Redis hash `market:latency:{symbol}` — P50/P95/P99 latency per symbol per pipeline stage
- Event: `feed_latency_report` — published each run with platform-wide latency summary
- Event: `feed_latency_breach` — published immediately when P95 > 500ms threshold
- Alert: Telegram notification when P99 latency exceeds 1000ms for major pairs
- Prometheus metrics: Updates `gas_feed_latency_p50`, `gas_feed_latency_p95`, `gas_feed_latency_p99` gauges
