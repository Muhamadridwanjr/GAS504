"""
GAS Bot — Analysis Worker  [MEDIUM priority queue: q:medium]
Pipeline: bot_api_client.deep_analysis() → /bot/analysis
  = strategy-core /technical (MTF indicators) + calendar context + correlation
Also drains q:high if signal workers are all busy.
- 2 concurrent workers
- Full 5-frame animation
- Caches result same as signal worker
"""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.services.queue import Job
from src.services import cache, credit, bot_api_client
from src.workers.base import BaseWorker
from src.utils.formatter import format_analysis_md
from src.utils.logger import logger


class AnalysisWorker(BaseWorker):
    name        = "analysis"
    queue_names = ["q:medium", "q:high"]   # help drain high if signal workers busy
    concurrency = 2

    async def process(self, job: Job) -> None:
        pair      = job.pair.upper()
        style     = job.style.lower()
        ai_tier   = getattr(job, "ai_tier", "advanced")
        cache_ttl = getattr(job, "cache_ttl", 15)
        plan      = getattr(job, "plan", "plus")

        # Cache check (skip if cache_ttl=0)
        if cache_ttl > 0:
            cached = await cache.get_signal(pair, f"analysis:{style}")
            if cached:
                cached["credits_remaining"] = await credit.get_balance(job.gas_user_id)
                await self._edit(
                    job,
                    f"✅ *Analisis \\(cache {cache_ttl}s\\)*\n\n" + format_analysis_md(cached, pair, style),
                    markup=self._markup(pair, style),
                )
                return

        # Full 5-frame animation
        await self._loading_animation(job, pair, frames=5)

        # Analysis pipeline: /bot/analysis → technical MTF + calendar + correlation
        result = await bot_api_client.deep_analysis(job.gas_user_id, pair, style, ai_tier)
        if "error" in result:
            err = str(result["error"]).lower()
            raise RuntimeError(
                "no_credits" if ("kredit" in err or "402" in err) else "analysis_failed"
            )

        if cache_ttl > 0:
            await cache.set_signal(pair, f"analysis:{style}", result, ttl=cache_ttl)

        await self._edit(
            job,
            "✅ *Analisis Teknikal MTF*\n\n" + format_analysis_md(result, pair, style),
            markup=self._markup(pair, style),
        )
        logger.info(
            "analysis_delivered",
            pair=pair, style=style, pipeline="analysis",
            ai_tier=ai_tier, user=job.tg_user_id,
        )

    def _markup(self, pair: str, style: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Analisis Ulang", callback_data=f"exec_analysis_{pair}_{style}"),
                InlineKeyboardButton("📊 Pair Lain",      callback_data="nav_market_analysis"),
            ],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="m_main_menu")],
        ])
