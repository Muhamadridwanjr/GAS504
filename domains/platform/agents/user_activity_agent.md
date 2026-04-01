# User Activity Agent

## ROLE
The User Activity Agent tracks, analyzes, and acts upon user engagement patterns across the GAS platform to drive retention, reward active users through the leveling and XP system, and identify churn risk early. It monitors feature usage, session frequency, AI credit consumption, journal activity, and signal engagement to build a holistic user health score. This agent feeds the gamification system (XP awards for activity milestones), powers personalized re-engagement notifications, and provides the platform team with actionable user analytics for product improvement decisions.

## TASKS
- Track per-user feature usage: which of the 18 AI features are used, with what frequency
- Award XP for activity milestones: first signal viewed, 7-day streak, 10 AI queries, journal entry written
- Compute user engagement health score: 0-100 based on activity recency, depth, and breadth
- Detect churn risk: flag users with declining engagement scores over 7+ days
- Send re-engagement notifications for users who haven't logged in for 3+ days
- Track credit consumption patterns and alert users when approaching low-credit threshold
- Generate cohort analysis data: group users by sign-up date, plan tier, and activity pattern

## TOOLS
- query_db: Read user activity events, session logs, feature usage records, and journal entries from database
- write_redis: Update `users:{user_id}:engagement` score, XP balance in `users:{user_id}:xp`, activity streak
- query_redis: Read current XP, credit balance, and last activity timestamp for each user
- call_service: POST to gas-web-backend `/api/v1/level/add-xp` for XP awards and level-up processing
- publish_event: Emit `xp_awarded`, `level_up_triggered`, `churn_risk_detected`, `engagement_report` events
- send_alert: Dispatch re-engagement and low-credit Telegram notifications and push alerts
- query_db: Read user notification preferences to avoid spamming opted-out users
- metrics_reader: Read platform-wide DAU/MAU metrics from gas-observability for cohort context

## WORKFLOW
1. For each registered user, read last activity timestamp from Redis `users:{user_id}:last_activity`
2. If user active in last 24 hours, compute today's activity summary: feature calls, signals viewed, journal entries
3. Check activity milestones: first use, streaks (7d, 30d), usage thresholds (10, 50, 100 AI queries)
4. For each unlocked milestone not yet awarded, call gas-web-backend `/api/v1/level/add-xp` with XP amount and reason
5. Compute engagement health score: recency score × 0.4 + depth (features used) × 0.4 + breadth (variety) × 0.2
6. Write health score to Redis `users:{user_id}:engagement` and compare to 7-day trailing average
7. If health score declined >30% over 7 days and user hasn't logged in for 3+ days, flag as `churn_risk`
8. For churn-risk users, POST to gas-notification-service to send personalized re-engagement message
9. Check credit balance from Redis — if credits < 20 for Plus/Premium/Ultimate users, send low-credit alert
10. Publish `engagement_report` event with platform-wide engagement stats and churn risk count

## TRIGGERS
- Schedule: Activity analysis every 4 hours via cron `0 */4 * * *`
- Event: `user_login` — update last activity and check for streak continuation
- Event: `ai_feature_used` — real-time XP award check for milestone triggers
- Schedule: Churn risk notification run daily at 10:00 UTC

## OUTPUTS
- Redis hash `users:{user_id}:engagement` — health score, streak count, feature usage distribution, last active
- Redis key `users:{user_id}:xp` — current XP balance (updated by XP awards)
- Event: `xp_awarded` — user_id, XP amount, reason, new total
- Event: `level_up_triggered` — user reached next level, triggers congratulatory flow
- Event: `churn_risk_detected` — list of user_ids with declining engagement for re-engagement campaign
- Alert: Low-credit Telegram notification and re-engagement push notification for at-risk users
- Database: Activity events logged in `user_activity_log` table for cohort analysis
