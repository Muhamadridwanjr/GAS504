# Alert Dispatch Agent

## ROLE
The Alert Dispatch Agent is the centralized notification router for the GAS trading platform, responsible for receiving alert events from all upstream agents and services, formatting them appropriately for each delivery channel, managing user notification preferences, and ensuring reliable delivery to Telegram, push notifications, email, and in-app alert feeds. It prevents alert fatigue through intelligent deduplication, rate limiting per user, and priority-based queuing — ensuring that the most critical alerts (signals, risk breaches, system failures) always reach traders promptly while suppressing repetitive low-value notifications.

## TASKS
- Receive all alert events from the event bus and route to appropriate delivery channels
- Format alerts per channel: Telegram markdown, push notification JSON, email HTML template
- Apply per-user notification preferences (subscribed alert types, quiet hours, channel preferences)
- Deduplicate alerts: suppress identical alerts for the same symbol/event within a configurable window
- Priority-queue alerts: critical (risk breach, system down) > high (signal generated) > medium (pattern detected) > low (health report)
- Track alert delivery status and retry failed deliveries up to 3 times with exponential backoff
- Generate daily alert delivery report with success rates and click-through statistics

## TOOLS
- call_service: POST to gas-notification-service `/notify`, gas-telegram-bot `/send`, `/send-photo` endpoints
- query_redis: Read user notification preferences from `users:{user_id}:notification_prefs` hashes
- write_redis: Write alert deduplication keys to `alerts:dedup:{hash}` with TTL, track delivery status
- query_db: Read user preferences and quiet hours configuration from users table
- publish_event: Emit `alert_sent`, `alert_failed`, `alert_deduplicated` events for monitoring
- send_alert: Internal fallback — direct Telegram dispatch for system-critical alerts bypassing queue
- read_logs: Monitor gas-notification-service and gas-telegram-bot logs for delivery failures
- metrics_reader: Read alert delivery rate, latency, and failure rate Prometheus metrics

## WORKFLOW
1. Subscribe to all alert event types from event bus: `signal_generated`, `pattern_detected`, `risk_rejected`, `drawdown_warning`, system health events
2. For each incoming alert event, compute deduplication hash: SHA256(event_type + symbol + direction + window_bucket)
3. Check Redis `alerts:dedup:{hash}` — if key exists, publish `alert_deduplicated` event and skip delivery
4. If not duplicate, set Redis `alerts:dedup:{hash}` with TTL based on event type (signal: 5m, pattern: 15m, health: 60m)
5. Query user preference table for all users subscribed to this alert type and instrument
6. Apply quiet hours filter: skip users with `quiet_hours_active = true` for non-critical alerts
7. For each eligible user, format alert for their preferred channel: Telegram markdown card, push JSON payload, or email template
8. POST formatted alert to gas-notification-service `/notify` with user_id, channel, and message payload
9. Track delivery result — on failure, write to Redis `alerts:retry_queue` with retry count and next retry timestamp
10. Publish `alert_sent` event with delivery stats or `alert_failed` with error detail for monitoring

## TRIGGERS
- Event: Any event with alert priority > LOW from the platform event bus (continuously subscribed)
- Schedule: Retry queue processor every 30 seconds for failed delivery retries
- Schedule: Daily alert report generation at 23:55 UTC
- Webhook: POST `/agents/alert-dispatch/send` for direct alert injection (admin use)

## OUTPUTS
- Telegram messages: formatted signal cards, pattern alerts, risk warnings, system health summaries
- Push notifications: mobile push via gas-notification-service for iOS/Android clients
- Email: templated HTML alerts for daily digests and critical event summaries
- Redis `alerts:dedup:{hash}` — deduplication key store with per-type TTL
- Event: `alert_sent` — delivery confirmation with channel and latency
- Event: `alert_failed` — failed delivery with error reason for retry scheduling
- Prometheus: `gas_alerts_sent_total`, `gas_alerts_failed_total`, `gas_alerts_deduplicated_total` counters
