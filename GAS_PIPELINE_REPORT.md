# GAS — Full System Pipeline Report
> Generated: 2026-03-28 | Author: Claude Code Analysis

---

## 1. ARSITEKTUR KESELURUHAN

```
USER (Telegram)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  gas-telegram-bot  (port 8003)                                  │
│  ├── ReplyKeyboard  — 10 tombol utama (bottom nav)              │
│  ├── InlineKeyboard — submenu & flow steps                      │
│  ├── Workers (8 proses asyncio bersamaan)                       │
│  │   ├── 3× SignalWorker   [q:high,   cache 30s]                │
│  │   ├── 2× AnalysisWorker [q:medium, cache 30s]                │
│  │   ├── 1× AnalystWorker  [q:low,    NO cache, full AI]        │
│  │   ├── 1× ScannerWorker  [q:low,    cache 60s, 5 pairs]       │
│  │   └── 1× FeedWorker     [interval 300s, news+calendar]       │
│  └── Redis Session  — state flow user (TTL 10 menit)            │
└─────────────────┬───────────────────────────────────────────────┘
                  │ POST /api/v1/bot/analyze
                  │ Header: X-Bot-Key
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  gas-web-backend  (port 8005)                                   │
│  ├── /bot/analyze  — verifikasi key, baca plan, potong kredit   │
│  ├── /api/v1/analysis/* — 18 AI features (web terminal)         │
│  ├── /api/v1/billing/*  — kredit, topup, plan                   │
│  └── Redis → user:{id}:plan, user:{id}:credits                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │ POST /v1/analysis/signal
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  gas-strategy-core  (port 7003)                                 │
│  ├── Layer 1: Redis MT5 data (OHLCV multi-TF)                   │
│  ├── Layer 2: Technical Indicators (RSI, MACD, BB, ATR, ADX)   │
│  ├── Layer 3: SMC Engine (OB, FVG, BOS, Liquidity, Kill Zone)  │
│  ├── Layer 4: DXY Correlation (DXY↑=XAU↓, DXY↓=XAU↑)          │
│  ├── Layer 5: Macro + News filter                               │
│  └── AI Engine (OpenRouter / Kimi)                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Redis ohlc:{PAIR}:{TF}
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  gas-mt5-websocket  (port 8110)                                 │
│  ← GAS_StrategyScanner_v5.mq5 (MT5 EA)                         │
│  Mengirim OHLCV semua pair dari Market Watch setiap interval    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. PAIR LIST DI SISTEM (Lengkap)

### 💱 Forex (16 pairs)
| Symbol   | Label         | Live Redis |
|----------|---------------|------------|
| XAUUSD   | Gold / XAU    | ✅ Confirmed |
| EURUSD   | EUR/USD       | ✅ Confirmed |
| GBPUSD   | GBP/USD       | ✅ Confirmed |
| USDJPY   | USD/JPY       | ✅ Confirmed |
| AUDUSD   | AUD/USD       | ✅ Confirmed |
| USDCAD   | USD/CAD       | ✅ Confirmed |
| NZDUSD   | NZD/USD       | ✅ Confirmed |
| USDCHF   | USD/CHF       | ✅ Confirmed |
| USDCNH   | USD/CNH       | ✅ Confirmed |
| USDSEK   | USD/SEK       | ✅ Confirmed |
| GBPJPY   | GBP/JPY       | ⚡ On-demand |
| EURJPY   | EUR/JPY       | ⚡ On-demand |
| EURGBP   | EUR/GBP       | ⚡ On-demand |
| AUDJPY   | AUD/JPY       | ⚡ On-demand |
| CADJPY   | CAD/JPY       | ⚡ On-demand |
| GBPCAD   | GBP/CAD       | ⚡ On-demand |

### ₿ Crypto (12 pairs)
| Symbol    | Label        | Notes |
|-----------|--------------|-------|
| BTCUSD    | BTC/USD      | Primary |
| ETHUSD    | ETH/USD      | Primary |
| BNBUSDT   | BNB/USDT     | Binance |
| SOLUSDT   | SOL/USDT     | High vol |
| XRPUSDT   | XRP/USDT     | |
| ADAUSDT   | ADA/USDT     | |
| AVAXUSDT  | AVAX/USDT    | |
| DOTUSDT   | DOT/USDT     | |
| LINKUSDT  | LINK/USDT    | |
| LTCUSDT   | LTC/USDT     | |
| MATICUSDT | MATIC/USDT   | |
| TONUSDT   | TON/USDT     | |

### 🥇 Komoditas (8 pairs)
| Symbol | Label        | Notes |
|--------|--------------|-------|
| XAUUSD | Gold         | Most popular |
| XAGUSD | Silver       | |
| USOIL  | WTI Crude    | |
| UKOIL  | Brent Crude  | |
| NATGAS | Natural Gas  | |
| COPPER | Copper       | |
| WHEAT  | Wheat        | |
| CORN   | Corn         | |

### 📈 Indeks (10 pairs)
| Symbol | Label        | Market |
|--------|--------------|--------|
| US30   | Dow Jones    | USA |
| US500  | S&P 500      | USA |
| USTEC  | Nasdaq 100   | USA |
| GER40  | DAX 40       | Germany |
| JPN225 | Nikkei 225   | Japan |
| UK100  | FTSE 100     | UK |
| AUS200 | ASX 200      | Australia |
| FRA40  | CAC 40       | France |
| ESP35  | IBEX 35      | Spain |
| HK50   | Hang Seng    | Hong Kong |

### 🐸 Meme Coins (10 pairs)
| Symbol     | Label       |
|------------|-------------|
| DOGEUSDT   | DOGE        |
| SHIBUSDT   | SHIB        |
| PEPEUSDT   | PEPE        |
| WIFUSDT    | WIF         |
| BONKUSDT   | BONK        |
| FLOKIUSDT  | FLOKI       |
| MOGUSDT    | MOG         |
| BRETTUSDT  | BRETT       |
| POPCATUSDT | POPCAT      |
| MEWUSDT    | MEW         |

### 💻 Saham US (10 pairs)
| Symbol | Label       | Live Redis |
|--------|-------------|------------|
| NVDA   | Nvidia      | ✅ Confirmed |
| MSFT   | Microsoft   | ✅ Confirmed |
| AMD    | AMD         | ✅ Confirmed |
| INTC   | Intel       | ✅ Confirmed |
| AAPL   | Apple       | ⚡ On-demand |
| TSLA   | Tesla       | ⚡ On-demand |
| AMZN   | Amazon      | ⚡ On-demand |
| GOOGL  | Google      | ⚡ On-demand |
| META   | Meta        | ⚡ On-demand |
| COIN   | Coinbase    | ⚡ On-demand |

> **✅ Confirmed** = data OHLCV sudah ada di Redis (MT5 EA aktif mengirim)
> **⚡ On-demand** = pair tersedia di platform, butuh EA add ke Market Watch

---

## 3. PIPELINE DETAIL PER FLOW

### 📊 SIGNAL FLOW (Fast — 3–5 detik)

```
[User tap "📊 Signal"]
         │
         ▼
