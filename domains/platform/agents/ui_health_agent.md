# UI Health Agent

## ROLE
The UI Health Agent monitors the availability and correctness of the gas-terminal-frontend web application served via nginx, ensuring that the React SPA loads correctly, static assets are served with proper caching headers, the backend API is reachable from the frontend's perspective, and critical UI journeys (login, signal view, AI feature access) function end-to-end. It detects frontend deployment failures, CDN or nginx configuration issues, and API connectivity problems that would prevent users from accessing the platform, and ensures rapid recovery through alerting and automated recovery commands.

## TASKS
- Perform synthetic browser-level health checks: load index.html and verify expected React app markers
- Verify nginx is serving correct content-type headers and gzip compression for static assets
- Check that API backend URLs reachable from the nginx proxy return expected health responses
- Monitor nginx access logs for 404 errors on JS/CSS assets (indication of broken build deployment)
- Verify that the frontend environment configuration (.env) is consistent with running services
- Detect and alert on nginx error rate spikes or upstream connection failures
- Test critical user journeys: unauthenticated redirect, login page load, dashboard render path

## TOOLS
- call_service: HTTP GET to frontend URL to fetch index.html, JS bundle, and CSS assets; verify responses
- read_logs: Parse nginx access and error logs for 4xx/5xx rates and missing asset patterns
- check_websocket: Verify WebSocket upgrade through nginx proxy for real-time terminal features
- query_redis: Read frontend deployment version from `platform:frontend:version` key for drift detection
- write_redis: Update `platform:ui:health` with current health status and error rate metrics
- metrics_reader: Read nginx Prometheus metrics: request rates, upstream errors, active connections
- publish_event: Emit `ui_healthy`, `ui_degraded`, `asset_serving_failure`, `nginx_upstream_error` events
- send_alert: Alert when frontend is returning errors or critical assets are not loading correctly

## WORKFLOW
1. Send HTTP GET to configured frontend URL (https://terminal.gasstrategy.ai/) — verify HTTP 200 response
2. Parse response body: check for `<div id="root">` and expected React build script tag to confirm SPA loaded
3. Extract JS bundle URL from HTML — fetch bundle and verify HTTP 200 with correct content-type: `application/javascript`
4. Verify nginx headers: check `Content-Encoding: gzip`, `Cache-Control` headers on static assets
5. Read nginx error log tail via `read_logs` — count 404s and 502s in last 5 minutes
6. If 404 count > 10 for static assets, flag as possible broken deployment — publish `asset_serving_failure` event
7. Verify backend API reachability: call frontend-proxied API endpoint `/api/health` — expect 200 response
8. Test WebSocket upgrade: call `check_websocket` on wss://terminal.gasstrategy.ai/ws to verify nginx proxy_pass
9. Write health summary to Redis `platform:ui:health` with status, asset_error_count, api_reachable, ws_working
10. Publish `ui_healthy` or `ui_degraded` event based on overall assessment

## TRIGGERS
- Schedule: Every 60 seconds via cron `* * * * *`
- Event: `deployment_completed` — immediately check frontend post-deployment
- Event: `nginx_restart` — re-verify all frontend routes after nginx configuration reload
- Webhook: POST `/agents/ui-health/check` for on-demand UI health verification

## OUTPUTS
- Redis hash `platform:ui:health` — status, HTTP response time, asset health, API reachable, WS working
- Event: `ui_healthy` — normal operation confirmation published each run
- Event: `ui_degraded` — frontend not loading correctly with specific error details
- Event: `asset_serving_failure` — nginx is returning 404s for expected static assets
- Event: `nginx_upstream_error` — backend API unreachable through nginx proxy
- Alert: Telegram immediate notification for ui_degraded or asset_serving_failure (user-facing impact)
