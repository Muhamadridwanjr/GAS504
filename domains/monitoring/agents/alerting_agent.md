# Alerting Agent

## ROLE
The Alerting Agent manages the platform-wide alert rule engine, evaluating Prometheus-style alerting rules against live metrics and health signals, maintaining alert state (pending/firing/resolved), and routing firing alerts to the appropriate notification channels. It implements alert grouping to prevent alert storms, applies inhibition rules (suppress less severe alerts when a critical alert is already firing), and manages alert silences for planned maintenance windows. This agent ensures that the operations team receives actionable, deduplicated, and contextualized alerts rather than a flood of raw events.

## TASKS
- Evaluate all configured alert rules against live Prometheus metrics every 30 seconds
- Maintain alert state machine: pending (rule violated < threshold duration) → firing → resolved
- Group related alerts to prevent alert storms (e.g., multiple services down → single incident alert)
- Apply inhibition rules: suppress feed latency alerts when market feed is already down
- Manage maintenance window silences: suppress all alerts for configured service during planned downtime
- Compute alert severity escalation: warning → critical based on duration and impact score
- Track mean-time-to-detection (MTTD) and mean-time-to-resolution (MTTR) for alert KPIs

## TOOLS
- metrics_reader: Read Prometheus metrics for all configured alert rule expressions
- query_redis: Read alert state from `alerting:state:{alert_name}` and silence configurations from `alerting:silences`
- write_redis: Update alert state, firing time, and resolution time in `alerting:state:{alert_name}`
- publish_event: Emit `alert_firing`, `alert_resolved`, `alert_silenced`, `incident_detected` events
- send_alert: Route firing alerts to Telegram, email, or PagerDuty-style webhook based on severity
- call_service: POST to gas-notification-service for alert delivery and tracking
- query_db: Read alert rule configurations from `alerting_rules` table and maintenance windows from `silences`
- read_logs: Correlate firing alerts with log patterns for root cause context enrichment

## WORKFLOW
1. Load all active alert rules from database `alerting_rules` table — includes metric query, threshold, and duration
2. For each rule, execute Prometheus metric query via `metrics_reader` — compare current value to threshold
3. If threshold violated and alert state is `ok`: set state to `pending` with pending_since timestamp
4. If threshold violated and pending_since > rule's `for` duration: transition to `firing` state
5. Check active silences in Redis `alerting:silences` — if firing alert matches a silence, suppress delivery
6. Check inhibition rules: if `service_critical` is firing, inhibit `service_degraded` for the same service
7. Group firing alerts by service and severity — combine multiple related alerts into a single incident
8. For new firing alerts, enrich with context from logs (`read_logs`) and publish `alert_firing` event
9. If previously firing alert's metric is now below threshold, transition to `resolved` and publish `alert_resolved`
10. Compute and update MTTD (firing_time - anomaly_start_time) and MTTR (resolved_time - firing_time) in Redis

## TRIGGERS
- Schedule: Alert rule evaluation every 30 seconds via cron `*/30 * * * * *`
- Event: `system_health_report` — re-evaluate health-based alert rules after each health sweep
- Event: `maintenance_window_started` — load new silence for the maintenance period
- Webhook: POST `/agents/alerting/silence` for creating manual maintenance silences

## OUTPUTS
- Redis hash `alerting:state:{alert_name}` — current state, firing since, resolved at, last evaluated
- Event: `alert_firing` — alert name, severity, metric value, threshold, affected service, context snippet
- Event: `alert_resolved` — alert name, resolution time, duration it was firing
- Event: `incident_detected` — grouped multi-alert event representing a larger system incident
- Alert: Telegram, email, or webhook notification routed by severity (warning → Telegram, critical → both)
- Database: Alert history in `alert_events` table for MTTD/MTTR KPI tracking
