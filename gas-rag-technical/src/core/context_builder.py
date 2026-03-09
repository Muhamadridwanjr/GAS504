"""
Context builder – assembles the enriched prompt sent to the LLM.
Combines retrieved documents with live market data and query.
"""
from typing import Any
from src.lib.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """Anda adalah analis teknikal profesional yang ahli dalam pasar forex, 
komoditas, dan kripto. Anda menganalisis pasar menggunakan metodologi Smart Money Concepts (SMC), 
price action, dan indikator teknikal. Selalu berikan analisis yang actionable, terstruktur, 
dan didukung bukti dari data yang diberikan. Respons HARUS dalam format JSON yang valid."""

ANALYSIS_TEMPLATE = """
## Konteks Analisis

### Query Pengguna
{query}

### Informasi Aset
- **Simbol:** {symbol}
- **Timeframe:** {timeframe}

### Data Pasar Saat Ini
{market_data}

### Indikator Teknikal
{indicators}

### SMC Context
{smc_context}

### Konteks dari Knowledge Base (Relevan)
{retrieved_context}

---

## Instruksi Output

Berikan analisis dalam format JSON berikut:
```json
{{
  "summary": "Ringkasan singkat kondisi pasar (1-2 kalimat)",
  "key_levels": {{
    "support": [harga_support_1, harga_support_2],
    "resistance": [harga_resistance_1, harga_resistance_2]
  }},
  "signal": "BUY | SELL | NEUTRAL",
  "confidence": 0.0-1.0,
  "entry": {{
    "price": null,
    "stop_loss": null,
    "take_profit": []
  }},
  "reasoning": "Penjelasan detail alasan analisis berdasarkan data",
  "short_term_bias": "bullish | bearish | sideways",
  "key_risks": ["risiko utama 1", "risiko utama 2"]
}}
```
"""


def build_prompt(
    query: str,
    symbol: str,
    timeframe: str,
    market_data: dict[str, Any] | None = None,
    indicators: dict[str, Any] | None = None,
    smc_context: dict[str, Any] | None = None,
    retrieved_docs: list[dict[str, Any]] | None = None,
) -> tuple[str, str]:
    """
    Build system prompt and user prompt for the LLM.

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Format market data
    md_text = _format_market_data(market_data or {})

    # Format indicators
    ind_text = _format_indicators(indicators or {})

    # Format SMC context
    smc_text = _format_smc(smc_context or {})

    # Format retrieved documents
    rag_text = _format_retrieved_docs(retrieved_docs or [])

    user_prompt = ANALYSIS_TEMPLATE.format(
        query=query,
        symbol=symbol,
        timeframe=timeframe,
        market_data=md_text,
        indicators=ind_text,
        smc_context=smc_text,
        retrieved_context=rag_text,
    )

    return SYSTEM_PROMPT, user_prompt


def _format_market_data(data: dict[str, Any]) -> str:
    if not data:
        return "Data pasar tidak tersedia."
    lines = []
    for k, v in data.items():
        lines.append(f"- **{k}:** {v}")
    return "\n".join(lines)


def _format_indicators(data: dict[str, Any]) -> str:
    if not data:
        return "Indikator tidak tersedia."
    lines = []
    for k, v in data.items():
        lines.append(f"- **{k.upper()}:** {v}")
    return "\n".join(lines)


def _format_smc(data: dict[str, Any]) -> str:
    if not data:
        return "Data SMC tidak tersedia."
    parts = []
    if "order_blocks" in data and data["order_blocks"]:
        parts.append(f"Order Blocks: {len(data['order_blocks'])} ditemukan")
    if "fvgs" in data and data["fvgs"]:
        parts.append(f"Fair Value Gaps: {len(data['fvgs'])} ditemukan")
    if "liquidity_levels" in data:
        parts.append(f"Likuiditas: {data['liquidity_levels']}")
    return "\n".join(parts) if parts else "Tidak ada data SMC."


def _format_retrieved_docs(docs: list[dict[str, Any]]) -> str:
    if not docs:
        return "Tidak ada konteks yang ditemukan dari knowledge base."
    parts = []
    for i, doc in enumerate(docs[:5], 1):          # top 5 docs
        text = doc.get("text", doc.get("content", ""))[:600]
        source = doc.get("source", doc.get("title", f"Dokumen {i}"))
        relevance = doc.get("relevance", doc.get("score", 0.0))
        parts.append(f"**[{i}] {source}** (relevansi: {relevance:.2f})\n{text}\n")
    return "\n---\n".join(parts)
