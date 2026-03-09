from typing import Dict, Any
import os
from src.models.base import BaseModelClient
from src.config import settings
from src.lib.logger import setup_logger
import httpx
import json

logger = setup_logger(__name__)

# Model fallback chain — try in order until one works on Vertex AI
VERTEX_MODEL_CHAIN = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


class GeneralModelClient(BaseModelClient):
    """Client for Google Vertex AI (Gemini) with automatic model fallback."""

    def __init__(self):
        self.credentials_path = settings.google_application_credentials
        self.project_id = "gen-lang-client-0060492434"
        self.location = "us-central1"
        self.default_model = "gemini-2.0-flash"

        self.initialized = False
        self.genai_initialized = False
        self._working_model = None  # cache the first model that succeeds

        # Try Vertex AI via service account
        try:
            import vertexai
            from google.oauth2 import service_account
            if os.path.exists(self.credentials_path):
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                vertexai.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=creds,
                )
                self.initialized = True
                logger.info("Vertex AI initialized via Service Account")
            else:
                logger.warning(f"Credentials not found at {self.credentials_path}")
        except Exception as e:
            logger.error(f"Vertex AI init failed: {e}")

        # Try google-generativeai as fallback if API key is set
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.genai_initialized = True
                logger.info("google-generativeai initialized via API key")
            except Exception as e:
                logger.error(f"google-generativeai init failed: {e}")

        # Provider keys from env
        self.kimi_key = os.getenv("MOONSHOT_API_KEY", "sk-jHaST2FHxfBpQv6ulgWrIeI7D07m4jdgNiGlDpoob6ld3cV4")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

    async def generate(self, prompt: str, params: Dict[str, Any] = None) -> str:
        model_id = (params or {}).get("model_id", self.default_model)
        temp = (params or {}).get("temperature", 0.7)

        # Route by model naming convention — fallback to Vertex AI if provider returns None
        mid_lower = model_id.lower()

        if "moonshot" in mid_lower or "kimi" in mid_lower:
            result = await self._try_kimi(prompt, model_id, temp)
            if result:
                return result
            logger.warning(f"Kimi failed for {model_id}, falling back to Vertex AI")

        elif "deepseek" in mid_lower:
            result = await self._try_deepseek(prompt, model_id, temp)
            if result:
                return result
            logger.warning(f"DeepSeek failed for {model_id}, falling back to Vertex AI")

        elif "claude" in mid_lower or "anthropic" in mid_lower:
            result = await self._try_anthropic(prompt, model_id, temp)
            if result:
                return result
            logger.warning(f"Anthropic failed for {model_id}, falling back to Vertex AI")

        elif any(x in mid_lower for x in ["qwen", "glm", "minimax", "gpt-oss"]):
            result = await self._try_openrouter(prompt, model_id, temp)
            if result:
                return result
            logger.warning(f"OpenRouter failed for {model_id}, falling back to Vertex AI")

        # Path 1: Vertex AI (Default for Gemini)
        if self.initialized:
            result = await self._try_vertex(prompt, model_id, temp)
            if result:
                return result

        # Path 2: Direct google-generativeai API fallback
        if self.genai_initialized:
            result = await self._try_genai(prompt, model_id, temp)
            if result:
                return result

        # Path 3: Rich static analysis
        logger.warning("All AI backends failed — returning static analysis")
        return self._static_analysis(prompt)

    async def _try_vertex(self, prompt: str, model_id: str, temp: float):
        try:
            from vertexai.generative_models import GenerativeModel
        except ImportError:
            return None

        # Build candidate list: requested model first, then fallbacks
        candidates = [model_id] + [m for m in VERTEX_MODEL_CHAIN if m != model_id]
        if self._working_model:
            candidates = [self._working_model] + [
                c for c in candidates if c != self._working_model
            ]

        for mid in candidates:
            try:
                model = GenerativeModel(mid)
                response = await model.generate_content_async(
                    prompt,
                    generation_config={
                        "temperature": temp,
                        "max_output_tokens": 4096 if "pro" in mid else 2048,
                    },
                )
                self._working_model = mid
                logger.info(f"Vertex AI success: {mid}")
                return response.text
            except Exception as e:
                err = str(e)
                if "404" in err or "not found" in err.lower() or "not have access" in err.lower():
                    logger.warning(f"Model {mid} unavailable, trying next…")
                    continue
                logger.error(f"Vertex AI error ({mid}): {err}")
                return None

        logger.error("All Vertex AI model candidates exhausted")
        return None

    async def _try_genai(self, prompt: str, model_id: str, temp: float):
        try:
            import google.generativeai as genai
            mid = model_id.removesuffix("-001") if model_id.endswith("-001") else model_id
            model = genai.GenerativeModel(mid)
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temp, max_output_tokens=2048
                ),
            )
            logger.info(f"google-generativeai success: {mid}")
            return response.text
        except Exception as e:
            logger.error(f"google-generativeai error: {e}")
            return None

    async def _try_kimi(self, prompt: str, model_id: str, temp: float):
        if not self.kimi_key: return None
        url = "https://api.moonshot.cn/v1/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp
        }
        return await self._openai_style_request("Kimi", url, self.kimi_key, payload)

    async def _try_deepseek(self, prompt: str, model_id: str, temp: float):
        if not self.deepseek_key: return None
        url = "https://api.deepseek.com/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp,
            "stream": False
        }
        return await self._openai_style_request("DeepSeek", url, self.deepseek_key, payload)

    async def _try_anthropic(self, prompt: str, model_id: str, temp: float):
        if not self.anthropic_key: return None
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model_id,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["content"][0]["text"]
                logger.error(f"Anthropic error: {resp.status_code} {resp.text}")
            except Exception as e:
                logger.error(f"Anthropic request failed: {e}")
        return None

    async def _try_openrouter(self, prompt: str, model_id: str, temp: float):
        if not self.openrouter_key: return None
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp
        }
        return await self._openai_style_request("OpenRouter", url, self.openrouter_key, payload)

    async def _openai_style_request(self, name: str, url: str, key: str, payload: dict):
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                logger.error(f"{name} error: {resp.status_code} {resp.text}")
            except Exception as e:
                logger.error(f"{name} request failed: {e}")
        return None

    def _static_analysis(self, prompt: str) -> str:
        prompt_upper = prompt.upper()
        pairs = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "NASDAQ", "US30", "GBPJPY", "AUDUSD"]
        pair = next((p for p in pairs if p in prompt_upper), "XAUUSD")

        if any(k in prompt_upper for k in ["ANLS", "ANALISA", "TECHNICAL"]):
            return (
                f"[GAS AI — OFFLINE MODE]\n\n"
                f"TECHNICAL ANALYSIS: {pair}\n"
                f"{'─' * 34}\n"
                f"Regime     : RANGING → potensi reversal\n"
                f"Structure  : Belum ada BOS/CHOCH M15\n"
                f"Bias       : NEUTRAL — tunggu konfirmasi\n"
                f"Key Level  : Identifikasi FVG + OB di H1\n"
                f"Setup      : WAIT — entry setelah SMS\n\n"
                f"[!] AI Engine offline. Analisa manual SMC/ICT tetap berlaku."
            )
        if any(k in prompt_upper for k in ["FUND", "FUNDAMENTAL", "MACRO"]):
            return (
                f"[GAS AI — OFFLINE MODE]\n\n"
                f"FUNDAMENTAL: {pair}\n"
                f"{'─' * 34}\n"
                f"DXY        : Pantau level kritis USD\n"
                f"Risk       : Risk-on/off belum jelas\n"
                f"Catalyst   : Cek kalender ekonomi\n"
                f"Sentiment  : Netral — data makro mixed\n\n"
                f"[!] AI Engine offline. Gunakan FUND manual."
            )
        if "NEWS" in prompt_upper or "BERITA" in prompt_upper:
            return (
                "[GAS AI — OFFLINE MODE]\n\n"
                "NEWS SUMMARY\n"
                "─────────────────────────────────\n"
                "• Fed: Data inflasi/NFP jadi fokus\n"
                "• Gold: Geopolitik tetap jadi driver\n"
                "• Forex: DXY tentukan arah major pairs\n\n"
                "[!] AI Engine offline. Cek news manual."
            )
        return (
            "[GAS AI — OFFLINE MODE]\n"
            "Koneksi ke AI Engine gagal.\n"
            "Perintah tersedia: ANLS <PAIR> | FUND <PAIR> | NEWS | SGNL | HELP"
        )
