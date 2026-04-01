import yfinance as yf
import requests
import redis
import json
import time
import os
import random
from typing import List, Dict, Any, Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    REDIS_OK = True
except:
    REDIS_OK = False

# ── Custom session to avoid Yahoo Finance rate-limit ──────────────────────────
_UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": random.choice(_UA_LIST),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://finance.yahoo.com/",
        "Origin": "https://finance.yahoo.com",
    })
    return s

# ── Full IDX stock list (blue chip + mid cap + recent IPO) ────────────────────
IDX_SYMBOLS = [
    # Index
    "^JKSE",
    # ── Perbankan ──────────────────────────────────────────────────────────────
    "BBCA","BBRI","BMRI","BBNI","BRIS","NISP","PNBN","BBTN","BJTM","BJBR",
    "MAYA","AGRO","ARTO","BBYB","BBHI","BNII","BNGA","MCOR",
    # ── Telekomunikasi ────────────────────────────────────────────────────────
    "TLKM","ISAT","EXCL","TBIG","TOWR","MTEL","LINK","FREN","WIFI",
    # ── Teknologi & Digital ───────────────────────────────────────────────────
    "GOTO","EMTK","BUKA","DMMX","LCKM","LIFE",
    # ── Energi & EBT ─────────────────────────────────────────────────────────
    "BREN","PGAS","ESSA","ELSA","MEDC","ENRG","PGEO","KEEN","SULI",
    # ── Batubara ─────────────────────────────────────────────────────────────
    "ADRO","PTBA","ITMG","HRUM","BUMI","KKGI","DOID","BYAN","CUAN",
    # ── Tambang & Mineral ────────────────────────────────────────────────────
    "INCO","ANTM","TINS","MDKA","AMMN","NCKL","BRMS","NICL","DKFT","PSAB",
    # ── Minyak & Gas ─────────────────────────────────────────────────────────
    "AKRA","PELE","RUIS",
    # ── Konsumer ─────────────────────────────────────────────────────────────
    "UNVR","ICBP","INDF","HMSP","GGRM","MYOR","DLTA","ULTJ","SIDO",
    "CPIN","JPFA","MAIN","CMRY","GOOD","BOBA","SOHO",
    # ── Farmasi & Kesehatan ───────────────────────────────────────────────────
    "KLBF","MIKA","HEAL","SCMA","PRDA","TSPC","KAEF","INAF","PYFA",
    # ── Industri & Material ───────────────────────────────────────────────────
    "ASII","SMGR","INTP","INKP","TKIM","BRPT","TPIA","UNIC","AMFG",
    "JSMR","WIKA","PTPP","ADHI","WSKT","NRCA","TOTL",
    # ── Properti ─────────────────────────────────────────────────────────────
    "BSDE","PWON","LPKR","SMRA","CTRA","DMAS","PANI","SMDM","KIJA",
    # ── Retail & Consumer Discretionary ──────────────────────────────────────
    "ACES","MAPI","ERAA","LPPF","MPPA","CSAP","RALS",
    # ── Media & Entertainment ────────────────────────────────────────────────
    "SRTG","MNCN","SCMA",
    # ── Agrikultur ────────────────────────────────────────────────────────────
    "AALI","SGRO","LSIP","TAPG","DSNG","SSMS",
    # ── Logistik & Transportasi ───────────────────────────────────────────────
    "BIRD","GIAA","SMDR","TMAS","MPXL",
]

IHSG_SYMBOL = "^JKSE"

def to_jk(symbol: str) -> str:
    s = symbol.upper().strip()
    if s.startswith("^") or s.endswith(".JK"):
        return s
    return f"{s}.JK"

def cache_get(key: str) -> Optional[Any]:
    if not REDIS_OK:
        return None
    try:
        v = r.get(key)
        return json.loads(v) if v else None
    except:
        return None

def cache_set(key: str, value: Any, ttl: int = 60):
    if not REDIS_OK:
        return
    try:
        r.set(key, json.dumps(value), ex=ttl)
    except:
        pass

def _fetch_ticker(jk: str, retries: int = 2) -> Optional[Any]:
    """Create yfinance Ticker with retry + custom session."""
    for attempt in range(retries):
        try:
            t = yf.Ticker(jk, session=_make_session())
            return t
        except Exception:
            if attempt < retries - 1:
                time.sleep(0.3 * (attempt + 1))
    return None

