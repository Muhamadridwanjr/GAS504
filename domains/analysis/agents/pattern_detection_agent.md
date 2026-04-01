# Pattern Detection Agent

## ROLE
The Pattern Detection Agent scans all tracked instruments across multiple timeframes to identify classical chart patterns (head and shoulders, double tops/bottoms, triangles, flags, wedges, cup and handle) as well as candlestick patterns (engulfing, doji, hammer, shooting star, morning/evening star). It leverages gas-pattern-detector to run the actual detection algorithms, enriches each detection with context (volume confirmation, trend alignment, proximity to key levels), assigns a confidence score, and caches the results for consumption by signal generation and the AI orchestrator.

## TASKS
- Scan all active symbols for classical chart patterns on 15m, 1h, 4h, and 1D timeframes
- Detect high-probability candlestick patterns on the most recent 3 bars per symbol+timeframe
- Enrich each detected pattern with volume confirmation and trend alignment context
- Assign a confidence score (0-100) to each detected pattern based on formation quality
- Track pattern completion progress (e.g., handle forming in cup-and-handle)
- Invalidate stale patterns that have been broken without triggering
- Cross-reference detected patterns with key support/resistance levels from the technical analysis cache

## TOOLS
- fetch_ohlcv: Retrieve OHLCV candles needed for pattern scanning (minimum 100 bars)
- call_service: POST to gas-pattern-detector `/detect` with candle payload and pattern type filter
- query_redis: Read cached technical snapshots from `analysis:technical:{symbol}:{timeframe}` for context enrichment
- write_redis: Store detected patterns to `analysis:patterns:{symbol}:{timeframe}` sorted sets
- publish_event: Emit `pattern_detected`, `pattern_completed`, `pattern_invalidated` events
- query_db: Fetch volume history for volume confirmation analysis
- send_alert: Notify when high-confidence patterns (>80 score) form on major pairs in key timeframes
- metrics_reader: Monitor pattern detection throughput and false positive rates

## WORKFLOW
1. Read symbol+timeframe scan matrix from Redis — prioritize 4H and 1D patterns as highest value
2. For each symbol+timeframe, call `fetch_ohlcv` with 200-bar history for classical pattern scanner
3. POST to gas-pattern-detector `/detect/classical` with candle data — receive list of PatternResult objects
4. POST to gas-pattern-detector `/detect/candlestick` with last 10 bars for candlestick patterns
5. For each detected pattern, read `analysis:technical:{symbol}:{timeframe}` from Redis for trend context
6. Compute volume confirmation: compare pattern formation volume against 20-period average volume
7. Assign confidence score: base score from pattern geometry quality + volume bonus + trend alignment bonus
8. Check if pattern target/stop levels align with cached support/resistance zones (adds +10 confidence)
9. Write all patterns above confidence 40 to Redis sorted set `analysis:patterns:{symbol}:{timeframe}` scored by confidence
10. Publish `pattern_detected` event for each pattern above confidence 70, and `send_alert` for patterns above 85

## TRIGGERS
- Schedule: 15m timeframe scans every 3 minutes, 1h every 10 minutes, 4h every 30 minutes, 1D at 00:01 UTC
- Event: `technical_analysis_ready` — re-scan for newly formed patterns after indicator update
- Event: `market_open` — full pattern sweep for all symbols at session open
- Webhook: POST `/agents/pattern-detection/run?symbol=EURUSD&timeframe=1h` for on-demand scan

## OUTPUTS
- Redis sorted set `analysis:patterns:{symbol}:{timeframe}` — detected patterns ranked by confidence
- Event: `pattern_detected` — includes pattern type, symbol, timeframe, confidence, target, and stop levels
- Event: `pattern_completed` — when a forming pattern (e.g., triangle) breaks out with confirmation
- Event: `pattern_invalidated` — when price action breaks a developing pattern's structure
- Alert: Telegram message for high-confidence patterns (>85) on major pairs (EURUSD, XAUUSD, BTCUSDT)