set_state(flow_type="signal")
         │
         ▼
[Pilih Market Category]
  FOREX / CRYPTO / COMMODITY / INDEX / MEME / STOCK
         │
         ▼
 SKIP pair picker — gunakan FEATURED_PAIR:
   FOREX     → XAUUSD
   CRYPTO    → BTCUSD
   COMMODITY → XAUUSD
   INDEX     → US30
   MEME      → DOGEUSDT
   STOCK     → NVDA
         │
         ▼
[Pilih Style: Scalping / Intraday / Swing / Position]
         │
         ▼
[Konfirmasi: tampil biaya kredit]
         │
         ▼
exec_{signal}_{pair}_{style} callback
         │
         ├─── Cache hit?  YES → kirim langsung, 0 AI call
         │                        edit message → FORMAT SIGNAL
         │
         └─── Cache miss → edit "Menganalisis..."
                    │
                    ▼
             enqueue(JobType.SIGNAL, queue="q:high")
                    │
                    ▼
             SignalWorker dequeue
             (3 workers parallel)
                    │
                    ▼
             bot_api_client.analyze(pair, style, "technical")
                    │
                    ▼
             POST /api/v1/bot/analyze  (gas-web-backend)
                    │
                    ▼
             Deduct credits (plan-based)
             POST /v1/analysis/signal  (gas-strategy-core)
                    │
                    ▼
             5-Layer Engine (lihat section 4)
                    │
                    ▼
             AI Response → normalize → return
                    │
                    ▼
             cache.set_signal(pair, style, result, TTL=30s)
                    │
                    ▼
             format_signal_md(result) → MarkdownV2
                    │
                    ▼
             bot.edit_message(chat_id, msg_id, text)
                    │
                    ▼
         [User sees Premium Signal Card]
