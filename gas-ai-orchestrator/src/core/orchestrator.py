import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from src.core.model_router import router
from src.core.market_data import market_data, get_macro_context
from src.rag.retriever import retriever
from src.core.exceptions import OrchestratorException
from src.lib.logger import setup_logger

logger = setup_logger(__name__)

HYBRID_SYSTEM = """Anda adalah GAS AI — sistem analisa trading terintegrasi (SMC/ICT + Makro).

Tugas: Berikan FULL HYBRID ANALYSIS dalam format EXACT berikut. Ringkas, padat, actionable.
JANGAN tambah section lain. JANGAN berpanjang lebar.

FORMAT OUTPUT WAJIB:

## 🔭 OBSERVASI

[Fundamental 2-3 kalimat: DXY, yield, event/news utama, bias risk-on/risk-off]

[Teknikal per TF — tiap TF 1 baris]:
H4 [struktur, EMA key, RSI, ATR]
H1 [swing, Higher/Lower High/Low, EMA dinamis]
M15 [BOS/CHOCH, range aktif, RSI]
M5 [EMA9/21, rejection/breakout terakhir]

Likuiditas: [EQH/EQL, OB, FVG yang belum tersentuh]

---

## 🧠 REASONING

[2-4 kalimat: konfluensi teknikal + fundamental, skenario paling probable, kondisi entry ideal]

Probabilitas: BUY [X]% / SELL [Y]% / Ranging [Z]%

---

## 🎯 TRADING PLAN

Setup BUY [kondisi]
Entry  : [level]
SL     : [level]
TP1    : [level] — partial close 50%
TP2    : [level] — move SL ke entry
TP3    : [level] — biarkan jalan
RR     : [1:X / 1:X / 1:X]
Confidence : [X/10] [✅ >=6.5 / ⚠️ <6.5]

Setup SELL kondisional [kondisi jika ada]
Entry  : [level]
SL     : [level]
TP1    : [level]
TP2    : [level]
Confidence : [X/10] ⚠️

Status sekarang : [WAIT ⏳ / BUY NOW 🚀 / SELL NOW 🔴]
[1 kalimat — apa yang harus terjadi sebelum entry]

---

## 💰 RISK

Risk per trade : [0.5-1%] dari equity
Move BE        : setelah +[X] points
Partial close  : 50% di TP1
[Catatan: stop trading pre-event jika ada news besar]

---

## 🧘 MINDSET

[1-2 kalimat: pesan psikologi trading yang relevan dengan kondisi hari ini]

---

## 🤖 AI MENTOR

[1-2 kalimat: insight atau edge spesifik untuk setup ini yang trader retail sering lewatkan]

---

PENTING:
- Semua level harga HARUS angka spesifik dari data yang diberikan
- Bahasa: Indonesia, profesional, padat
- Jika data OHLCV tidak tersedia, gunakan estimasi berdasarkan konteks pair
"""


