# Performance Analytics Agent

## ROLE
The Performance Analytics Agent computes, tracks, and reports on real-time and historical trading performance across all user accounts on the GAS platform. It aggregates live position P&L, closed trade statistics, and equity curve data to produce the comprehensive performance dashboards shown in the terminal frontend. This agent also drives the platform leaderboard by computing risk-adjusted performance rankings, generates personalized performance insights for the journal and psychology coaching features, and feeds performance data back to the strategy validation pipeline for continuous model improvement.

## TASKS
- Compute real-time unrealized P&L for all open positions across tracked accounts
- Update closed trade statistics: running totals for win rate, profit factor, average R achieved
- Generate equity curve data points for charting on 1m, 1h, 1D resolution
- Compute drawdown metrics: current drawdown, maximum drawdown, recovery time
- Calculate risk-adjusted metrics: Sharpe ratio (rolling 30-day), Sortino ratio, Calmar ratio
- Rank users for leaderboard by risk-adjusted return and update Redis leaderboard sorted set
- Identify performance patterns: best/worst session, best/worst day of week, best/worst pair

## TOOLS
- query_db: Read closed trade records from `trades` table and open positions from `positions` table
- query_redis: Read current prices from `market:prices:{symbol}` for unrealized P&L computation
- write_redis: Update `performance:{user_id}:summary`, `performance:{user_id}:equity_curve`, and leaderboard sorted set
- call_service: POST to gas-strategy-core `/performance/compute` for advanced metric calculations
- fetch_ohlcv: Get price history for equity curve reconstruction and drawdown computation
- publish_event: Emit `performance_updated`, `new_high_equity`, `drawdown_milestone` events
- send_alert: Notify user on new equity high, significant drawdown milestone, or exceptional performance
- metrics_reader: Read account-level metrics from MT5 heartbeat data in Redis

## WORKFLOW
1. Read all active user accounts from database — fetch latest MT5 heartbeat data from Redis `account:{account_id}:state`
2. For each account, read open positions and current market prices to compute unrealized P&L
3. Combine unrealized P&L with closed trade P&L to compute current equity and daily P&L
4. Compare current equity to previous high-water mark — if new high, publish `new_high_equity` event
5. Compute current drawdown: (high_water_mark - current_equity) / high_water_mark × 100
6. Query TimescaleDB for last 30 days of closed trades — compute rolling Sharpe, Sortino, and Calmar ratios
7. Identify performance patterns: aggregate closed trades by session, weekday, and symbol to find strengths/weaknesses
8. Update Redis `performance:{user_id}:summary` with all metrics and `performance:{user_id}:equity_curve` time series
9. Update leaderboard: compute risk-adjusted rank score = Sharpe × sqrt(trade_count) × (1 - max_drawdown)
10. Write rank score to Redis sorted set `platform:leaderboard` and publish `performance_updated` event

## TRIGGERS
- Schedule: Real-time P&L update every 30 seconds via cron `*/30 * * * * *` during market hours
- Event: `position_closed` — immediately update stats after a trade is closed
- Event: `account_equity_updated` — triggered by MT5 heartbeat when balance changes
- Schedule: Daily performance report generation at 23:00 UTC

## OUTPUTS
- Redis hash `performance:{user_id}:summary` — equity, daily P&L, win rate, Sharpe, current drawdown, streak
- Redis list `performance:{user_id}:equity_curve` — timestamped equity data points for charting
- Redis sorted set `platform:leaderboard` — all users ranked by risk-adjusted performance score
- Event: `performance_updated` — broadcast for UI real-time refresh
- Event: `new_high_equity` — triggers congratulatory notification and XP award
- Event: `drawdown_milestone` — published at -2%, -4%, -6% drawdown levels for escalating alerts
- Alert: Telegram notification for equity highs, drawdown milestones, and daily performance summary