```

---

### 🧠 ANALISA FLOW (Medium — 3–7 detik)

```
[User tap "🧠 Analisa"]
         │
set_state(flow_type="analysis")
         │
[Pilih Market Category]
         │
[Pilih Pair dari list] ← BERBEDA dengan Signal (ada pair picker)
         │
[Pilih Style]
         │
[Konfirmasi + biaya]
         │
exec_{analysis}_{pair}_{style}
         │
         ├─── Cache hit → kirim langsung
         │
         └─── enqueue(JobType.ANALYSIS, queue="q:medium")
                    │
              AnalysisWorker (2 workers)
              Juga drain queue q:high jika kosong
                    │
              bot_api_client.analyze(pair, style, "technical")
                    │
              POST /bot/analyze → strategy-core
                    │
              5-Layer Engine
                    │
              AI (model tier by plan)
                    │
              cache 30s → format → edit message
```

---

### 👑 ANALYST FLOW (Full Power — 5–15 detik, NO cache)

```
[User tap "👑 Analyst"]
         │
Plan check: Plus / Premium / Ultimate only
         │
set_state(flow_type="analyst")
         │
[Market → Pair → Style → Konfirmasi]
         │
exec_{analyst}_{pair}_{style}
         │
NO CACHE CHECK (always fresh AI)
         │
enqueue(JobType.ANALYST, queue="q:low")
         │
AnalystWorker (1 worker, serialized)
         │
bot_api_client.analyze(pair, style, "full")
         │
POST /bot/analyze
  feature="full" → strategy-core full power
         │
5-Layer Engine + deeper SMC analysis
         │
AI model ULTRA (Claude Sonnet / Opus)
  → More tokens, deeper reasoning
  → Full multi-TF analysis
  → Complete narrative + psychology notes
         │
NO cache storage
         │
format_signal_md() → edit message
```

---

## 4. 5-LAYER ENGINE (gas-strategy-core)

```
Input: pair, timeframe, style, model_tier
                │
                ▼
