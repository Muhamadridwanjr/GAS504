"""
GAS Bot — Signal Worker  [HIGH priority queue: q:high]
Pipeline: bot_api_client.signal() → /bot/signal
  = strategy-core /signal + calendar-news high-impact check
- 3 concurrent workers
- 30s signal cache shared across all users
- Fastest path: cache hit → no AI call, no credit deduct
"""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.services.queue import Job
from src.services import cache, credit, bot_api_client
from src.workers.base import BaseWorker
from src.utils.formatter import format_signal_md
from src.utils.logger import logger


class SignalWorker(BaseWorker):
    name        = "signal"
    queue_names = ["q:high"]
    concurrency = 3

    async def process(self, job: Job) -> None:
        pair      = job.pair.upper()
        style     = job.style.lower()
        ai_tier   = getattr(job, "ai_tier", "basic")
        cache_ttl = getattr(job, "cache_ttl", 30)

        # ── 1. Cache hit (skip if cache_ttl=0 for ultimate) ───────────────────
        if cache_ttl > 0:
            cached = await cache.get_signal(pair, style)
            if cached:
                cached["credits_remaining"] = await credit.get_balance(job.gas_user_id)
                cache_label = f"cache {cache_ttl}s"
                await self._edit(
                    job,
                    f"✅ *Sinyal Terbaru \\({cache_label}\\)*\n\n" + format_signal_md(cached, pair, style),
                    markup=self._result_markup(pair, style, getattr(job, "plan", "free")),
                )
                logger.info("signal_cache_hit", pair=pair, style=style, user=job.tg_user_id)
                return

        # ── 2. Loading animation ───────────────────────────────────────────────
        await self._loading_animation(job, pair, frames=2)

        # ── 3. Signal pipeline: /bot/signal → indicator + strategy-core + calendar
        result = await bot_api_client.signal(job.gas_user_id, pair, style, ai_tier)

        if "error" in result:
            err = str(result["error"]).lower()
            raise RuntimeError(
                "no_credits" if ("kredit" in err or "402" in err) else "analysis_failed"
            )

        # ── 4. Finish animation ───────────────────────────────────────────────
        await self._loading_animation(job, pair, frames=3)

        # ── 5. Cache (skip for ultimate/no-cache plans) ───────────────────────
        if cache_ttl > 0:
            await cache.set_signal(pair, style, result, ttl=cache_ttl)

        # ── 6. Build output with calendar warning if present ─────────────────
        plan        = getattr(job, "plan", "free")
        cal_warning = result.get("calendar_warning", "")
        header      = "✅ *Sinyal Terbaru*"
        if cal_warning:
            from src.utils.formatter import _esc
            header += f"\n\n_{_esc(cal_warning)}_"

        await self._edit(
            job,
            header + "\n\n" + format_signal_md(result, pair, style),
            markup=self._result_markup(pair, style, plan),
        )
        logger.info(
            "signal_delivered",
            pair=pair, style=style, pipeline="signal",
            grade=result.get("grade"), prob=result.get("probability"),
            user=job.tg_user_id,
        )

    def _result_markup(self, pair: str, style: str, plan: str = "free") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Refresh Sinyal", callback_data=f"exec_signal_{pair}_{style}"),
                InlineKeyboardButton("📊 Pair Lain",      callback_data="nav_market_signal"),
            ],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="m_main_menu")],
        ])
