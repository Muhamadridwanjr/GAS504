# Fundamental Data Agent

## ROLE
The Fundamental Data Agent is responsible for ingesting, processing, and maintaining all macroeconomic and fundamental data relevant to the traded instruments on the GAS platform. It coordinates gas-fundamental-data-service to fetch central bank rate decisions, GDP reports, CPI/PPI data, employment figures, PMI readings, and commodity supply/demand fundamentals. This agent translates raw fundamental data into structured market impact scores that can be consumed by signal generation, regime classification, and the AI orchestrator for macro-informed trading decisions.

## TASKS
- Fetch and store major macroeconomic data releases from configured data providers
- Compute currency fundamental strength scores based on relative interest rates and economic health
- Process commodity fundamentals: EIA oil inventories, gold ETF flows, agricultural supply data
- Update central bank policy stance tracker: hawkish/neutral/dovish for all G10 central banks
- Correlate fundamental data releases with subsequent price action for impact scoring
- Maintain a fundamental data freshness index — flag stale data that needs updating
- Generate fundamental summary snapshots for AI orchestrator consumption

## TOOLS
- call_service: GET/POST requests to gas-fundamental-data-service `/fundamentals`, `/macro`, `/rates` endpoints
- query_db: Query fundamental_data table in TimescaleDB for historical fundamental readings
- write_redis: Cache fundamental scores to `analysis:fundamental:{currency_or_asset}` Redis hashes
- query_redis: Read cached scores and check data freshness timestamps
- publish_event: Emit `fundamental_data_updated`, `central_bank_stance_changed`, `macro_shock` events
- fetch_ohlcv: Retrieve price data to correlate with fundamental releases for impact analysis
- send_alert: Alert on major fundamental shifts (rate hike surprise, major data miss/beat)
- read_logs: Monitor gas-fundamental-data-service for ingestion errors or provider outages

## WORKFLOW
1. Read fundamental data freshness index from Redis `analysis:fundamental:freshness` — identify stale datasets
2. For stale currencies, call gas-fundamental-data-service `GET /macro/{currency}` to fetch latest macro readings
3. Fetch central bank policy data via `GET /rates/central-banks` — parse stance (hawkish/dovish/neutral)
4. For each currency, compute fundamental strength score from: interest rate differential, GDP growth, CPI trajectory, employment trend
5. Process commodity fundamentals: call `GET /fundamentals/commodities` for oil, gold, and agricultural data
6. Query TimescaleDB for last 10 fundamental data releases per currency — compute average surprise magnitude
7. Update `analysis:fundamental:{currency}` Redis hash with: strength_score, cb_stance, last_rate, cpi, gdp_growth
8. Detect stance changes: if previous stance != current stance, publish `central_bank_stance_changed` event
9. Correlate last 5 data releases with price movement over subsequent 4 hours for impact coefficient update
10. Publish `fundamental_data_updated` event with list of updated currencies/commodities and summary scores

## TRIGGERS
- Schedule: Full refresh every 6 hours via cron `0 */6 * * *`
- Schedule: Rates and central bank data refresh daily at 06:00 UTC
- Event: `calendar_event_completed` — re-run fundamental scoring after major economic data release
- Event: `macro_news_published` — parse and integrate breaking fundamental news
- Webhook: POST `/agents/fundamental-data/run?currency=USD` for targeted fundamental refresh

## OUTPUTS
- Redis hash `analysis:fundamental:{currency_or_asset}` — strength score, CB stance, key macro indicators
- Event: `fundamental_data_updated` — list of updated assets with new scores and change deltas
- Event: `central_bank_stance_changed` — critical event triggering regime reclassification
- Event: `macro_shock` — published for major surprise data releases (miss/beat > 2 standard deviations)
- Alert: Telegram notification for central bank stance changes and major data shocks
- TimescaleDB: Persisted history of all fundamental readings in `fundamental_data` table