┌───────────────────────────────────────────┐
│  LAYER 1: Multi-TF OHLCV Data (Redis)    │
│                                           │
│  Style → TF Matrix:                       │
│  scalping: H1 → M15 → M5 → M1           │
│  intraday: H4 → H1 → M15 → M5           │
│  swing:    D1 → H4 → H1 → M15           │
│                                           │
│  Source: ohlc:{PAIR}:{TF} in Redis       │
│  Pushed by: GAS_StrategyScanner_v5.mq5   │
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│  LAYER 2: Technical Indicators           │
│                                           │
│  RSI (14)        → Overbought/Oversold   │
│  MACD            → Momentum              │
│  Bollinger Bands → Volatility            │
│  ATR (14)        → True Range            │
│  ADX (14)        → Trend Strength        │
│  EMA 20/50/200   → Trend Direction       │
│  Stochastic      → Entry timing          │
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│  LAYER 3: SMC Engine                     │
│                                           │
│  ├── Market Structure (BOS/CHoCH/MSS)    │
│  ├── Order Blocks (Bullish/Bearish OB)   │
│  ├── Fair Value Gap (FVG/Imbalance)      │
│  ├── Liquidity (Equal H/L, BSL/SSL)      │
│  ├── Kill Zones (London/NY/Asian)        │
│  ├── AMD Phase (Accumulation/Manip/Dist) │
│  └── OTE Zone (0.618–0.786 Fib)         │
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│  LAYER 4: DXY Correlation                │
│  (khusus XAU/Forex pairs)                │
│                                           │
│  DXY↑ = XAU SELL signal                  │
│  DXY↓ = XAU BUY signal                   │
│  DXY TF: H1/M15 (scalping)              │
│          H4/H1 (intraday)                │
│          D1/H4 (swing)                   │
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│  LAYER 5: Macro + News Context           │
│                                           │
│  ├── Fear & Greed Index (external API)   │
│  ├── COT Data (Gold / DXY positioning)  │
│  ├── Economic Calendar (upcoming events) │
│  └── Market Macro (interest rates, GDP)  │
└───────────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│  AI ENGINE (ai.analyze_signal_tiered)    │
│                                           │
│  Setup Type Detection:                   │
│  → Reversal / Liquidity Grab / Pullback  │
│  → Breakout / Continuation / Accumulation│
│                                           │
│  AI Prompt = semua layer data di atas    │
│  AI Output = structured JSON signal:     │
│   grade, signal, bias, entry, SL, TP     │
│   probability, rr, summary, session      │
└───────────────────────────────────────────┘
```

---

## 5. AI MODEL TIERS (Plan-gated)

| Tier     | Model                       | Plan         | Temp | Max Token |
|----------|-----------------------------|--------------|------|-----------|
| basic    | deepseek/deepseek-chat      | Essential    | 0.30 | 1000 |
| advanced | google/gemini-flash-1.5     | Plus         | 0.25 | 1400 |
| pro      | anthropic/claude-haiku-4-5  | Premium      | 0.20 | 1600 |
| ultra    | anthropic/claude-sonnet-4-6 | Ultimate     | 0.15 | 1800 |
| agent    | anthropic/claude-opus-4-6   | Ultra        | 0.10 | 2000 |

**Fallback chain:**
```
OpenRouter (primary)
    │ fail
    ▼
Kimi AI / Moonshot (secondary)
    │ fail
    ▼
Static offline response
```

---

## 6. QUEUE & WORKER SYSTEM

```
USER CLICK ──→ enqueue() ──→ Redis List
                              │
                     ┌────────┴────────────────┐
                     │                         │
                  q:high                    q:medium / q:low
                     │                         │
              SignalWorker (×3)         AnalysisWorker (×2)
                     │                 AnalystWorker (×1)
                     └────────┬────────ScannerWorker (×1)
                               │
                        FeedWorker (×1)
                        [interval 300s]
                        Fetches: news + calendar
                        Caches: cache:feed:news
                                cache:feed:calendar
```

### Priority Queue Logic
```
q:high   → SIGNAL flow       (fastest, 3× workers)
q:medium → ANALISA flow      (2× workers, also drain q:high)
q:low    → ANALYST / SCANNER (1× worker each, serialized)

Worker picks job: BRPOP with 5s timeout
If no job in 5s → sleep, retry
```

### Cache Layers
```
cache:signal:{PAIR}:{STYLE}  TTL=30s   → Shared antar user
cache:scanner:{key}          TTL=60s   → Per scan batch
cache:feed:news              TTL=300s  → News ticker
cache:feed:calendar          TTL=300s  → Economic calendar
```

---

## 7. CREDIT SYSTEM

```
Sumber kredit: gas-redis → user:{gas_user_id}:credits

Cost per style:
  scalping  = 2 cr
  intraday  = 3 cr
  swing     = 4 cr
  position  = 5 cr

