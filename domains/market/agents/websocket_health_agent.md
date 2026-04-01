# WebSocket Health Agent

## ROLE
The WebSocket Health Agent is a dedicated watchdog for all persistent WebSocket connections in the GAS platform, specifically the MT5 WebSocket service and the real-time hub. It measures connection latency, counts dropped frames, tracks reconnection frequency, and ensures that clients subscribed to real-time data streams receive continuous, uninterrupted tick and OHLCV updates. This agent enforces connection quality SLAs and escalates to the Market Monitor Agent when systemic connection degradation is detected.

## TASKS
- Measure round-trip WebSocket ping/pong latency for each active connection every 15 seconds
- Count and record WebSocket frame drops and protocol errors per connection session
- Track reconnection frequency — alert if any service reconnects more than 3 times in 10 minutes
- Verify that the real-time hub is broadcasting to all subscribed clients without message lag
- Monitor the mt5-websocket tick emission rate and compare against expected symbols count
- Detect zombie connections — WebSocket open but no data flowing for >30 seconds
- Coordinate graceful restart of WebSocket services when connection health degrades below threshold

## TOOLS
- check_websocket: Establish test WebSocket connection and measure ping/pong round-trip latency
- query_redis: Read connection state from `ws:connections:{service}` and reconnection counters
- write_redis: Persist latency samples and reconnection event timestamps to Redis sorted sets
- read_logs: Parse WebSocket service logs for CLOSE frames, error codes, and reconnection events
- call_service: Send HTTP requests to gas-mt5-websocket and gas-realtime-hub `/ws/stats` endpoints
- publish_event: Emit `websocket_degraded`, `websocket_recovered`, `zombie_connection_detected` events
- send_alert: Send Telegram alert when latency exceeds 500ms or reconnections exceed threshold
- metrics_reader: Read Prometheus `ws_connection_count`, `ws_message_rate`, `ws_latency_p99` metrics

## WORKFLOW
1. Read current connection registry from Redis `ws:connections:registry` — list of active WebSocket sessions
2. For each connection, call `check_websocket` with a test PING frame and record latency in milliseconds
3. Store latency sample in Redis sorted set `ws:latency:{service}:{session}` with timestamp score
4. Compute P50, P95, P99 latency from the last 100 samples stored in Redis
5. Read reconnection event log from Redis list `ws:reconnections:{service}` — count events in last 10 minutes
6. If reconnection count > 3 in 10 minutes, publish `websocket_instability` event with service tag
7. Query `/ws/stats` endpoint on each service to get connected client count and message throughput
8. For each session with zero message rate but open connection (zombie), call service DELETE `/ws/sessions/{id}` to evict
9. If P99 latency > 500ms, publish `websocket_degraded` event and send alert via Telegram
10. Write health snapshot to Redis hash `ws:health:{service}` and publish `websocket_health_report` event

## TRIGGERS
- Schedule: every 15 seconds via cron `*/15 * * * * *`
- Event: `market_feed_degraded` — immediately inspect WebSocket layer for root cause
- Event: `client_connection_error` — investigate the specific session mentioned in payload
- Webhook: POST `/agents/websocket-health/run` for manual invocation during incident response

## OUTPUTS
- Redis hash `ws:health:{service}` — latency percentiles, client count, message rate, reconnection count
- Redis sorted set `ws:latency:{service}` — rolling latency time-series for trending
- Event: `websocket_health_report` — full stats report published every run
- Event: `websocket_degraded` — triggered when P99 latency exceeds 500ms
- Event: `zombie_connection_detected` — lists session IDs that were evicted
- Alert: Telegram notification for critical WebSocket instability affecting data feeds
