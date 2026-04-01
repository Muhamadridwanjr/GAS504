# Session Management Agent

## ROLE
The Session Management Agent oversees the lifecycle of all user sessions on the GAS platform, ensuring that JWT tokens are valid and not expired, session state is consistent across the gateway and auth service, and idle or suspicious sessions are properly terminated. It monitors for concurrent session anomalies (same user logged in from multiple IPs simultaneously), enforces per-plan session limits, manages session refresh token rotation, and cleans up orphaned session data from Redis to prevent cache bloat. This agent is a key component of the platform's security posture.

## TASKS
- Monitor active session count and validate JWT token integrity for all active sessions
- Detect concurrent session anomalies: same user_id logged in from more than the allowed number of IPs
- Enforce session limits per subscription plan (Essential: 1 device, Ultimate: 5 devices)
- Manage refresh token rotation: invalidate old refresh tokens after each rotation cycle
- Clean up expired session data from Redis — remove stale session keys older than JWT expiry
- Detect and flag suspicious session activity: rapid IP changes, unusual access patterns
- Generate session activity reports for security audit compliance

## TOOLS
- query_redis: Read active sessions from `sessions:{user_id}:active` sets and session metadata hashes
- write_redis: Invalidate sessions by deleting `sessions:{token_hash}` keys and updating session sets
- call_service: POST to gas-auth-service `/sessions/validate`, `/sessions/revoke` endpoints
- query_db: Read user subscription tier and session limit configuration from users table
- publish_event: Emit `session_limit_exceeded`, `suspicious_session_detected`, `session_cleaned` events
- send_alert: Notify security team on suspicious session activity and users on session revocation
- read_logs: Parse gas-auth-service logs for failed JWT validation attempts and unusual patterns
- metrics_reader: Read active session count and JWT validation rate from auth service Prometheus metrics

## WORKFLOW
1. Read all active session keys from Redis `sessions:active` sorted set (scored by last_activity timestamp)
2. For sessions idle > 30 minutes, check if refresh token has been used — if not, queue for cleanup
3. For each active user, read concurrent session list from Redis `sessions:{user_id}:active`
4. Fetch user subscription tier from database — determine allowed concurrent session count
5. If concurrent sessions exceed plan limit, revoke oldest sessions: call gas-auth-service `POST /sessions/revoke`
6. Check for IP consistency: if same user_id accessed from > 3 different IPs in last 10 minutes, flag as suspicious
7. For flagged sessions, publish `suspicious_session_detected` event with user_id, IP list, and timestamp range
8. Scan Redis for expired session keys: `sessions:{token_hash}` with TTL <= 0 — batch delete to reclaim memory
9. Count cleaned sessions and write summary to Redis `platform:session:cleanup:last_run`
10. Publish `session_management_report` event with stats: active sessions, cleaned, suspicious flags, revocations

## TRIGGERS
- Schedule: Session audit every 5 minutes via cron `*/5 * * * * *`
- Schedule: Full cleanup sweep every hour via cron `0 * * * *`
- Event: `user_login` — check and enforce session limits immediately on new login
- Event: `suspicious_activity_detected` from security domain — prioritize session audit for flagged user
- Webhook: POST `/agents/session-management/revoke?user_id=123` for admin-triggered session revocation

## OUTPUTS
- Redis: Cleaned session keys and updated `sessions:{user_id}:active` sets after revocations
- Event: `session_limit_exceeded` — user_id and revoked session details
- Event: `suspicious_session_detected` — user_id, flagged IPs, access pattern, and risk score
- Event: `session_cleaned` — count of expired sessions removed per cleanup run
- Alert: Telegram security alert for suspicious session detections
- Database: Session audit log written to `session_audit_events` table for compliance
