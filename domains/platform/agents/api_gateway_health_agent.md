# API Gateway Health Agent

## ROLE
The API Gateway Health Agent monitors the availability, performance, and correctness of the gas-gateway-api service, which is the single entry point for all external traffic to the GAS platform. It continuously verifies that all upstream service proxy routes are healthy, measures request throughput and error rates, detects gateway configuration drift, and ensures that authentication middleware, rate limiting, and CORS policies are functioning correctly. When gateway degradation is detected — high error rates, slow responses, or failed upstream proxies — this agent escalates immediately given the gateway's critical role in platform accessibility.

## TASKS
- Perform end-to-end health checks on all gateway proxy routes every 30 seconds
- Monitor gateway request rate, error rate (4xx and 5xx), and response latency P50/P95/P99
- Verify upstream service connectivity: auth, web-backend, terminal-backend, billing checks
- Detect configuration drift: compare running gateway config against expected configuration baseline
- Monitor rate limiting enforcement — verify limits are applied correctly per endpoint and user tier
- Alert on error rate spikes (>5% 5xx over 60s) or latency degradation (P95 > 2 seconds)
- Validate authentication middleware is correctly rejecting invalid JWT tokens

## TOOLS
- call_service: HTTP health checks to `GET /health` on gas-gateway-api and all upstream services
- check_websocket: Verify WebSocket upgrade path through gateway works for real-time hub connections
- query_redis: Read gateway request stats from `gateway:stats:*` Redis keys populated by gateway middleware
- write_redis: Update `platform:gateway:health` with current health status and metrics
- read_logs: Parse gateway nginx/reverse-proxy logs for error patterns and slow request entries
- metrics_reader: Read Prometheus metrics from gateway: `nginx_http_requests_total`, `nginx_http_request_duration_seconds`
- publish_event: Emit `gateway_healthy`, `gateway_degraded`, `upstream_unreachable`, `gateway_critical` events
- send_alert: Dispatch critical alerts when gateway error rate or an upstream service becomes unreachable

## WORKFLOW
1. Send HTTP GET to gas-gateway-api `/health` endpoint — verify 200 response within 2 seconds
2. For each configured upstream proxy route (/auth/v1/, /web/api/v1/, /terminal/, /billing-api/), send test request
3. Verify upstream responses: check HTTP status, response time, and that auth middleware returns correct errors on invalid JWT
4. Read gateway metrics from Prometheus: total requests, 5xx count, P95 latency for last 60 seconds
5. Compute error rate: (5xx_count / total_requests) × 100 — flag if > 5% threshold
6. Check rate limiting: send burst of 20 requests to a rate-limited endpoint — verify 429 responses kick in at limit
7. Read gateway config hash from Redis `gateway:config:hash` — compare to known-good baseline hash
8. If config drift detected (hash mismatch), publish `gateway_config_drift` event and alert immediately
9. Write health snapshot to Redis `platform:gateway:health` with all metrics and upstream status flags
10. Publish `gateway_healthy` or `gateway_degraded` event based on overall health assessment

## TRIGGERS
- Schedule: Every 30 seconds via cron `*/30 * * * * *`
- Event: `service_restarted` with gateway tag — immediately re-verify after restart
- Event: `deployment_completed` — verify gateway health post-deployment
- Webhook: POST `/agents/api-gateway-health/check` for on-demand health check

## OUTPUTS
- Redis hash `platform:gateway:health` — overall status, upstream health map, error rate, latency percentiles
- Event: `gateway_healthy` — published each run when all checks pass
- Event: `gateway_degraded` — published when error rate or latency exceeds threshold
- Event: `upstream_unreachable` — specific upstream service unreachable through gateway
- Event: `gateway_critical` — gateway itself is unresponsive (most critical platform event)
- Alert: Telegram immediate notification for gateway_critical and upstream_unreachable events
