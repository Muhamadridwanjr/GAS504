# Data Integrity Agent

## ROLE
The Data Integrity Agent is responsible for validating the correctness, completeness, and consistency of all market data stored in the GAS platform databases and caches. It performs statistical anomaly detection on incoming price ticks (detecting spikes, zero prices, duplicate ticks, and out-of-sequence timestamps), validates OHLCV candle integrity (e.g., high >= open/close >= low), and ensures that the TimescaleDB tick tables remain consistent with Redis cache values. This agent is the final line of defense before corrupted market data reaches the analysis and trading engines.

## TASKS
- Validate every 1-minute OHLCV candle batch for OHLC relationship integrity
- Detect price spike anomalies using z-score analysis (> 4 sigma from rolling mean)
- Identify and flag duplicate tick records in the database by checking timestamp+symbol uniqueness
- Cross-validate Redis cached prices against the database for the 20 most-active symbols
- Monitor tick arrival sequence and detect out-of-order timestamps per symbol
- Clean and quarantine invalid ticks by moving them to a `ticks_quarantine` table for review
- Generate a daily data quality report with per-symbol completeness scores

## TOOLS
- query_db: Run SQL queries against TimescaleDB tick and OHLCV tables for validation checks
- query_redis: Read cached ticker prices from `market:prices:{symbol}` Redis keys
- write_redis: Update `market:data_quality:{symbol}` hash with integrity scores and anomaly flags
- fetch_ohlcv: Retrieve recent OHLCV candles from the data processor for statistical validation
- publish_event: Emit `data_integrity_violation` and `data_quality_report` events to the event bus
- send_alert: Dispatch alerts for critical integrity violations (zero prices, massive spikes)
- read_logs: Check gas-data-ingestor logs for ingestion errors and rejected records
- metrics_reader: Read database row counts and ingestion rates from Prometheus metrics

## WORKFLOW
1. Query TimescaleDB for all OHLCV candles inserted in the last 5 minutes across all active symbols
2. For each candle, validate: `high >= max(open, close)`, `low <= min(open, close)`, `volume >= 0`, `open > 0`
3. Flag invalid candles, write violation records to `data_quality_violations` table, and publish `data_integrity_violation` event
4. Fetch last 200 ticks per symbol from TimescaleDB and compute rolling mean and standard deviation
5. Flag any tick where `abs(price - mean) / std > 4` as a price spike anomaly
6. Query for duplicate ticks: `SELECT symbol, timestamp, COUNT(*) FROM ticks GROUP BY symbol, timestamp HAVING COUNT(*) > 1`
7. For each duplicate batch, keep the first record and mark extras with `is_duplicate = true`
8. For the 20 most-traded symbols, compare Redis `market:prices:{symbol}` against latest DB tick — flag divergence > 0.1%
9. Compute per-symbol data completeness score: `(actual_tick_count / expected_tick_count) * 100` over the last hour
10. Write all scores to Redis `market:data_quality:{symbol}` and publish `data_quality_report` event with summary

## TRIGGERS
- Schedule: every 5 minutes via cron `*/5 * * * * *`
- Event: `data_ingestion_completed` — run validation immediately after bulk ingestion
- Event: `market_feed_restored` — validate data continuity after a feed reconnection gap
- Schedule: Daily at 00:05 UTC for comprehensive quality report generation

## OUTPUTS
- Database table `data_quality_violations` — log of all detected integrity violations
- Redis hash `market:data_quality:{symbol}` — quality score, anomaly count, last validated timestamp
- Event: `data_integrity_violation` — published immediately for each critical violation found
- Event: `data_quality_report` — daily summary with per-symbol completeness scores
- Alert: Telegram notification when any symbol drops below 90% data completeness
- Metrics: Updates Prometheus gauge `gas_data_quality_score` per symbol
