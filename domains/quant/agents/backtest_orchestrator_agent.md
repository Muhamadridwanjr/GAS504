# Backtest Orchestrator Agent

## ROLE
The Backtest Orchestrator Agent manages the full lifecycle of backtesting jobs on the GAS platform, from job submission through execution, monitoring, and result delivery. It coordinates gas-quant-backtester and gas-quant-orch to schedule and execute backtests across historical data ranges, handles resource allocation to prevent concurrent backtests from overwhelming the system, streams progress updates to the frontend, and stores results with full trade-by-trade statistics in the database. This agent enables users to validate strategy performance and generate walk-forward analysis across different market regimes.

## TASKS
- Accept backtest job submissions and queue them with priority based on user subscription tier
- Allocate backtest execution resources — limit concurrent backtests based on available compute
- Execute backtests via gas-quant-backtester with full parameter sets and historical data
- Stream real-time progress updates to frontend via WebSocket/Redis pub-sub
- Compute comprehensive performance statistics: Sharpe ratio, maximum drawdown, win rate, profit factor, expectancy
- Store complete backtest results with per-trade log for download and journal integration
- Run walk-forward optimization splits for strategy robustness validation

## TOOLS
- call_service: POST to gas-quant-backtester `/backtest/run`, `/backtest/status/{id}`, gas-quant-orch `/orchestrate`
- run_backtest: Direct invocation of backtest engine with OHLCV data and strategy parameters
- query_db: Fetch historical OHLCV data and existing backtest results from TimescaleDB
- write_redis: Stream progress updates to `backtest:progress:{job_id}` and queue to `backtest:queue`
- query_redis: Read job queue and concurrency counter from `backtest:running_count`
- publish_event: Emit `backtest_started`, `backtest_completed`, `backtest_failed` events
- send_alert: Notify user when long-running backtest completes or fails
- metrics_reader: Monitor gas-quant-backtester CPU and memory utilization during execution

## WORKFLOW
1. Receive backtest job from `backtest_queue` event or direct API call — validate parameters (symbol, date range, strategy config)
2. Check concurrent backtest count from Redis `backtest:running_count` — queue job if at capacity limit (default 3)
3. Increment Redis `backtest:running_count` and write job metadata to `backtest:jobs:{job_id}` with status=running
4. Fetch OHLCV data from TimescaleDB for the requested symbol, timeframe, and date range
5. POST to gas-quant-backtester `/backtest/run` with OHLCV data and strategy parameters — receive job handle
6. Poll `/backtest/status/{id}` every 5 seconds — stream progress percentage to Redis `backtest:progress:{job_id}`
7. When backtest completes, receive trade log and equity curve from backtester service
8. Compute performance metrics: Sharpe=(mean_return/std_return)*sqrt(252), MaxDD, win_rate, profit_factor, expectancy
9. Store full results in TimescaleDB `backtest_results` table with trade log JSON blob
10. Publish `backtest_completed` event with summary statistics and send Telegram notification to user

## TRIGGERS
- Event: `backtest_job_submitted` — primary trigger from user UI submission
- Schedule: Walk-forward backtest runs for active strategies every Sunday at 02:00 UTC
- Event: `strategy_parameters_updated` — re-run backtest for the updated strategy configuration
- Webhook: POST `/agents/backtest-orchestrator/submit` for API-based backtest submission

## OUTPUTS
- Redis hash `backtest:jobs:{job_id}` — job status, progress, result summary, and completion timestamp
- Redis key `backtest:progress:{job_id}` — streaming progress for frontend WebSocket display
- TimescaleDB `backtest_results` table — complete results with equity curve and per-trade log
- Event: `backtest_completed` — result summary with key performance metrics
- Event: `backtest_failed` — error details and job metadata for debugging
- Alert: Telegram message to user when backtest completes with top-line performance stats
