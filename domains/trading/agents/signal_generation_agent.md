# Signal Generation Agent

## ROLE
The Signal Generation Agent is the core trading decision engine of the GAS platform, responsible for synthesizing inputs from technical analysis, multi-timeframe alignment, pattern detection, orderflow, and fundamental data to produce actionable trade signals. It coordinates gas-signal-service to evaluate entry conditions against a library of strategy rules, validates signal quality against MTF alignment thresholds, applies news event filters, and publishes fully-formed signals with entry, stop-loss, take-profit, and confidence metadata for consumption by the risk engine and alert system.

## TASKS
- Evaluate entry conditions for all active strategies against current market state per symbol
- Filter signals based on MTF alignment score (minimum configurable threshold, default 55)
- Apply news event blackout filter — suppress signals within 15 minutes of high-impact events
- Compute signal confidence score from weighted inputs: technical (40%), MTF (30%), pattern (20%), orderflow (10%)
- Assign risk/reward ratio based on nearest support/resistance levels and ATR-based stop placement
- Rate-limit signal generation per symbol to prevent overtrading (max 3 signals per symbol per session)
- Log all evaluated signals (triggered and filtered) for backtesting feedback loop

## TOOLS
- query_redis: Read `analysis:mtf:{symbol}`, `analysis:technical:{symbol}:{tf}`, `analysis:patterns:{symbol}:{tf}`, `analysis:orderflow:{symbol}` from cache
- call_service: POST to gas-signal-service `/evaluate` with full market state object for strategy rule evaluation
- query_redis: Read `calendar:upcoming` to check for imminent high-impact news events
- write_redis: Write generated signals to `trading:signals:{symbol}` and signal log to `trading:signal_log`
- publish_event: Emit `signal_generated`, `signal_filtered`, `signal_expired` events to event bus
- send_alert: Dispatch signal alerts to Telegram and notification service for subscribed users
- query_db: Read user strategy configurations and signal preferences from database
- metrics_reader: Monitor signal generation rate, filter rates, and win rate from historical performance

## WORKFLOW
1. Read current MTF ranked list from Redis `analysis:mtf:ranked` — process symbols in order of conviction
2. For each symbol, read full analysis stack: MTF score, technical snapshot, patterns, orderflow, regime
3. If MTF score < configured threshold (default 55), log as filtered and skip signal evaluation
4. Check Redis `calendar:upcoming` for events within 15 minutes affecting this symbol's currency — skip if found
5. POST to gas-signal-service `/evaluate` with full market state — receive list of strategy rule matches
6. For each matched strategy, compute confidence: technical_score * 0.4 + mtf_score * 0.3 + pattern_conf * 0.2 + orderflow_conf * 0.1
7. Compute entry, stop-loss (ATR-based or structure-based), and take-profit levels (R:R minimum 1.5:1)
8. Check signal rate limit: read `trading:signal_count:{symbol}:{session}` from Redis — skip if >= 3
9. Write signal to Redis `trading:signals:{symbol}` with full metadata and TTL 4 hours
10. Publish `signal_generated` event with complete signal payload and send alert to subscribed users

## TRIGGERS
- Event: `mtf_analysis_ready` — primary trigger: re-evaluate signals after each MTF sweep
- Event: `pattern_detected` — immediate signal evaluation for high-confidence patterns
- Event: `regime_transition_detected` — re-evaluate all active symbols after regime change
- Schedule: Forced full sweep every 5 minutes via cron `*/5 * * * * *` as safety net
- Webhook: POST `/agents/signal-generation/run?symbol=XAUUSD` for on-demand evaluation

## OUTPUTS
- Redis hash `trading:signals:{symbol}` — active signal with entry, SL, TP, confidence, strategy, expiry
- Redis list `trading:signal_log` — audit log of all evaluated signals with filter reasons
- Event: `signal_generated` — full signal payload for alert dispatch and risk engine processing
- Event: `signal_filtered` — logged filter decisions for analytics and model improvement
- Alert: Telegram signal card with symbol, direction, entry zone, SL, TP, and confidence score
- Prometheus metric: `gas_signals_generated_total`, `gas_signals_filtered_total` counters
