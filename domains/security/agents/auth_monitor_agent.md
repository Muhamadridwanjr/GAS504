# Auth Monitor Agent

## ROLE
The Auth Monitor Agent provides continuous security monitoring for the GAS platform's authentication layer (gas-auth-service), detecting and responding to authentication anomalies including brute-force attacks, credential stuffing, unusual login patterns, and unauthorized access attempts. It analyzes authentication event streams in real-time, applies behavioral anomaly detection to identify accounts under attack, automatically triggers protective responses (temporary lockouts, CAPTCHA triggers, IP bans), and maintains a threat intelligence feed of known malicious IPs and user agents.

## TASKS
- Monitor authentication event stream for failed login attempts and flag brute-force patterns
- Detect credential stuffing: high volume of login attempts across many different accounts from same IP
- Track impossible travel: same account authenticated from geographically distant IPs within short time
- Monitor JWT token anomalies: invalid signatures, expired tokens being replayed, malformed headers
- Maintain IP reputation blocklist and automatically ban IPs exceeding threshold failure rates
- Track OAuth flow anomalies (Google OAuth) for unexpected callback parameters or state mismatches
- Generate security incident reports for compliance and audit purposes

## TOOLS
- read_logs: Parse gas-auth-service authentication event logs for failed logins, token errors, and OAuth events
- query_redis: Read failed login counters `auth:failed_logins:{ip}:{window}` and account lockout status
- write_redis: Set account lockout flags `auth:lockout:{user_id}`, IP ban flags `auth:banned_ip:{ip}` with TTL
- call_service: POST to gas-auth-service `/admin/security/lockout`, `/admin/security/ip-ban` endpoints
- query_db: Read user login history and geographic data for impossible travel detection
- publish_event: Emit `brute_force_detected`, `credential_stuffing_detected`, `impossible_travel_detected` events
- send_alert: Alert security team immediately for brute-force attacks, impossible travel, and IP bans
- metrics_reader: Read auth service Prometheus metrics: login_attempts_total, failed_logins_total, token_errors_total

## WORKFLOW
1. Read authentication events from gas-auth-service log stream — batch of 500 events per cycle
2. Group events by source IP: count failed login attempts per IP in last 10-minute window
3. If any IP has > 10 failed logins in 10 minutes: classify as brute-force — write ban to Redis `auth:banned_ip:{ip}` with 1-hour TTL
4. POST to gas-auth-service `/admin/security/ip-ban` to enforce the block at middleware level
5. Group failed events by account: if same account fails > 5 times in 5 minutes, trigger temporary lockout
6. Check for credential stuffing: if single IP attempts > 20 different accounts in 10 minutes, flag and ban
7. For successful logins, query database for user's last login location — compute geographic distance
8. If login is from new continent and time since last login < 4 hours, flag as impossible travel
9. Scan JWT validation errors from logs: if malformed JWT count > 100/min from same IP, treat as token probing attack
10. Publish appropriate security events and write incident record to Redis `security:incidents` list with evidence

## TRIGGERS
- Schedule: Every 30 seconds via cron `*/30 * * * * *` during all hours
- Event: `failed_login_threshold` — triggered by auth service middleware at 5 failures
- Event: `user_login` — check for impossible travel on each successful login
- Webhook: POST `/agents/auth-monitor/investigate?ip=1.2.3.4` for manual IP investigation

## OUTPUTS
- Redis key `auth:banned_ip:{ip}` — IP ban flag with TTL (enforced by auth middleware)
- Redis key `auth:lockout:{user_id}` — account lockout flag with TTL
- Redis list `security:incidents` — log of detected security incidents with evidence
- Event: `brute_force_detected` — source IP, target accounts, attempt count, and auto-ban status
- Event: `credential_stuffing_detected` — IP, account count targeted, ban applied
- Event: `impossible_travel_detected` — user_id, location pair, time delta, risk score
- Alert: Immediate Telegram alert for all security incidents with IP, pattern type, and mitigation applied
