# Regime Classification Agent

## ROLE
The Regime Classification Agent determines the current market regime for each tracked instrument — categorizing market conditions as trending (bullish/bearish), ranging, volatile, or transitioning. It coordinates gas-regime-detector and gas-market-phase to apply multiple regime classification methodologies including Hidden Markov Models, volatility clustering, ADX-based trend detection, and Wyckoff phase analysis. The output regime classification is critical for adapting signal generation strategies: trend-following signals are suppressed in ranging markets while mean-reversion setups are prioritized.

## TASKS
- Classify current market regime for each symbol on 1h, 4h, and 1D timeframes
- Apply Wyckoff phase analysis to identify accumulation, markup, distribution, and markdown phases
- Compute volatility regime: low/normal/high/extreme using ATR percentile rankings
- Detect regime transitions — the most actionable condition for trend traders
- Assign regime confidence score and expected duration estimate
- Feed regime classification into a Redis key read by signal generation and risk engines
- Generate daily regime summary report for AI briefing consumption

## TOOLS
- fetch_ohlcv: Retrieve OHLCV history for regime computation (minimum 500 bars for HMM stability)
- call_service: POST to gas-regime-detector `/classify` and gas-market-phase `/wyckoff` endpoints
- query_redis: Read existing regime classifications and transition history from Redis
- write_redis: Persist regime results to `analysis:regime:{symbol}:{timeframe}` Redis hashes
- publish_event: Emit `regime_classified`, `regime_transition_detected`, `volatility_spike` events
- query_db: Fetch extended historical data for volatility percentile calculation
- send_alert: Alert on regime transitions for major pairs (actionable trading context)
- metrics_reader: Read regime classification model performance metrics from gas-observability

## WORKFLOW
1. Read the last classified regime for each symbol+timeframe from Redis `analysis:regime:{symbol}:{timeframe}`
2. Determine if reclassification is needed: 4H regime stale after 30 minutes, 1D regime stale after 4 hours
3. Call `fetch_ohlcv` with 500 bars for HMM-based classification and ATR percentile computation
4. POST to gas-regime-detector `/classify` with OHLCV data — receive regime label, confidence, and state probabilities
5. POST to gas-market-phase `/wyckoff` to get current Wyckoff phase and expected next phase
6. Compute volatility regime: calculate current ATR vs ATR percentile ranks over past 252 trading days
7. Combine regime signals: if HMM says trending and Wyckoff says markup, assign high-confidence bullish trend regime
8. Compare new regime to previous regime — if changed, mark as `regime_transition` with transition timestamp
9. Write full regime object to Redis `analysis:regime:{symbol}:{timeframe}` with fields: regime, phase, volatility, confidence, transition, timestamp
10. If regime transition detected, publish `regime_transition_detected` event; if volatility > 90th percentile, publish `volatility_spike`

## TRIGGERS
- Schedule: 1h timeframes every 10 minutes, 4h every 30 minutes, 1D at 00:15 UTC daily
- Event: `volatility_spike` — immediately reclassify all symbols when market-wide volatility surges
- Event: `major_news_released` — reclassify affected currency/commodity pairs post-news
- Webhook: POST `/agents/regime-classification/run?symbol=XAUUSD` for targeted reclassification

## OUTPUTS
- Redis hash `analysis:regime:{symbol}:{timeframe}` — regime label, Wyckoff phase, volatility regime, confidence score
- Event: `regime_classified` — published after each classification run with full regime object
- Event: `regime_transition_detected` — highest-priority event, triggers signal strategy adaptation
- Event: `volatility_spike` — published when volatility regime moves to extreme tier
- Daily report: Redis key `analysis:regime:daily_report` with platform-wide regime summary for AI briefing
