"""
GAS Bot — Analyst Worker  [LOW priority queue: q:low]
Pipeline: bot_api_client.full_analyst() → /bot/analyst
  = strategy-core /hybrid + fundamental data + trend-engine + market-phase
Full-power AI: vision + fusion + reasoning.
- 1 concurrent worker (heavy requests)
- NO cache (always fresh, deepest analysis)
- Only queued by premium/ultimate users
"""
import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.services.queue import Job
from src.services import bot_api_client
from src.workers.base import BaseWorker
from src.utils.formatter import format_analyst_md
from src.utils.logger import logger


class AnalystWorker(BaseWorker):
    name        = "analyst"
    queue_names = ["q:low"]
    concurrency = 1   # heavy — serialize

    async def process(self, job: Job) -> None:
        pair  = job.pair.upper()
        style = job.style.lower()

        # Show full animation
        await self._loading_animation(job, pair, frames=5)

        # Final "thinking" frame
        await self._edit(
            job,
            f"🧠 *Full AI Analyst \\- {pair}*\n\n`▓▓▓▓▓▓▓▓▓▓`  99%\n\n_Finalizing deep analysis\\.\\.\\._",
        )
        await asyncio.sleep(0.5)

        # Analyst pipeline: /bot/analyst → hybrid + fundamental + trend + phase
        ai_tier = getattr(job, "ai_tier", "pro")
        result = await bot_api_client.full_analyst(job.gas_user_id, pair, style, ai_tier)
        if "error" in result:
            err = str(result["error"]).lower()
            raise RuntimeError(
                "no_credits" if ("kredit" in err or "402" in err) else "analysis_failed"
            )

        # Analyst results are NOT cached — always fresh
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Analisis Ulang", callback_data=f"exec_analyst_{pair}_{style}"),
                InlineKeyboardButton("📊 Pair Lain",      callback_data="nav_market_analyst"),
            ],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="m_main_menu")],
        ])
        await self._edit(
            job,
            "🏆 *Full Analyst Report*\n\n" + format_analyst_md(result, pair, style),
            markup=markup,
        )
        logger.info(
            "analyst_delivered",
            pair=pair, style=style, pipeline="analyst",
            grade=result.get("grade"), user=job.tg_user_id,
        )
