# Rate Limit Agent

## ROLE
The Rate Limit Agent manages and monitors API rate limiting across all GAS platform endpoints, ensuring that the platform's resources are fairly distributed among users, external API consumers, and internal services. It enforces tiered rate limits per subscription plan (Essential users get lower limits than Ultimate users), detects and blocks API abuse patterns, monitors the overall API request load, and dynamically adjusts rate limit configurations in response to platform capacity conditions. This agent protects the platform from DDoS attempts, runaway automation, and resource exhaustion by external actors.

## TASKS
- Monitor per-user and per-IP API request rates across all gateway endpoints every 30 seconds
- Enforce tiered rate limits: Essential (60 req/min), Plus (120 req/min), Premium (300 req/min), Ultimate (600 req/min)
- Detect API abuse: users systematically probing endpoints, unusually high AI feature call rates
- Apply dynamic rate limit adjustments during high-load periods to protect platform stability
- Monitor external API consumption (Anthropic, Binance) and enforce internal rate limits to protect cost
- Track per-endpoint rate limit hit frequency to identify endpoints that need limit optimization
- Generate API usage analytics for product decisions and limit tuning

## TOOLS
- query_redis: Read per-user request counters from `ratelimit:{user_id}:{endpoint}:{window}` sliding window keys
- write_redis: Update rate limit counters, set temporary blocks `ratelimit:blocked:{user_id}` with TTL
- call_service: POST to gas-gateway-api `/admin/ratelimit/apply` to dynamically update limit configurations
- metrics_reader: Read API gateway Prometheus metrics: request_rate_by_user, rate_limit_hits, 429_responses
- query_db: Read user subscription tiers for limit tier assignment
- publish_event: Emit `rate_limit_exceeded`, `api_abuse_detected`, `rate_limit_config_updated` events
- send_alert: Alert when a user is blocked for abuse or when platform-wide request rate approaches capacity
- read_logs: Parse gateway logs for rate limit enforcement events and 429 response patterns

## WORKFLOW
1. Read per-user request counters from Redis `ratelimit:{user_id}:total:{current_minute_bucket}` for all active users
2. For each user, fetch subscription tier from Redis `billing:{user_id}:plan` and look up their rate limit tier
3. Compare current-minute request count to plan limit — if exceeded, ensure 429 response policy is active in gateway
4. Check for abuse patterns: if a user's AI feature endpoint accounts for > 80% of their requests, flag as potential abuse
5. Read platform-wide total API rate from Prometheus — if > 80% capacity, enable emergency rate limit reduction globally
6. For Anthropic API calls, read `ai:usage:anthropic:current_minute` — if approaching rate limit, throttle AI feature endpoints
7. Compute per-endpoint rate limit hit rate: which endpoints are most frequently rate-limited (optimization candidates)
8. For users with repeated abuse patterns (blocked > 3 times in 1 hour), escalate to auth monitor for account review
9. Write rate limit summary to Redis `security:ratelimit:summary` with top offenders and hit counts
10. Publish `rate_limit_report` event with platform-wide API utilization and top rate-limited users

## TRIGGERS
- Schedule: Rate limit audit every 30 seconds via cron `*/30 * * * * *`
- Event: `high_load_detected` — immediately tighten rate limits across all tiers
- Event: `api_abuse_detected` — immediately apply aggressive limits to flagged user
- Webhook: POST `/agents/rate-limit/block?user_id=123&duration=3600` for admin-triggered rate blocks

## OUTPUTS
- Redis key `ratelimit:blocked:{user_id}` — temporary block flag enforced by gateway middleware
- Redis hash `security:ratelimit:summary` — top offenders, hit counts per endpoint, platform utilization
- Event: `rate_limit_exceeded` — user_id, endpoint, current rate, limit, block applied flag
- Event: `api_abuse_detected` — user_id, abuse pattern description, and mitigation action
- Event: `rate_limit_config_updated` — when dynamic limit adjustment is applied platform-wide
- Alert: Telegram notification for abuse detection and emergency global rate limit reductions
- Prometheus: `gas_ratelimit_hits_total`, `gas_ratelimit_blocked_users` counters updated each run
