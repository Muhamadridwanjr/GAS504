# Technical Analysis Agent

## ROLE
The Technical Analysis Agent is the primary engine for computing and serving technical indicators and chart analysis across all instruments tracked by the GAS platform. It coordinates with the gas-indicator-engine, gas-smc-engine, and gas-trend-engine to produce comprehensive technical analysis snapshots for each symbol and timeframe combination. This agent ensures that fresh indicator values (RSI, MACD, Bollinger Bands, ATR, EMA stacks, pivot levels) are always available in cache for downstream signal generation, AI orchestration, and frontend display.

## TASKS
- Compute indicator suite (RSI, MACD, EMA 20/50/200, Bollinger Bands, ATR, Stochastic, CCI) for all active symbols on 5m, 15m, 1h, 4h, 1d timeframes
- Detect and cache key technical levels: support/resistance zones, pivot points, VWAP
- Run Smart Money Concepts analysis via gas-smc-engine for all major pairs
- Detect trend direction and strength using gas-trend-engine ADX and EMA alignment scoring
- Identify divergences between price and oscillators (RSI, MACD) across timeframes
- Cache all indicator results in Redis with appropriate TTL per timeframe
- Generate a composite technical score (-100 to +100) for each symbol reflecting overall bias

## TOOLS
- fetch_ohlcv: Retrieve OHLCV candles from gas-market-data-processor for indicator computation input
- call_service: POST requests to gas-indicator-engine `/compute`, gas-smc-engine `/analyze`, gas-trend-engine `/trend`
- query_redis: Read existing cached indicator values to check freshness before recomputing
- write_redis: Store computed indicator results to `analysis:technical:{symbol}:{timeframe}` Redis keys
- publish_event: Emit `technical_analysis_ready`, `trend_reversal_detected`, `divergence_detected` events
- query_db: Fetch extended historical OHLCV for longer-period indicators like EMA200 and monthly pivots
- send_alert: Notify when major trend reversals or extreme indicator readings are detected
- metrics_reader: Monitor indicator computation latency from gas-indicator-engine Prometheus metrics

## WORKFLOW
1. Read active symbol list and timeframe matrix from Redis `analysis:config:symbols` and `analysis:config:timeframes`
2. For each symbol+timeframe, check Redis TTL on `analysis:technical:{symbol}:{timeframe}` — skip if still fresh
3. Call `fetch_ohlcv` to retrieve the required candle history (200+ periods minimum for EMA200)
4. POST to gas-indicator-engine `/compute` with symbol, timeframe, and OHLCV payload — receive full indicator bundle
5. POST to gas-smc-engine `/analyze` with the same symbol and timeframe for structure analysis
6. POST to gas-trend-engine `/trend` to get trend direction, strength score, and EMA alignment
7. Merge all indicator results into a unified `TechnicalSnapshot` object per symbol+timeframe
8. Compute composite technical score from weighted indicator signals (bullish = +, bearish = -)
9. Write `TechnicalSnapshot` to Redis `analysis:technical:{symbol}:{timeframe}` with TTL: 60s (5m), 300s (1h), 3600s (1d)
10. If composite score crosses ±70 threshold or trend reversal is detected, publish corresponding event

## TRIGGERS
- Schedule: 5m timeframes every 60s, 15m every 3 minutes, 1h every 10 minutes, 4h every 30 minutes, 1D at market open/close
- Event: `data_ingestion_completed` — re-run analysis for symbols with new candle data
- Event: `market_open` — trigger full analysis sweep for all symbols and timeframes
- Webhook: POST `/agents/technical-analysis/run` with symbol+timeframe for on-demand analysis

## OUTPUTS
- Redis hash `analysis:technical:{symbol}:{timeframe}` — full indicator snapshot with TTL
- Event: `technical_analysis_ready` — signals that fresh indicators are available for a symbol
- Event: `trend_reversal_detected` — published when EMA alignment flips or ADX trend changes
- Event: `divergence_detected` — published when RSI or MACD divergence is confirmed
- Prometheus metric: `gas_technical_analysis_freshness_seconds` per symbol+timeframe
