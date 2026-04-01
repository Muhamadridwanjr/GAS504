# Token Validation Agent

## ROLE
The Token Validation Agent continuously audits the integrity and security of the GAS platform's JWT token ecosystem, ensuring that all tokens in circulation are valid, have not been tampered with, belong to active accounts with the correct claims, and are within their authorized refresh window. It manages the token revocation list, detects leaked or stolen tokens (used from unexpected locations after a refresh), enforces token rotation policies, and provides a real-time token health score for the platform's security posture dashboard.

## TASKS
- Maintain and enforce the JWT token revocation list (blocklist) in Redis for immediate token invalidation
- Detect token reuse after refresh: if an old access token is used after its replacement was issued, flag as stolen
- Validate JWT claim structure: verify that role, plan, user_id, and exp fields are present and correctly formatted
- Monitor for tokens with unusually long expiry times that may indicate JWT configuration drift
- Audit admin token usage: every admin-role JWT usage must be logged with full request context
- Enforce token rotation: refresh tokens must be rotated on each use (refresh token family tracking)
- Compute and publish platform token health score based on anomaly rate and revocation frequency

## TOOLS
- call_service: POST to gas-auth-service `/admin/tokens/validate`, `/admin/tokens/revoke` endpoints
- query_redis: Read token revocation list from `auth:token:revoked` set and refresh token family tracking
- write_redis: Add tokens to revocation list `auth:token:revoked`, track refresh token families in `auth:refresh:{family_id}`
- query_db: Read token audit log from `token_audit_events` table and user account status
- read_logs: Parse gas-auth-service token validation logs for claim errors and refresh events
- publish_event: Emit `token_revoked`, `stolen_token_detected`, `token_audit_alert`, `token_health_report` events
- send_alert: Immediate alert for stolen token detection and admin token anomalies
- metrics_reader: Read token validation rate, revocation rate, and refresh rate from auth service metrics

## WORKFLOW
1. Read latest batch of token validation events from gas-auth-service logs
2. For each token validation event, extract JWT header and payload claims without full signature verification
3. Check that required claims are present: `user_id`, `role`, `plan`, `exp`, `iat`, `jti` (JWT ID)
4. If any required claim is missing, log as malformed token and publish `token_audit_alert` event
5. For each refresh token use, look up family ID in Redis `auth:refresh:{family_id}` — verify this is the latest token in the family
6. If an older refresh token in the family is being used (rotation bypass), revoke ALL tokens in the family and flag as stolen
7. Scan for tokens with `exp` more than 24 hours from `iat` — these should not exist with platform config
8. For all admin role token usages, write full request context to `token_audit_events` table in database
9. Compute token health score: 100 - (revocation_rate × 50) - (anomaly_rate × 30) - (malformed_rate × 20)
10. Write health score to Redis `security:token:health` and publish `token_health_report` event

## TRIGGERS
- Schedule: Token audit sweep every 2 minutes via cron `*/2 * * * * *`
- Event: `user_logout` — immediately add user's active tokens to revocation list
- Event: `account_suspended` — revoke all tokens for suspended user_id
- Event: `password_changed` — revoke all existing tokens, forcing re-authentication
- Webhook: POST `/agents/token-validation/revoke?user_id=123` for admin-triggered revocation

## OUTPUTS
- Redis set `auth:token:revoked` — active token revocation list checked by auth middleware on every request
- Redis hash `auth:refresh:{family_id}` — refresh token family tracking for rotation validation
- Database `token_audit_events` table — admin token usage log for compliance
- Event: `stolen_token_detected` — user_id, family_id, old token hash, and auto-revocation action
- Event: `token_revoked` — token hash, reason (logout/suspension/stolen/expiry), user_id
- Event: `token_health_report` — platform token health score with anomaly rates
- Alert: Immediate Telegram alert for stolen token detection with user_id and mitigation action taken
