# Strategy Validation Agent

## ROLE
The Strategy Validation Agent performs rigorous statistical validation of trading strategies to distinguish genuine edge from overfitting and data-mining bias. It applies a battery of statistical tests — Monte Carlo simulation, permutation tests, out-of-sample validation, and regime-conditional performance analysis — to every strategy before it is approved for live signal generation. This agent acts as a quantitative gatekeeper, preventing under-tested strategies from reaching users and providing a transparent confidence rating for each validated strategy's live performance expectations.

## TASKS
- Run Monte Carlo simulation (1000 iterations) on each strategy's trade log to compute realistic performance distribution
- Execute permutation tests to verify that strategy performance is statistically significant vs random entry
- Validate strategy on out-of-sample data using walk-forward splits (70% in-sample, 30% out-of-sample)
- Compute regime-conditional performance: does strategy work in trending markets but fail in ranging regimes?
- Detect overfitting via stability analysis: performance sensitivity to parameter perturbations
- Assign strategy confidence rating (A/B/C/F) based on statistical test results
- Maintain strategy validity records and trigger re-validation when market regime shifts

## TOOLS
- run_backtest: Execute backtest with permuted entry signals for null hypothesis testing
- call_service: POST to gas-quant-orch `/validate/montecarlo`, `/validate/permutation`, `/validate/oos` endpoints
- query_db: Fetch completed backtest trade logs from `backtest_results` table for statistical testing
- write_redis: Cache validation results to `quant:validation:{strategy_id}` and strategy rating index
- query_redis: Read current regime classification from `analysis:regime:{symbol}` for conditional analysis
- publish_event: Emit `strategy_validated`, `strategy_invalidated`, `validation_failed` events
- send_alert: Notify strategy owner when validation rating changes or strategy is invalidated
- metrics_reader: Read validation engine performance metrics and compute time from gas-observability

## WORKFLOW
1. Receive `backtest_completed` event — read trade log from TimescaleDB `backtest_results` for the completed backtest
2. Compute basic statistics: win rate, profit factor, Sharpe ratio, maximum drawdown — reject if Sharpe < 0.5
3. Call gas-quant-orch `/validate/montecarlo` with trade log — run 1000 simulations via random sampling with replacement
4. Receive MC distribution: median Sharpe, 5th percentile Sharpe, probability of ruin — reject if P(ruin) > 5%
5. Call `/validate/permutation` — shuffle entry signals 500 times, compute null distribution of returns
6. Compute p-value: what fraction of permuted runs exceed actual strategy performance? Reject if p-value > 0.05
7. Call `/validate/oos` with walk-forward splits — validate performance consistency across out-of-sample periods
8. Read regime classification for strategy's primary trading pair — compute conditional performance per regime type
9. Run parameter sensitivity analysis: perturb each parameter ±10% and measure Sharpe stability (coefficient of variation)
10. Assign rating: A (all tests pass, Sharpe > 1.5), B (most pass, Sharpe > 1.0), C (marginal), F (fails); publish `strategy_validated` event

## TRIGGERS
- Event: `backtest_completed` — primary trigger for new strategy validation
- Schedule: Re-validation for all active strategies monthly on the 1st at 03:00 UTC
- Event: `regime_transition_detected` — re-test regime-dependent strategies under new conditions
- Webhook: POST `/agents/strategy-validation/run?strategy_id=123` for manual validation request

## OUTPUTS
- Redis hash `quant:validation:{strategy_id}` — rating, MC stats, permutation p-value, OOS Sharpe, regime breakdown
- Database record in `strategy_validations` table — full validation report with all statistical test results
- Event: `strategy_validated` — rating, confidence level, conditional regime performance summary
- Event: `strategy_invalidated` — when re-validation shows strategy has lost its statistical edge
- Alert: Telegram notification to strategy owner with validation rating and key stats