Free/Trial override = 1 cr (semua style)

Market multiplier (di web-backend):
  forex     = 1.0×
  crypto    = 1.2×
  meme      = 1.5×
  stock     = 1.3×
  poly      = 1.2×

Deduction: WATCH + pipeline (atomic, 3 retry on conflict)
Refund:    jika AI error setelah deduction
```

---

## 8. DATA FLOW MT5 → REDIS

```
MT5 Platform (user's PC / VPS)
    │
    │  GAS_StrategyScanner_v5.mq5 (EA)
    │  Runs on chart, scans all Market Watch symbols
    │
    ├── Every tick:    POST /tick/{symbol}    → gas-mt5-websocket
    ├── Every bar:     POST /batch-ohlc       → gas-mt5-websocket
    ├── Every scan:    POST /scanner-snapshot → gas-mt5-websocket
    └── Every 30s:     POST /account/heartbeat → gas-mt5-websocket
                              │
                              ▼
                   gas-mt5-websocket (port 8110)
                              │
                    Stores: ohlc:{SYMBOL}:{TF} → Redis
                    Stores: tick:{SYMBOL}       → Redis
                    Stores: account:{user}      → Redis

Live symbols confirmed in Redis (2026-03-28):
  Forex:    XAUUSD, EURUSD, GBPUSD, USDJPY, AUDUSD,
            USDCAD, NZDUSD, USDCHF, USDCNH, USDSEK
  Stocks:   NVDA, MSFT, AMD, INTC
  DXY:      DXY (correlation data)

To add more pairs: tambahkan symbol ke MT5 Market Watch
EA akan otomatis kirim data ke webhook.
```

---

## 9. AUTHENTICATION FLOW

```
User Telegram Account
    │
    ├── /link → bot generate code (8 char)
    │            stored: tg:link:{code} = tg_user_id  TTL=15min
    │
    ▼
User login ke gasstrategyai.xyz
    │
    ├── POST /telegram/link-v2 (authenticated)
    │   body: { code: "..." }
    │   Stores:
    │     tg:bind:{tg_user_id}  = gas_user_id  (permanent)
    │     tg:gas:{gas_user_id}  = tg_user_id   (reverse index)
    │
    ▼
Bot access check (every request):
    │
    ├── r.get("tg:bind:{tg_user_id}") → gas_user_id
    ├── r.get("user:{gas_user_id}:plan") → plan tier
    └── r.get("user:{gas_user_id}:credits") → balance
```

---

## 10. ERROR HANDLING & FALLBACKS

| Error | Handling |
|-------|----------|
| Cache miss | Enqueue AI job |
| Redis down | Log warning, try proceed |
| strategy-core timeout | Kimi AI fallback |
| Kimi AI fail | Static offline message |
| No OHLC data | HTTP 503, bot shows "pair tidak tersedia" |
| Credits < cost | Show "💳 Credits Habis" error |
| Idempotency hit | Show "⏳ Tunggu sebentar" |
| Plan not allowed | Show "🔒 Fitur Terkunci" |
| MT5 not connected | strategy-core returns empty data |

---

## 11. ENDPOINT MAP (Lengkap)

### gas-telegram-bot (internal)
- No HTTP server — asyncio polling only

### gas-web-backend (port 8005)
```
POST /bot/analyze              ← dipanggil bot workers
POST /api/v1/bot/analyze       ← alias
POST /telegram/link            ← user link via dashboard
POST /telegram/link-v2         ← dengan reverse index
GET  /telegram/me              ← cek link status
DELETE /telegram/unlink        ← unlink akun
GET  /api/v1/billing/credits   ← saldo kredit
POST /api/v1/billing/deduct    ← potong kredit
GET  /api/v1/health            ← healthcheck
```

### gas-strategy-core (port 7003)
```
POST /v1/analysis/signal       ← main AI signal endpoint
POST /v1/analysis/sentiment    ← sentimen analysis
POST /v1/analysis/fundamental  ← fundamental analysis
GET  /v1/symbols               ← list symbols with data
GET  /health                   ← healthcheck
```

### gas-mt5-websocket (port 8110)
```
POST /tick/{symbol}            ← single tick
POST /batch-tick               ← batch tick snapshot (EA Scanner)
POST /batch-ohlc               ← batch OHLCV (EA Scanner)
POST /scanner-snapshot         ← full scanner snapshot
POST /account/heartbeat        ← MT5 account status
GET  /ohlc/{symbol}/{tf}       ← get cached OHLCV
GET  /tick/{symbol}            ← get latest tick
GET  /health                   ← healthcheck
```

---

## 12. KNOWN ISSUES & TODO

### Issues Aktif
1. **Pairs tanpa live data** — Cross pairs (GBPJPY, EURJPY) dan Crypto altcoin belum ada
   di Redis karena belum di-add ke MT5 Market Watch. Add ke Market Watch → EA akan kirim.

2. **Meme coins** — DOGE/SHIB/PEPE tidak ada di MT5 broker biasa.
   Perlu integrasi gas-binance-service untuk Binance CCXT data.

3. **Stocks** — AAPL/TSLA/AMZN belum ada di Redis. Tambahkan ke Market Watch
   (butuh broker yang menyediakan CFD saham US).

4. **Polymarket** — Saat ini hanya static display. Perlu integrasi API
   `https://clob.polymarket.com/` untuk data real-time.

5. **Scanner UI** — Scanner result belum memiliki pair selector di bot.
   Saat ini pakai DEFAULT_SCAN_PAIRS saja.

### TODO Next
- [ ] Gas-binance-service integration untuk Crypto/Meme real-time data
- [ ] Polymarket API fetch di FeedWorker
- [ ] Pair selector untuk Scanner flow
- [ ] /analyst command plan gate (saat ini semua plan bisa akses)
- [ ] Notification system untuk alert price
- [ ] Push notif otomatis saat ada signal SS/S grade

---

## 13. FILE STRUCTURE GAS-TELEGRAM-BOT

```
gas-telegram-bot/
├── src/
│   ├── main.py                    ← Entry point, asyncio gather, set_my_commands
│   ├── config.py                  ← Settings, BOT_ALLOWED_PLANS
│   ├── bot/
│   │   └── handlers.py            ← ALL handlers (text + callback + commands)
│   ├── keyboards/
│   │   ├── market.py              ← Market categories + pair lists
│   │   ├── style.py               ← Style selector + confirm keyboard
│   │   └── main_menu.py           ← ReplyKeyboard + all section inline keyboards
│   ├── workers/
│   │   ├── base.py                ← BaseWorker ABC
│   │   ├── signal_worker.py       ← Fast signal (q:high, cache)
│   │   ├── analysis_worker.py     ← Analysis (q:medium)
│   │   ├── analyst_worker.py      ← Full AI (q:low, no cache)
│   │   ├── scanner_worker.py      ← Multi-pair scan (q:low)
│   │   ├── feed_worker.py         ← News+Calendar cache (interval)
│   │   └── runner.py              ← Launches all 8 workers
│   ├── services/
│   │   ├── bot_api_client.py      ← HTTP client → gas-web-backend
│   │   ├── auth_service.py        ← Redis auth (plan, credits, xp)
│   │   ├── cache.py               ← Signal/Scanner/Feed cache
│   │   ├── credit.py              ← Credit deduction (atomic)
│   │   ├── queue.py               ← Redis job queue (BRPOP/LPUSH)
│   │   └── redis_client.py        ← Shared Redis client
│   └── utils/
│       ├── formatter.py           ← Premium MarkdownV2 formatter
│       ├── session.py             ← Per-user flow state (Redis TTL 10m)
│       └── logger.py              ← Structlog
```

---

*Report generated by Claude Code analysis of live codebase — 2026-03-28*
