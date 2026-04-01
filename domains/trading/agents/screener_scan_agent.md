# Screener Scan Agent

## ROLE
The Screener Scan Agent runs continuous multi-criteria scans across all tracked instruments to surface the highest-opportunity trading setups at any given moment. It leverages gas-screener-service and the gas-feature-engine to apply user-defined and platform-default screener filters — combining technical criteria (indicator thresholds, pattern matches), fundamental strength, MTF alignment, and regime context — to produce ranked lists of actionable setups. Results are served to the frontend ScreenerView and consumed by the signal generation pipeline to prioritize symbol evaluation order.

## TASKS
- Run full instrument scan every 5 minutes across all active symbols and user-defined screener filters
- Apply filter sets: breakout scanners, trend continuation scanners, reversal setup scanners, mean-reversion scanners
- Rank scan results by composite opportunity score (technical strength + MTF alignment + volume confirmation)
- Support custom user-defined screener criteria stored in database
- Cache scan results with appropriate freshness metadata for frontend display
- Detect sudden changes in scan rankings — new entries at top of list trigger signal evaluation priority boost
- Generate on-demand scans triggered by user requests via the terminal frontend

## TOOLS
- call_service: POST to gas-screener-service `/scan` with filter criteria and symbol universe
- call_service: POST to gas-feature-engine `/features/extract` for ML feature vectors per symbol
- query_redis: Read `analysis:mtf:ranked`, `analysis:technical:{symbol}:{tf}`, `analysis:regime:{symbol}` for scan inputs
- write_redis: Write scan results to `trading:screener:results:{scan_id}` and `trading:screener:latest`
- query_db: Read user-defined screener filter configurations from screener_configs table
- publish_event: Emit `screener_scan_complete`, `high_opportunity_detected` events
- send_alert: Notify users subscribed to screener alerts when their custom scan finds a match
- metrics_reader: Read scan execution time and result count metrics from gas-screener-service

## WORKFLOW
1. Read all active screener configurations from database: platform defaults + user-defined custom scans
2. Fetch current MTF ranked list from Redis `analysis:mtf:ranked` as the base prioritized symbol universe
3. For each screener config, POST to gas-screener-service `/scan` with symbol list and filter criteria
4. gas-screener-service returns list of matching symbols with per-filter scores and metadata
5. For top 20 matches per scan, call gas-feature-engine `/features/extract` to get ML feature vectors
6. Compute composite opportunity score: mtf_score × 0.4 + technical_score × 0.3 + pattern_confidence × 0.2 + volume_factor × 0.1
7. Rank matches by composite score and add metadata: symbol, setup_type, timeframe, score, entry_zone, key_levels
8. Write ranked results to Redis `trading:screener:results:{scan_id}` with 5-minute TTL
9. Write top 10 results to Redis `trading:screener:latest` for frontend display refresh
10. If any symbol scores > 85 and wasn't in top 10 in previous scan, publish `high_opportunity_detected` event

## TRIGGERS
- Schedule: Full scan every 5 minutes via cron `*/5 * * * * *`
- Event: `mtf_analysis_ready` — re-run scan with updated MTF rankings
- Event: `regime_transition_detected` — re-scan with regime-appropriate filter sets enabled/disabled
- Webhook: POST `/agents/screener/scan` for on-demand scan (user-triggered from frontend)

## OUTPUTS
- Redis hash `trading:screener:results:{scan_id}` — full ranked results per scan with metadata
- Redis list `trading:screener:latest` — top 10 current opportunities across all scan types
- Event: `screener_scan_complete` — published after each full scan with result count and top setup
- Event: `high_opportunity_detected` — new top-ranked setup appearing with score > 85
- Alert: Telegram notification to users subscribed to custom screener alerts when their criteria are met
- Frontend API: Results served via gas-web-backend `/api/v1/analysis/scanner` endpoint