def get_quote(symbol: str) -> Dict[str, Any]:
    jk = to_jk(symbol)
    cache_key = f"idx:quote:{jk}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    try:
        t = _fetch_ticker(jk)
        if not t:
            return {"symbol": symbol.upper(), "error": "fetch_failed"}
        fi = t.fast_info
        price = fi.last_price
        prev = fi.previous_close
        result = {
            "symbol": symbol.upper(),
            "jk_symbol": jk,
            "price": price,
            "prev_close": prev,
            "open": fi.open,
            "day_high": fi.day_high,
            "day_low": fi.day_low,
            "volume": fi.last_volume,
            "market_cap": fi.market_cap,
            "change": round(price - prev, 2) if price and prev else 0,
            "change_pct": round(((price - prev) / prev * 100), 2) if price and prev else 0,
            "timestamp": int(time.time()),
        }
        cache_set(cache_key, result, ttl=60)
        return result
    except Exception as e:
        stale = cache_get(f"idx:quote:stale:{jk}")
        if stale:
            return stale
        return {"symbol": symbol.upper(), "error": str(e)}

def get_ohlcv(symbol: str, interval: str = "1d", period: str = "3mo") -> List[Dict]:
    jk = to_jk(symbol)
    cache_key = f"idx:ohlcv:{jk}:{interval}:{period}"
    ttl_map = {"1m": 60, "5m": 120, "15m": 180, "1h": 600, "1d": 3600, "1wk": 7200}
    ttl = ttl_map.get(interval, 300)
    cached = cache_get(cache_key)
    if cached:
        return cached
    try:
        t = _fetch_ticker(jk)
        if not t:
            return []
        df = t.history(period=period, interval=interval)
        if df.empty:
            return []
        candles = []
        for ts, row in df.iterrows():
            candles.append({
                "time": int(ts.timestamp()),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })
        cache_set(cache_key, candles, ttl=ttl)
        return candles
    except Exception:
        return []

def get_multi_quote(symbols: List[str]) -> List[Dict]:
    """Batch fetch — splits into chunks to avoid rate limits."""
    results = []
    chunk_size = 10
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i + chunk_size]
        jk_syms = " ".join([to_jk(s) for s in chunk])
        try:
            sess = _make_session()
            tickers = yf.Tickers(jk_syms, session=sess)
            for sym in chunk:
                jk = to_jk(sym)
                cache_key = f"idx:quote:{jk}"
                cached = cache_get(cache_key)
                if cached:
                    results.append(cached)
                    continue
                try:
                    fi = tickers.tickers[jk].fast_info
                    price = fi.last_price
                    prev = fi.previous_close
                    rec = {
                        "symbol": sym.upper(),
                        "price": price,
                        "prev_close": prev,
                        "day_high": fi.day_high,
                        "day_low": fi.day_low,
                        "volume": fi.last_volume,
                        "change_pct": round(((price - prev) / prev * 100), 2) if price and prev else 0,
                        "change": round(price - prev, 2) if price and prev else 0,
                    }
                    cache_set(cache_key, rec, ttl=60)
                    results.append(rec)
                except:
                    results.append({"symbol": sym.upper(), "price": None, "error": "fetch_failed"})
        except Exception as e:
            for sym in chunk:
                results.append({"symbol": sym.upper(), "error": str(e)})
        if i + chunk_size < len(symbols):
            time.sleep(0.2)
    return results

def get_ihsg() -> Dict:
    cache_key = "idx:ihsg"
    cached = cache_get(cache_key)
    if cached:
        return cached
    try:
        t = _fetch_ticker(IHSG_SYMBOL)
        if not t:
            return {"symbol": "IHSG", "error": "fetch_failed"}
        fi = t.fast_info
        price = fi.last_price
        prev = fi.previous_close
        result = {
            "symbol": "IHSG",
            "price": price,
            "prev_close": prev,
            "open": fi.open,
            "day_high": fi.day_high,
            "day_low": fi.day_low,
            "volume": fi.last_volume,
            "change": round(price - prev, 2) if price and prev else 0,
            "change_pct": round(((price - prev) / prev * 100), 2) if price and prev else 0,
            "timestamp": int(time.time()),
        }
        cache_set(cache_key, result, ttl=120)
        # also save stale copy
        cache_set("idx:ihsg:stale", result, ttl=86400)
        return result
    except Exception as e:
        stale = cache_get("idx:ihsg:stale")
        if stale:
            return {**stale, "stale": True}
        return {"symbol": "IHSG", "error": str(e)}

def get_company_info(symbol: str) -> Dict:
    jk = to_jk(symbol)
    cache_key = f"idx:info:{jk}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    try:
        t = _fetch_ticker(jk)
        if not t:
            return {"symbol": symbol.upper(), "error": "fetch_failed"}
        info = t.info
        result = {
            "symbol": symbol.upper(),
            "name": info.get("shortName", ""),
            "long_name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
            "employees": info.get("fullTimeEmployees"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "debt_equity": info.get("debtToEquity"),
            "description": (info.get("longBusinessSummary", "") or "")[:400],
        }
        cache_set(cache_key, result, ttl=7200)
        return result
    except Exception as e:
        return {"symbol": symbol.upper(), "error": str(e)}
