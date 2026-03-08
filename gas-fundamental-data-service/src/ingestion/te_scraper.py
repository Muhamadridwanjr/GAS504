"""
Trading Economics scraper using the tedata open-source library.
https://github.com/HelloThereMatey/tedata

Runs as a scheduled background job (sync via ProcessPoolExecutor).
Results are stored in the fundamental_data PostgreSQL table.
"""
from __future__ import annotations
import time
import datetime
from src.lib.logger import get_logger

logger = get_logger(__name__)

# ─── INDICATOR REGISTRY ─────────────────────────────────────────────────────
# Maps indicator keys → Trading Economics URLs + metadata.
# tedata CAN scrape the "static/economic" chart type (monthly/quarterly series).
# High-frequency/real-time charts (VIX, DXY price, spot oil) are NOT scrapable.

TE_INDICATORS: dict[str, dict] = {
    # ── US MACRO ────────────────────────────────────────────────────────
    "US_CPI": {
        "url": "https://tradingeconomics.com/united-states/inflation-cpi",
        "label": "CPI (US, YoY)",
        "region": "USA",
        "assets": ["XAUUSD", "EURUSD", "USDJPY", "DXY", "BTCUSD"],
        "tier": 1,
        "impact": "VERY_HIGH",
        "unit": "%",
        "period": "Monthly",
        "symbol": "US",
    },
    "US_CORE_CPI": {
        "url": "https://tradingeconomics.com/united-states/core-inflation-rate",
        "label": "Core CPI (US)",
        "region": "USA",
        "assets": ["XAUUSD", "DXY"],
        "tier": 1,
        "impact": "VERY_HIGH",
        "unit": "%",
        "period": "Monthly",
        "symbol": "US",
    },
    "US_NFP": {
        "url": "https://tradingeconomics.com/united-states/non-farm-payrolls",
        "label": "Non-Farm Payrolls",
        "region": "USA",
        "assets": ["XAUUSD", "EURUSD", "USDJPY", "DXY"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "K",
        "period": "Monthly",
        "symbol": "US",
    },
    "US_FED_RATE": {
        "url": "https://tradingeconomics.com/united-states/interest-rate",
        "label": "Fed Funds Rate",
        "region": "USA",
        "assets": ["XAUUSD", "EURUSD", "USDJPY", "GBPUSD", "DXY", "BTCUSD"],
        "tier": 1,
        "impact": "VERY_HIGH",
        "unit": "%",
        "period": "Quarterly",
        "symbol": "US",
    },
    "US_10Y_YIELD": {
        "url": "https://tradingeconomics.com/united-states/government-bond-yield",
        "label": "US 10Y Treasury Yield",
        "region": "USA",
        "assets": ["XAUUSD", "USDJPY"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "%",
        "period": "Real-time",
        "symbol": "US",
    },
    "EIA_CRUDE": {
        "url": "https://tradingeconomics.com/united-states/crude-oil-stocks-change",
        "label": "EIA Crude Oil Inventories",
        "region": "USA",
        "assets": ["XTIUSD", "XBRUSD"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "MBbl",
        "period": "Weekly",
        "symbol": "OIL",
    },
    "US_MFG_PMI": {
        "url": "https://tradingeconomics.com/united-states/manufacturing-pmi",
        "label": "US Manufacturing PMI",
        "region": "USA",
        "assets": ["XTIUSD", "XAGUSD", "EURUSD", "SPX"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "pts",
        "period": "Monthly",
        "symbol": "US",
    },
    "US_INDUSTRIAL_PROD": {
        "url": "https://tradingeconomics.com/united-states/industrial-production",
        "label": "US Industrial Production",
        "region": "USA",
        "assets": ["XAGUSD"],
        "tier": 2,
        "impact": "MEDIUM",
        "unit": "%",
        "period": "Monthly",
        "symbol": "US",
    },
    "US_GDP": {
        "url": "https://tradingeconomics.com/united-states/gdp-growth",
        "label": "US GDP Growth (QoQ)",
        "region": "USA",
        "assets": ["SPX", "NDQ", "DJI", "DXY"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "%",
        "period": "Quarterly",
        "symbol": "US",
    },
    "US_UNEMPLOYMENT": {
        "url": "https://tradingeconomics.com/united-states/unemployment-rate",
        "label": "US Unemployment Rate",
        "region": "USA",
        "assets": ["XAUUSD", "EURUSD", "DXY"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "%",
        "period": "Monthly",
        "symbol": "US",
    },
    # ── EUROZONE ─────────────────────────────────────────────────────────
    "EU_CPI": {
        "url": "https://tradingeconomics.com/euro-area/inflation-cpi",
        "label": "Eurozone CPI (YoY)",
        "region": "Eurozone",
        "assets": ["EURUSD"],
        "tier": 1,
        "impact": "VERY_HIGH",
        "unit": "%",
        "period": "Monthly",
        "symbol": "EU",
    },
    "ECB_RATE": {
        "url": "https://tradingeconomics.com/euro-area/interest-rate",
        "label": "ECB Interest Rate",
        "region": "Eurozone",
        "assets": ["EURUSD"],
        "tier": 1,
        "impact": "VERY_HIGH",
        "unit": "%",
        "period": "Quarterly",
        "symbol": "EU",
    },
    "EU_GDP": {
        "url": "https://tradingeconomics.com/euro-area/gdp-growth",
        "label": "Eurozone GDP Growth",
        "region": "Eurozone",
        "assets": ["EURUSD"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "%",
        "period": "Quarterly",
        "symbol": "EU",
    },
    "EU_MFG_PMI": {
        "url": "https://tradingeconomics.com/euro-area/manufacturing-pmi",
        "label": "Eurozone Manufacturing PMI",
        "region": "Eurozone",
        "assets": ["EURUSD", "XTIUSD"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "pts",
        "period": "Monthly",
        "symbol": "EU",
    },
    # ── JAPAN ─────────────────────────────────────────────────────────────
    "JP_BOJ_RATE": {
        "url": "https://tradingeconomics.com/japan/interest-rate",
        "label": "BOJ Policy Rate",
        "region": "Japan",
        "assets": ["USDJPY"],
        "tier": 1,
        "impact": "VERY_HIGH",
        "unit": "%",
        "period": "Quarterly",
        "symbol": "JP",
    },
    "JP_CPI": {
        "url": "https://tradingeconomics.com/japan/inflation-cpi",
        "label": "Japan CPI (YoY)",
        "region": "Japan",
        "assets": ["USDJPY"],
        "tier": 2,
        "impact": "MEDIUM",
        "unit": "%",
        "period": "Monthly",
        "symbol": "JP",
    },
    # ── UK ────────────────────────────────────────────────────────────────
    "UK_CPI": {
        "url": "https://tradingeconomics.com/united-kingdom/inflation-cpi",
        "label": "UK CPI (YoY)",
        "region": "UK",
        "assets": ["GBPUSD"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "%",
        "period": "Monthly",
        "symbol": "UK",
    },
    "BOE_RATE": {
        "url": "https://tradingeconomics.com/united-kingdom/interest-rate",
        "label": "BOE Interest Rate",
        "region": "UK",
        "assets": ["GBPUSD"],
        "tier": 1,
        "impact": "VERY_HIGH",
        "unit": "%",
        "period": "Quarterly",
        "symbol": "UK",
    },
    "UK_GDP": {
        "url": "https://tradingeconomics.com/united-kingdom/gdp-growth",
        "label": "UK GDP Growth",
        "region": "UK",
        "assets": ["GBPUSD"],
        "tier": 2,
        "impact": "HIGH",
        "unit": "%",
        "period": "Quarterly",
        "symbol": "UK",
    },
    # ── GLOBAL ─────────────────────────────────────────────────────────────
    "GLOBAL_MFG_PMI": {
        "url": "https://tradingeconomics.com/world/manufacturing-pmi",
        "label": "Global Manufacturing PMI",
        "region": "Global",
        "assets": ["XTIUSD", "XAGUSD", "SPX"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "pts",
        "period": "Monthly",
        "symbol": "GLOBAL",
    },
    "CHINA_MFG_PMI": {
        "url": "https://tradingeconomics.com/china/manufacturing-pmi",
        "label": "China Manufacturing PMI",
        "region": "China",
        "assets": ["XTIUSD", "XAGUSD"],
        "tier": 1,
        "impact": "HIGH",
        "unit": "pts",
        "period": "Monthly",
        "symbol": "CN",
    },
}


def _generate_ai_note(key: str, actual: float | None, previous: float | None, unit: str) -> str:
    """Generate a brief AI note based on the actual vs previous comparison."""
    meta = TE_INDICATORS.get(key, {})
    label = meta.get("label", key)
    assets = ", ".join(meta.get("assets", [])[:3])

    if actual is None or previous is None:
        return f"Data untuk {label} sedang diperbarui."

    change = actual - previous
    direction = "naik" if change > 0 else "turun"
    pct = abs(change)
    impact = meta.get("impact", "HIGH")

    if key in ("US_CPI", "US_CORE_CPI", "EU_CPI", "UK_CPI", "JP_CPI"):
        if change > 0:
            return (f"CPI {direction} {pct:.2f}{unit}. Inflasi meningkat → hawkish pressure "
                    f"pada bank sentral. Bearish untuk {assets} jika Fed/ECB/BOE respons hawkish.")
        else:
            return (f"CPI {direction} {pct:.2f}{unit}. Inflasi mereda → dovish signal. "
                    f"Bullish untuk {assets} jika bank sentral longgarkan kebijakan.")

    if key in ("US_FED_RATE", "ECB_RATE", "BOE_RATE", "JP_BOJ_RATE"):
        if change > 0:
            return (f"Suku bunga naik {pct:.2f}%. Kebijakan hawkish → penguatan DXY/mata uang terkait, "
                    f"tekanan pada {assets}.")
        elif change < 0:
            return (f"Suku bunga dipangkas {pct:.2f}%. Kebijakan dovish → melemahnya mata uang, "
                    f"bullish untuk {assets}.")
        else:
            return f"Suku bunga ditahan. Pasar waspadai forward guidance untuk arah {assets}."

    if key == "US_NFP":
        if change > 0:
            return (f"NFP lebih kuat +{pct:.0f}K. Pasar tenaga kerja solid → hawkish Fed, "
                    f"bearish untuk XAUUSD, bullish DXY.")
        else:
            return (f"NFP melemah -{pct:.0f}K. Kekhawatiran resesi meningkat → "
                    f"safe haven demand, bullish XAUUSD.")

    if key in ("US_MFG_PMI", "EU_MFG_PMI", "GLOBAL_MFG_PMI", "CHINA_MFG_PMI"):
        zone = "ekspansi" if actual >= 50 else "kontraksi"
        return (f"PMI {actual:.1f}pts ({zone}). "
                f"{'Aktivitas manufaktur menguat, bullish untuk' if actual >= 50 else 'Permintaan melemah, bearish untuk'} "
                f"{assets}.")

    if key == "EIA_CRUDE":
        if change < 0:
            return f"Stok minyak turun {abs(pct):.1f}MBbl. Suplai menurun → bullish WTI/Brent."
        else:
            return f"Stok minyak naik {pct:.1f}MBbl. Suplai berlebih → bearish WTI/Brent."

    return (f"{label} {direction} ke {actual:.2f}{unit} dari {previous:.2f}{unit}. "
            f"Pantau dampak pada {assets}.")


def scrape_indicator_sync(key: str) -> dict | None:
    """
    Synchronous scrape for a single indicator using tedata.
    Returns dict with: key, actual, previous, history (list of {date, value}), unit, ai_notes
    Must be called in a thread/process executor (blocking Selenium call).
    """
    meta = TE_INDICATORS.get(key)
    if not meta:
        logger.warning("Unknown indicator key: %s", key)
        return None

    try:
        import os
        os.environ["TEDATA_DISABLE_LOGGING"] = "true"
        import tedata as ted  # type: ignore

        logger.info("Scraping %s from %s", key, meta["url"])
        scraped = ted.scrape_chart(url=meta["url"], use_existing_driver=False)

        if scraped is None or not hasattr(scraped, 'series') or scraped.series is None or scraped.series.empty:
            logger.warning("No data returned for %s", key)
            return None

        series = scraped.series.dropna()
        if len(series) < 2:
            logger.warning("Insufficient data points for %s", key)
            return None

        # Build history list (last 24 data points for sparkline)
        history = []
        for dt, val in series.tail(24).items():
            if hasattr(dt, "strftime"):
                date_str = dt.strftime("%Y-%m-%d")
            else:
                date_str = str(dt)
            history.append({"date": date_str, "value": float(val)})

        actual = float(series.iloc[-1])
        previous = float(series.iloc[-2])
        unit = meta.get("unit", "")
        ai_notes = _generate_ai_note(key, actual, previous, unit)

        # Build time-series records for DB storage (timestamps in seconds)
        db_records = []
        for dt, val in series.items():
            if hasattr(dt, "timestamp"):
                ts = int(dt.timestamp())
            else:
                try:
                    ts = int(datetime.datetime.fromisoformat(str(dt)).timestamp())
                except Exception:
                    continue
            db_records.append({"time": ts, "value": float(val), "unit": unit})

        return {
            "key": key,
            "label": meta["label"],
            "region": meta["region"],
            "assets": meta["assets"],
            "tier": meta["tier"],
            "impact": meta["impact"],
            "unit": unit,
            "period": meta["period"],
            "actual": actual,
            "previous": previous,
            "ai_notes": ai_notes,
            "history": history,
            "db_records": db_records,
            "scraped_at": datetime.datetime.utcnow().isoformat(),
        }

    except ImportError:
        logger.error("tedata not installed — pip install tedata")
        return None
    except Exception as e:
        logger.error("Error scraping %s: %s", key, e)
        return None


def scrape_all_sync(keys: list[str] | None = None) -> list[dict]:
    """Scrape all (or specified) indicators synchronously. Call from executor."""
    targets = keys or list(TE_INDICATORS.keys())
    results = []
    for key in targets:
        result = scrape_indicator_sync(key)
        if result:
            results.append(result)
        time.sleep(3)  # Polite delay between requests
    return results
