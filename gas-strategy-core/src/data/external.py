import httpx
import json
from typing import Optional

async def fetch_fear_greed() -> dict:
    """Fetch Fear & Greed Index from alternative.me (free, no auth)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://api.alternative.me/fng/?limit=1")
            r.raise_for_status()
            data = r.json()
            fg = data["data"][0]
            value = int(fg["value"])
            label = fg["value_classification"]
            return {
                "index": value,
                "label": label.upper(),
                "timestamp": fg.get("timestamp", ""),
            }
    except Exception as e:
        return {"index": None, "label": "UNAVAILABLE", "error": str(e)}


async def fetch_cot_gold() -> dict:
    """Fetch CFTC COT Gold data — tries multiple endpoints with fallback."""
    # Try the CFTC Socrata-based API (newer endpoint)
    endpoints = [
        # Newer CFTC public API (Socrata)
        "https://publicreporting.cftc.gov/resource/jun7-2rmb.json?$limit=2&$order=report_date_as_yyyy_mm_dd+DESC&$where=market_and_exchange_names+like+'%25GOLD%25'",
        # Legacy endpoint
        "https://publicreporting.cftc.gov/api/odata/v1/FinComData?$top=2&$filter=contains(Market_and_Exchange_Names,'GOLD')&$orderby=Report_Date_as_YYYY_MM_DD desc",
    ]
    for url in endpoints:
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    data = r.json()
                    # Socrata format: list directly
                    rows = data if isinstance(data, list) else data.get("value", [])
                    if not rows:
                        continue
                    latest = rows[0]
                    # Normalize key names (Socrata uses lowercase)
                    nc_long  = int(latest.get("noncomm_positions_long_all",  latest.get("NonComm_Positions_Long_All",  0)) or 0)
                    nc_short = int(latest.get("noncomm_positions_short_all", latest.get("NonComm_Positions_Short_All", 0)) or 0)
                    comm_long  = int(latest.get("comm_positions_long_all",  latest.get("Comm_Positions_Long_All",  0)) or 0)
                    comm_short = int(latest.get("comm_positions_short_all", latest.get("Comm_Positions_Short_All", 0)) or 0)
                    chg_long   = int(latest.get("change_in_noncomm_long_all",  latest.get("Change_in_NonComm_Long_All",  0)) or 0)
                    chg_short  = int(latest.get("change_in_noncomm_short_all", latest.get("Change_in_NonComm_Short_All", 0)) or 0)
                    date_key = latest.get("report_date_as_yyyy_mm_dd", latest.get("Report_Date_as_YYYY_MM_DD", ""))
                    nc_net   = nc_long - nc_short
                    comm_net = comm_long - comm_short
                    return {
                        "report_date": str(date_key)[:10],
                        "non_commercial": {
                            "long":   nc_long, "short": nc_short, "net": nc_net,
                            "bias":   "NET LONG" if nc_net > 0 else "NET SHORT",
                            "change_long": chg_long, "change_short": chg_short,
                        },
                        "commercials": {
                            "long":  comm_long, "short": comm_short, "net": comm_net,
                            "bias":  "NET LONG" if comm_net > 0 else "NET SHORT",
                        },
                    }
        except Exception:
            continue
    return {"status": "unavailable", "note": "CFTC COT data temporarily unavailable"}


async def fetch_cot_dxy() -> dict:
    """Fetch CFTC COT data for US Dollar Index."""
    endpoints = [
        "https://publicreporting.cftc.gov/resource/jun7-2rmb.json?$limit=1&$order=report_date_as_yyyy_mm_dd+DESC&$where=market_and_exchange_names+like+'%25DOLLAR+INDEX%25'",
        "https://publicreporting.cftc.gov/api/odata/v1/FinComData?$top=1&$filter=contains(Market_and_Exchange_Names,'U.S. DOLLAR INDEX')&$orderby=Report_Date_as_YYYY_MM_DD desc",
    ]
    for url in endpoints:
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    data = r.json()
                    rows = data if isinstance(data, list) else data.get("value", [])
                    if not rows:
                        continue
                    latest = rows[0]
                    nc_long  = int(latest.get("noncomm_positions_long_all",  latest.get("NonComm_Positions_Long_All",  0)) or 0)
                    nc_short = int(latest.get("noncomm_positions_short_all", latest.get("NonComm_Positions_Short_All", 0)) or 0)
                    nc_net   = nc_long - nc_short
                    date_key = latest.get("report_date_as_yyyy_mm_dd", latest.get("Report_Date_as_YYYY_MM_DD", ""))
                    return {
                        "report_date": str(date_key)[:10],
                        "non_commercial_net": nc_net,
                        "bias": "NET LONG USD" if nc_net > 0 else "NET SHORT USD",
                    }
        except Exception:
            continue
    return {"status": "unavailable", "note": "CFTC DXY data temporarily unavailable"}