class AIOrchestrator:
    """GAS AI Orchestrator — Bloomberg Commands, Multi-TF data, Structured Output."""

    def __init__(self):
        self.user_models: Dict[str, str] = {}
        self.model_map = {
            # Vertex AI / Google
            "GEMINI-2.0-FLASH": "gemini-2.0-flash",
            "GEMINI-2.0-PRO": "gemini-2.0-pro-exp-02-05", # Mapping to experimental/latest
            "GEMINI-1.5-FLASH": "gemini-1.5-flash",
            "GEMINI-1.5-PRO": "gemini-1.5-pro",
            
            # Kimi (Moonshot)
            "KIMI-2.5": "moonshot-v1-128k", # Mapping latest available moonshot
            
            # DeepSeek
            "DEEPSEEK-V3": "deepseek-chat",
            "DEEPSEEK-R1": "deepseek-reasoner",
            
            # Anthropic
            "CLAUDE-3.5-HAIKU": "claude-3-5-haiku-20241022",
            "CLAUDE-3.7-SONNET": "claude-3-7-sonnet-20250219",
            "CLAUDE-OPUS-4": "claude-3-opus-20240229", # Opus 3.0, Opus 4 doesn't exist yet
            
            # Others via OpenRouter/Direct
            "GPT-OSS-120B": "gpt-4o", # Fallback for high-end
            "GLM-4.7": "glm-4",
            "QWEN-3": "qwen/qwen-2.5-72b-instruct",
            "MINIMAX-M2": "minimax/abab6.5-chat",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Data helpers
    # ─────────────────────────────────────────────────────────────────────────

    async def _build_ohlcv_context(self, pair: str) -> str:
        """Build OHLCV string from Redis ticks (H4/H1/M15/M5)."""
        # build_multi_tf_ohlcv is async, call directly
        return await market_data.build_multi_tf_ohlcv(pair)

    async def _build_macro_context(self, pair: str) -> str:
        """Load macro context for pair from datamacro.md."""
        # get_macro_context is sync, run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_macro_context, pair)

    # ─────────────────────────────────────────────────────────────────────────
    # Command parser
    # ─────────────────────────────────────────────────────────────────────────

    async def _parse_command(self, prompt: str, user_id: str) -> Optional[Dict[str, Any]]:
        parts = prompt.strip().upper().split()
        if not parts:
            return None
        cmd, args = parts[0], parts[1:]

        if cmd == "HELP":
            return {
                "type": "system",
                "result": (
                    "GAS BLOOMBERG TERMINAL — COMMAND REFERENCE\n"
                    "─────────────────────────────────────────\n"
                    "ANLS <PAIR>   Analisa Teknikal SMC\n"
                    "              Contoh: ANLS XAUUSD\n"
                    "FUND <PAIR>   Analisa Fundamental Makro\n"
                    "              Contoh: FUND EURUSD\n"
                    "Tombol HYBRID Gabungan Tech + Macro (rekomendasi)\n"
                    "NEWS          Ringkasan berita ekonomi\n"
                    "SGNL          Sinyal aktif GAS Engine\n"
                    "MODE FLASH    Gemini 2.0 Flash (default, cepat)\n"
                    "MODE PRO      Gemini 1.5 Pro (lebih dalam)\n"
                    "HELP          Halaman ini"
                ),
            }

        if cmd == "MODE":
            target = args[0] if args else "FLASH"
            model_id = self.model_map.get(target, self.model_map["FLASH"])
            self.user_models[user_id] = model_id
            return {"type": "system", "result": f"✅ Model diganti ke {target} ({model_id})"}

        if cmd in ("ANLS", "ANALISA"):
            is_hybrid = "FUND" in args or "HYBRID" in args
            pair = next((a for a in args if a not in ("FUND", "HYBRID")), None)
            return {"type": "hybrid" if is_hybrid else "technical", "pair": pair}

        if cmd in ("FUND", "FUNDAMENTAL"):
            return {"type": "macro", "pair": args[0] if args else None}

        if cmd in ("NEWS", "BERITA"):
            return {"type": "macro", "query": "latest economic news and market events summary"}

        if cmd in ("SGNL", "SIGNAL"):
            return {"type": "technical", "query": "active GAS signals summary"}

        return None

    # ─────────────────────────────────────────────────────────────────────────
    # Main analyze flow
    # ─────────────────────────────────────────────────────────────────────────

    async def analyze(
        self,
        prompt: str,
        ai_type: str,
        user_id: str,
        context: Dict[str, Any] = None,
        model_params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        logger.info(f"analyze | user={user_id} | type={ai_type} | prompt={prompt[:60]}")

        # ── Step 0: Parse Bloomberg commands ──────────────────────────────
        cmd = await self._parse_command(prompt, user_id)
        if cmd:
            if cmd.get("type") == "system":
                return {
                    "id": f"sys_{uuid.uuid4().hex[:8]}",
                    "type": "system",
                    "result": {"summary": cmd["result"], "confidence": 1.0, "levels": {}},
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ai_type = cmd["type"]
            if cmd.get("pair"):
                context = {**(context or {}), "pair": cmd["pair"]}

        # Priority: explicit model_id in params > user session > default
        active_model = (model_params or {}).get("model_id") or self.user_models.get(user_id, "GEMINI-2.0-FLASH")
        # Ensure it's a key in our map
        model_name = active_model if active_model in self.model_map else "GEMINI-2.0-FLASH"
        model_id = self.model_map[model_name]
        
        mp = {**(model_params or {}), "model_id": model_id, "model_name": model_name}
        context = context or {}
        pair = context.get("pair") or self._extract_pair(prompt) or "XAUUSD"

        # ── Step 1: HYBRID — single comprehensive call ─────────────────────
        if ai_type.lower() == "hybrid":
            return await self._run_hybrid(pair, active_model, mp)

        # ── Step 2: Fetch OHLCV for technical / macro context for fund ────
        ohlcv_block = ""
        macro_block = ""
        if ai_type.lower() == "technical":
            logger.info(f"Fetching multi-TF OHLCV for {pair}")
            ohlcv_block = await self._build_ohlcv_context(pair)
        elif ai_type.lower() == "macro":
            logger.info(f"Loading macro context for {pair}")
            macro_raw = await self._build_macro_context(pair)
            if macro_raw:
                macro_block = f"[MACRO DATA — datamacro.md — {pair}]\n{macro_raw}\n\n"

        # ── Step 3: RAG enrichment ─────────────────────────────────────────
        rag_ctx = retriever.get_context(query=prompt, top_k=3)
        rag_block = ("Konteks RAG:\n" + "\n".join(rag_ctx) + "\n\n") if rag_ctx else ""

        enhanced = (
            f"{rag_block}"
            f"{macro_block}"
            f"{ohlcv_block}\n\n"
            f"Pair: {pair}\n"
            f"Permintaan: {prompt}"
        )

        # ── Step 4: Select client and generate ────────────────────────────
        try:
            client = router.get_client(ai_type)
        except Exception as e:
            raise OrchestratorException(str(e))

        try:
            raw = await client.generate(enhanced, mp)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise OrchestratorException(f"Generation failed: {e}")

        return {
            "id": f"analysis_{uuid.uuid4().hex[:8]}",
            "type": ai_type,
            "result": {
                "summary": raw,
                "model": active_model,
                "confidence": 0.95,
                "levels": {},
            },
            "sources": rag_ctx or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Hybrid: one unified call — more coherent than two separate calls
    # ─────────────────────────────────────────────────────────────────────────

    async def _run_hybrid(self, pair: str, active_model: str, mp: Dict) -> Dict:
        logger.info(f"Running HYBRID analysis for {pair}")

        # Fetch OHLCV and macro context concurrently
        ohlcv_data, macro_data = await asyncio.gather(
            self._build_ohlcv_context(pair),
            self._build_macro_context(pair),
        )
        now = datetime.now(timezone.utc).strftime("%A, %d %B %Y %H:%M UTC")

        macro_section = f"[MACRO DATA — datamacro.md]\n{macro_data}\n\n" if macro_data else ""

        hybrid_prompt = (
            f"{HYBRID_SYSTEM}\n\n"
            f"Pair    : {pair}\n"
            f"Waktu   : {now}\n\n"
            f"{macro_section}"
            f"{ohlcv_data if ohlcv_data else '[Data OHLCV tidak tersedia — gunakan estimasi berdasarkan kondisi pasar terkini]'}\n\n"
            f"Buat FULL HYBRID ANALYSIS untuk {pair} sekarang."
        )

        try:
            client = router.get_client("technical")  # uses GeneralModelClient under the hood
            raw = await client.generate(hybrid_prompt, mp)
        except Exception as e:
            logger.error(f"Hybrid generation failed: {e}")
            raw = f"[GAS AI ERROR] Hybrid analysis gagal: {e}"

        return {
            "id": f"hybrid_{uuid.uuid4().hex[:8]}",
            "type": "hybrid",
            "result": {"summary": raw, "model": active_model, "confidence": 0.95, "levels": {}},
            "sources": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _extract_pair(self, text: str) -> Optional[str]:
        known = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "GBPJPY",
                 "BTCUSD", "ETHUSD", "NASDAQ", "US30", "AUDUSD", "USDCAD"]
        up = text.upper()
        return next((p for p in known if p in up), None)


orchestrator = AIOrchestrator()
