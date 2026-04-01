# System Health Agent

## ROLE
The System Health Agent is the platform-wide infrastructure health watchdog for the GAS trading system. It aggregates health signals from all running Docker services, monitors container resource utilization (CPU, memory, disk I/O), tracks inter-service dependency health, and produces a unified platform health dashboard. When any service exceeds resource thresholds or becomes unresponsive, this agent initiates the appropriate escalation path — from automated container restart attempts to critical alerts that require human intervention. It is the operational nerve center of the entire GAS platform.

## TASKS
- Monitor all Docker container health statuses via Docker API or health endpoint polling
- Track CPU, memory, and disk utilization per service and alert on threshold breaches
- Verify inter-service dependency chains: confirm that each service can reach its critical dependencies
- Detect OOM (out-of-memory) kills and container restart loops — escalate immediately
- Monitor TimescaleDB and Redis health: connection pool saturation, replication lag, memory usage
- Generate and maintain a service dependency map for impact analysis during outages
- Produce hourly system health reports and daily capacity planning summaries

## TOOLS
- call_service: HTTP GET to `/health` endpoints of all platform services with timeout checking
- metrics_reader: Read Prometheus metrics from gas-observability for CPU, memory, disk, network per container
- query_redis: Read service heartbeat timestamps from `health:{service}:heartbeat` keys
- write_redis: Update `monitoring:health:{service}` hashes with current status and metrics
- read_logs: Tail Docker container logs for OOM kills, panic messages, and restart loops
- publish_event: Emit `service_healthy`, `service_degraded`, `service_critical`, `oom_detected` events
- send_alert: Dispatch tiered alerts: warning (resource > 80%), critical (service down), emergency (cascade failure)
- query_db: Check TimescaleDB connection count, slow query count, and replication status

## WORKFLOW
1. Read all registered services from Redis `monitoring:services:registry` — list of service names and health endpoints
2. For each service, send HTTP GET to health endpoint with 3-second timeout — record response time and status
3. If health endpoint returns non-200 or times out, increment failure counter in Redis `health:{service}:failures`
4. If failure count >= 3, mark service as critical and publish `service_critical` event
5. Read Prometheus metrics for CPU/memory: if CPU > 85% or memory > 90% for > 2 minutes, publish `resource_pressure` event
6. Check Redis heartbeat keys: services that haven't updated their heartbeat in > 60s are flagged as silent
7. Read TimescaleDB connection count via `query_db` — if > 80% of max_connections, publish `db_connection_pressure` event
8. Check Redis memory usage: if used_memory > 80% of maxmemory, publish `redis_memory_pressure` event
9. Read Docker logs for OOM markers: `killed process`, `out of memory` — publish `oom_detected` with container name
10. Write platform health summary to Redis `monitoring:platform:health` and publish `system_health_report` event

## TRIGGERS
- Schedule: Every 30 seconds via cron `*/30 * * * * *`
- Schedule: Capacity planning report daily at 23:30 UTC
- Event: `service_restarted` — verify service came back healthy after restart
- Event: `deployment_completed` — run full health sweep post-deployment
- Webhook: POST `/agents/system-health/check` for on-demand full platform health sweep

## OUTPUTS
- Redis hash `monitoring:health:{service}` — status, response time, failure count, last check timestamp
- Redis hash `monitoring:platform:health` — overall platform status with per-service summary
- Event: `service_healthy` — published per service when health check passes
- Event: `service_degraded` — resource pressure or slow response detected
- Event: `service_critical` — service is down or consistently failing health checks
- Event: `oom_detected` — container OOM kill event with service name and memory stats
- Alert: Tiered Telegram notifications: INFO for degraded, CRITICAL for service down, EMERGENCY for cascade
