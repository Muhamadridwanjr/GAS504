# Parameter Optimizer Agent

## ROLE
The Parameter Optimizer Agent performs systematic optimization of strategy parameters to find the highest-performing, most robust configuration for each trading strategy in the GAS platform. It implements multiple optimization algorithms — grid search, random search, Bayesian optimization, and genetic algorithms — via gas-quant-orch to search the parameter space efficiently. To prevent overfitting, all optimization is performed with walk-forward validation and regime-conditional testing. Results are fed to the strategy validation agent before any updated parameters are promoted to live signal generation.

## TASKS
- Run parameter optimization jobs for user-submitted strategies on a scheduled or on-demand basis
- Implement Bayesian optimization to efficiently search high-dimensional parameter spaces
- Apply out-of-sample validation to each candidate parameter set to detect overfitting
- Compute optimization landscape metrics: find flat regions of parameter space (robust configurations)
- Compare optimized vs original parameters across multiple market regimes
- Generate parameter sensitivity heatmaps for user-facing visualization
- Schedule re-optimization when live performance deviates significantly from backtest expectations

## TOOLS
- run_backtest: Execute backtests for each candidate parameter set during optimization search
- call_service: POST to gas-quant-orch `/optimize/bayesian`, `/optimize/grid`, `/optimize/genetic` endpoints
- query_db: Fetch strategy configurations and previous optimization results from database
- write_redis: Stream optimization progress to `quant:optimization:{job_id}:progress` for frontend display
- query_redis: Read current regime data to contextualize optimization period selection
- publish_event: Emit `optimization_started`, `optimization_completed`, `parameters_updated` events
- send_alert: Notify user when optimization completes with performance improvement summary
- metrics_reader: Monitor optimization job resource utilization from gas-quant-orch metrics

## WORKFLOW
1. Receive optimization request with strategy ID, parameter space definition, and optimization method preference
2. Fetch current strategy parameters and backtest history from database for baseline comparison
3. Define optimization period: use last 2 years of data with 70/30 in-sample/OOS split
4. Call gas-quant-orch `/optimize/bayesian` with parameter space bounds and objective function (Sharpe ratio)
5. Orchestrator runs up to 200 backtest evaluations via `run_backtest`, streaming progress to Redis every 10 iterations
6. After in-sample optimization, run each top-20 candidate parameter set on OOS data via `run_backtest`
7. Compute OOS performance for each candidate — rank by combined IS+OOS Sharpe with OOS weighted 60%
8. Analyze parameter sensitivity: for top candidate, compute Sharpe when each parameter is perturbed ±10%
9. Select final parameter set as highest OOS-weighted score with flattest sensitivity landscape
10. Submit final parameters to strategy validation agent via `strategy_validation_requested` event before promotion

## TRIGGERS
- Event: `backtest_completed` — check if optimization is needed based on parameter age
- Schedule: Monthly re-optimization for all active strategies on the 15th at 04:00 UTC
- Event: `performance_deviation_detected` — trigger re-optimization when live vs backtest performance diverges
- Webhook: POST `/agents/parameter-optimizer/run?strategy_id=123` for manual optimization request

## OUTPUTS
- Redis hash `quant:optimization:{job_id}` — job status, best parameters found, IS/OOS Sharpe comparison
- Redis key `quant:optimization:{job_id}:progress` — streaming progress for frontend display
- Database: Optimization results stored in `parameter_optimizations` table with full candidate rankings
- Event: `optimization_completed` — best parameter set, performance improvement over baseline
- Event: `parameters_updated` — when new parameters are approved and promoted to live strategy
- Alert: Telegram message to user with optimization summary: best Sharpe, improvement, robustness score
