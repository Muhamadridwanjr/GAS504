"""Dexscreener API client — fetch trending tokens and token data."""
import httpx
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger("dexscreener")

DEXSCREENER_BASE = "https://api.dexscreener.com"

# Supported chains
SUPPORTED_CHAINS = {
    "solana":   {"label": "Solana",   "color": "#9945ff"},
    "ethereum": {"label": "Ethereum", "color": "#627eea"},
    "base":     {"label": "Base",     "color": "#0052ff"},
    "bsc":      {"label": "BSC",      "color": "#f0b90b"},
    "arbitrum": {"label": "Arbitrum", "color": "#28a0f0"},
}

def _safe_float(val, default=0.0) -> float:
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default

def _safe_int(val, default=0) -> int:
    try:
        return int(val) if val is not None else default
    except (TypeError, ValueError):
        return default

def _parse_pair(pair: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse a Dexscreener pair object into our token schema."""
    try:
        base = pair.get("baseToken", {})
        symbol = base.get("symbol", "UNKNOWN")
        name = base.get("name", symbol)
        address = base.get("address", "")
        chain_id = pair.get("chainId", "ethereum").lower()

        if chain_id not in SUPPORTED_CHAINS:
            return None

        price_usd = _safe_float(pair.get("priceUsd"))
        price_native = _safe_float(pair.get("priceNative"))

        # Price changes
        pc = pair.get("priceChange", {})
        pc5m  = _safe_float(pc.get("m5"))
        pc1h  = _safe_float(pc.get("h1"))
        pc6h  = _safe_float(pc.get("h6"))
        pc24h = _safe_float(pc.get("h24"))

        # Volume
        vol = pair.get("volume", {})
        vol_24h = _safe_float(vol.get("h24"))
        vol_1h  = _safe_float(vol.get("h1"))

        # Liquidity
        liq = pair.get("liquidity", {})
        liq_usd = _safe_float(liq.get("usd"))

        # Market cap / FDV
        mcap = _safe_float(pair.get("marketCap")) or None
        fdv  = _safe_float(pair.get("fdv")) or None

        # Tx counts
        txns = pair.get("txns", {})
        txns_1h = txns.get("h1", {})
        buys_1h  = _safe_int(txns_1h.get("buys"))
        sells_1h = _safe_int(txns_1h.get("sells"))
        total_tx = buys_1h + sells_1h or 1
        buy_pressure = round(buys_1h / total_tx, 4)

        # Age
        created_at = pair.get("pairCreatedAt")
        if created_at:
            age_ms = datetime.now(timezone.utc).timestamp() * 1000 - int(created_at)
            age_minutes = max(0, age_ms / 60000)
        else:
            age_minutes = 9999  # unknown age

        pair_address = pair.get("pairAddress", "")
        dex_url = pair.get("url", f"https://dexscreener.com/{chain_id}/{pair_address}")
        dex_id = pair.get("dexId", "unknown")

        return {
            "token_address": address,
            "symbol": symbol.upper()[:20],
            "name": name[:50],
            "chain": chain_id,
            "price_usd": price_usd,
            "price_change_5m": pc5m,
            "price_change_1h": pc1h,
            "price_change_6h": pc6h,
            "price_change_24h": pc24h,
            "volume_24h": vol_24h,
            "volume_1h": vol_1h,
            "liquidity_usd": liq_usd,
            "market_cap": mcap,
            "fdv": fdv,
            "buys_1h": buys_1h,
            "sells_1h": sells_1h,
            "buy_pressure": buy_pressure,
            "age_minutes": round(age_minutes, 1),
            "pair_address": pair_address,
            "dex_url": dex_url,
            "dex_id": dex_id,
        }
    except Exception as e:
        logger.warning(f"Failed to parse pair: {e}")
        return None


def _is_valid_token(t: Dict[str, Any], min_liquidity: float = 10000, min_age: float = 10) -> bool:
    """Filter: remove garbage tokens."""
    if t["liquidity_usd"] < min_liquidity:
        return False
    if t["age_minutes"] < min_age:
        return False
    if t["volume_24h"] < 1000:
        return False
    if t["buys_1h"] + t["sells_1h"] < 5:
        return False
    return True


async def fetch_trending_tokens(
    chain: Optional[str] = None,
    limit: int = 30,
    min_liquidity: float = 10000,
    min_age: float = 10,
    max_age: float = 1440,
) -> List[Dict[str, Any]]:
    """Fetch trending token pairs from Dexscreener."""
    results = []

    # Dexscreener boosts endpoint for each chain
    chains_to_fetch = [chain] if chain and chain != "all" else ["solana", "ethereum", "base", "bsc", "arbitrum"]

    async with httpx.AsyncClient(timeout=15.0) as client:
        for ch in chains_to_fetch:
            try:
                # Try token-boosts endpoint first (most trending)
                resp = await client.get(
                    f"{DEXSCREENER_BASE}/token-boosts/top/v1",
                    params={"chainId": ch},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    pairs = data if isinstance(data, list) else []
                    for item in pairs[:30]:
                        addr = item.get("tokenAddress", "")
                        if not addr:
                            continue
                        # Fetch pair data for this token
                        try:
                            pair_resp = await client.get(
                                f"{DEXSCREENER_BASE}/latest/dex/tokens/{addr}",
                                timeout=8.0,
                            )
                            if pair_resp.status_code == 200:
                                pd = pair_resp.json()
                                pairs_data = pd.get("pairs", [])
                                if pairs_data:
                                    parsed = _parse_pair(pairs_data[0])
                                    if parsed and _is_valid_token(parsed, min_liquidity, min_age):
                                        if parsed["age_minutes"] <= max_age:
                                            results.append(parsed)
                        except Exception:
                            pass

                # Also fetch latest pairs for more coverage
                latest_resp = await client.get(
                    f"{DEXSCREENER_BASE}/latest/dex/pairs/{ch}",
                    timeout=10.0,
                )
                if latest_resp.status_code == 200:
                    ld = latest_resp.json()
                    for pair in (ld.get("pairs", []) or [])[:20]:
                        parsed = _parse_pair(pair)
                        if parsed and _is_valid_token(parsed, min_liquidity, min_age):
                            if parsed["age_minutes"] <= max_age:
                                # Avoid duplicates
                                if not any(r["token_address"] == parsed["token_address"] for r in results):
                                    results.append(parsed)

            except Exception as e:
                logger.warning(f"Dexscreener {ch} error: {e}")

    # Sort by volume_1h descending
    results.sort(key=lambda x: x["volume_1h"], reverse=True)
    return results[:limit]


async def fetch_token_by_address(address: str) -> Optional[Dict[str, Any]]:
    """Fetch token data by contract address."""
    async with httpx.AsyncClient(timeout=12.0) as client:
        try:
            resp = await client.get(f"{DEXSCREENER_BASE}/latest/dex/tokens/{address}")
            if resp.status_code == 200:
                data = resp.json()
                pairs = data.get("pairs", [])
                if pairs:
                    return _parse_pair(pairs[0])
        except Exception as e:
            logger.warning(f"Token fetch error {address}: {e}")
    return None


async def search_tokens(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search tokens by symbol or name."""
    async with httpx.AsyncClient(timeout=12.0) as client:
        try:
            resp = await client.get(
                f"{DEXSCREENER_BASE}/latest/dex/search",
                params={"q": query},
            )
            if resp.status_code == 200:
                data = resp.json()
                pairs = data.get("pairs", []) or []
                results = []
                for pair in pairs[:limit * 2]:
                    parsed = _parse_pair(pair)
                    if parsed:
                        results.append(parsed)
                return results[:limit]
        except Exception as e:
            logger.warning(f"Search error: {e}")
    return []
