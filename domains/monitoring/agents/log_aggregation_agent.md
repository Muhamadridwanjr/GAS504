# Log Aggregation Agent

## ROLE
The Log Aggregation Agent collects, normalizes, and indexes structured logs from all GAS platform services into a centralized log store, making them queryable for debugging, auditing, and anomaly detection. It monitors log volumes per service, detects log-level distribution shifts (sudden spike in ERROR logs), extracts key metrics from log patterns (slow query counts, failed authentication attempts, API error rates), and triggers alerting when critical log patterns are detected. This agent transforms raw log streams into actionable operational intelligence for the platform team.

## TASKS
- Collect logs from all service containers via Docker log drivers or log files
- Normalize log formats: parse structured JSON logs and convert unstructured text to structured format
- Index logs with metadata: service name, log level, timestamp, trace_id, user_id, symbol
- Detect log anomalies: ERROR rate spikes, repeated exception patterns, silence detection
- Extract business metrics from logs: API call rates, AI feature usage counts, signal generation rates
- Maintain 30-day rolling log retention with automatic pruning of older entries
- Provide fast log search API for debugging and incident investigation

## TOOLS
- read_logs: Read log streams from all service log files and Docker log outputs
- call_service: POST to gas-observability `/logs/ingest` for centralized log storage
- query_redis: Read log processing cursors from `logs:cursor:{service}` to resume after interruption
- write_redis: Update processing cursors and write log anomaly alerts to `logs:anomalies:{service}`
- query_db: Query log index in TimescaleDB for historical log search and pattern queries
- metrics_reader: Read log ingestion rate and storage utilization from gas-observability metrics
- publish_event: Emit `log_anomaly_detected`, `error_spike_detected`, `log_ingestion_healthy` events
- send_alert: Alert on critical log patterns: OOM kills, database connection failures, auth bypass attempts

## WORKFLOW
1. For each registered service, read log processing cursor from Redis `logs:cursor:{service}` to find resume point
2. Call `read_logs` from cursor position — read up to 1000 new log lines per service per cycle
3. Parse each log line: detect JSON structure or apply regex patterns for common log formats
4. Normalize to schema: `{timestamp, service, level, message, trace_id, user_id, symbol, duration_ms}`
5. Batch normalized log entries and POST to gas-observability `/logs/ingest` in batches of 100
6. After successful ingest, update Redis cursor `logs:cursor:{service}` to new log file position
7. Count ERROR and CRITICAL level logs in current batch — compare to baseline rate for this service
8. If ERROR count in last 5 minutes > 3× baseline rate, publish `error_spike_detected` with sample messages
9. Scan for critical patterns: OOM phrases, "connection refused", "authentication failed" > 10 in 60s
10. Write log anomaly summary to Redis `logs:anomalies:{service}` and publish appropriate events

## TRIGGERS
- Schedule: Log collection every 30 seconds via cron `*/30 * * * * *`
- Event: `service_critical` — immediately collect and analyze recent logs for root cause evidence
- Event: `incident_detected` — package last 1000 log lines from affected service for incident context
- Schedule: Log pruning and retention enforcement daily at 03:00 UTC
- Webhook: POST `/agents/log-aggregation/search?service=gas-auth-service&level=ERROR&minutes=30` for search

## OUTPUTS
- TimescaleDB `service_logs` table — normalized, indexed log entries with full metadata
- Redis `logs:anomalies:{service}` — current anomaly flags per service
- Event: `log_anomaly_detected` — service, anomaly type, sample messages, and rate information
- Event: `error_spike_detected` — service with sudden ERROR rate increase and sample stack traces
- Event: `log_ingestion_healthy` — periodic confirmation that log pipeline is running correctly
- Alert: Telegram notification for critical log patterns affecting security or data integrity
