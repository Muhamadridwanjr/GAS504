# Multi-Timeframe Agent

## ROLE
The Multi-Timeframe Agent synthesizes technical analysis, regime classification, and pattern detection results across multiple timeframes into coherent multi-timeframe (MTF) confluence scores. It implements top-down analysis methodology: validating higher-timeframe context (1D, 4H) before evaluating lower-timeframe entry conditions (1H, 15M), and computing an MTF alignment score that quantifies how strongly all timeframes agree on market direction. This agent is the primary input for signal generation — only when MTF alignment exceeds threshold do signals proceed to the risk engine.

## TASKS
- Compute MTF alignment score for each symbol by aggregating bias across 1D, 4H, 1H, and 15M timeframes
- Identify the highest timeframe trend direction and propagate its weight downward
- Detect MTF confluences: setups where 3+ timeframes align in the same direction
- Flag MTF conflicts: situations where higher and lower timeframes are in opposing trends
- Build a priority queue of symbols ranked by MTF alignment strength for screener consumption
- Cache MTF analysis results for consumption by signal generation and AI orchestrator
- Generate a daily MTF market overview across all major pairs for the market briefing

## TOOLS
- query_redis: Read `analysis:technical:{symbol}:{timeframe}` and `analysis:regime:{symbol}:{timeframe}` for each TF
- call_service: POST to gas-smc-engine `/mtf/analyze` for Smart Money MTF structure analysis
- write_redis: Store MTF scores to `analysis:mtf:{symbol}` Redis hashes and ranked list to `analysis:mtf:ranked`
- publish_event: Emit `mtf_confluence_detected`, `mtf_conflict_detected`, `mtf_analysis_ready` events
- fetch_ohlcv: Retrieve candles for timeframes not yet in cache for on-demand analysis
- query_db: Fetch inter-timeframe correlation data for confluence strength calibration
- send_alert: Alert when high-conviction MTF confluences form on major trading pairs
- metrics_reader: Monitor cache hit rates for MTF analysis to optimize computation scheduling

## WORKFLOW
1. For each active symbol, read cached technical snapshots from Redis for timeframes: 1D, 4H, 1H, 15M, 5M
2. If any timeframe cache is stale or missing, trigger `fetch_ohlcv` and queue indicator recomputation
3. Extract bias signal from each timeframe: +1 (bullish), -1 (bearish), 0 (neutral) based on EMA alignment and RSI zone
4. Apply timeframe weights: 1D=40%, 4H=30%, 1H=20%, 15M=10% for weighted MTF score computation
5. POST to gas-smc-engine `/mtf/analyze` for additional SMC-based confluence check (BOS, CHoCH, liquidity sweep)
6. Compute final MTF score: sum of (bias × weight × confidence) across all timeframes, normalized to -100 to +100
7. Classify alignment: score > 60 = strong bullish confluence, < -60 = strong bearish, ±30 to ±60 = moderate, -30 to 30 = conflict
8. Write MTF analysis to Redis `analysis:mtf:{symbol}`: score, classification, per-TF breakdown, top setup timeframe
9. Update Redis sorted set `analysis:mtf:ranked` with symbol scored by abs(mtf_score) for screener
10. Publish `mtf_confluence_detected` for strong confluences (>60), `mtf_conflict_detected` for conflicted markets

## TRIGGERS
- Schedule: Full MTF sweep every 5 minutes via cron `*/5 * * * * *`
- Event: `technical_analysis_ready` — re-run MTF synthesis when any timeframe is updated
- Event: `regime_transition_detected` — immediately recalculate MTF alignment after regime change
- Webhook: POST `/agents/multi-timeframe/analyze?symbol=EURUSD` for on-demand MTF analysis

## OUTPUTS
- Redis hash `analysis:mtf:{symbol}` — MTF score, alignment label, per-timeframe breakdown, dominant TF
- Redis sorted set `analysis:mtf:ranked` — symbols sorted by MTF conviction for screener consumption
- Event: `mtf_confluence_detected` — symbol, score, classification, involved timeframes, setup direction
- Event: `mtf_conflict_detected` — symbol with opposing higher/lower timeframe signals (reduce risk signal)
- Event: `mtf_analysis_ready` — broadcast after each full sweep to notify signal generation to re-evaluate
- Alert: Telegram notification for MTF scores > 80 on EURUSD, XAUUSD, BTCUSDT, GBPUSD
