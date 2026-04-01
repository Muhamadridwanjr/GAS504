"""
GAS Bot — BaseWorker
All workers inherit from this. Provides:
  - run() main loop with semaphore-limited concurrency
  - _edit()  — edit the queued Telegram message
  - _send_error() — edit with error message + retry keyboard
  - _loading_animation() — 5-frame animated progress bar
"""
import asyncio
import time
from abc import ABC, abstractmethod

from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode

from src.services.queue import Job, JobStatus, dequeue, update_job
from src.utils.formatter import format_error_md
from src.utils.logger import logger

_LOADING_FRAMES = [
    ("⏳", "10%", "▓░░░░░░░░░"),
    ("⏳", "30%", "▓▓▓░░░░░░░"),
    ("⏳", "50%", "▓▓▓▓▓░░░░░"),
    ("⚡", "70%", "▓▓▓▓▓▓▓░░░"),
    ("🧠", "90%", "▓▓▓▓▓▓▓▓▓░"),
]


class BaseWorker(ABC):
    name:        str       = "base"
    queue_names: list[str] = []
    concurrency: int       = 1

    def __init__(self, bot: Bot):
        self.bot      = bot
        self._running = True

    # ── Public ────────────────────────────────────────────────────────────────

    async def run(self) -> None:
        """Main blocking loop. Dequeues and dispatches jobs."""
        logger.info("worker_started", worker=self.name, concurrency=self.concurrency)
        semaphore = asyncio.Semaphore(self.concurrency)

        while self._running:
            try:
                job = await dequeue(self.queue_names, timeout=5)
                if job is None:
                    continue
                asyncio.create_task(self._handle(job, semaphore))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("worker_loop_error", worker=self.name, error=str(e))
                await asyncio.sleep(1)

        logger.info("worker_stopped", worker=self.name)

    def stop(self) -> None:
        self._running = False

    # ── Abstract ──────────────────────────────────────────────────────────────

    @abstractmethod
    async def process(self, job: Job) -> None:
        """Override in subclass. Raises on failure (triggers refund + error msg)."""
        ...

    # ── Internals ─────────────────────────────────────────────────────────────

    async def _handle(self, job: Job, semaphore: asyncio.Semaphore) -> None:
        async with semaphore:
            await update_job(job.id, status=JobStatus.PROCESSING, started_at=time.time())
            try:
                await self.process(job)
                await update_job(job.id, status=JobStatus.DONE, finished_at=time.time())
            except Exception as e:
                err_str = str(e)
                logger.error("worker_job_failed", worker=self.name, job_id=job.id, error=err_str)
                await update_job(
                    job.id, status=JobStatus.FAILED,
                    error=err_str, finished_at=time.time(),
                )
                # Refund credits if payment error is not the cause
                if "no_credits" not in err_str:
                    from src.services.credit import refund
                    from src.utils.session import get_state
                    state = await get_state(job.tg_user_id) or {}
                    cost  = state.get("pending_cost", 0)
                    if cost > 0:
                        await refund(job.gas_user_id, cost)

                error_code = err_str if err_str in (
                    "no_credits", "analysis_failed", "timeout", "plan_required"
                ) else "analysis_failed"
                await self._send_error(job, error_code)

    async def _edit(self, job: Job, text: str, markup=None) -> None:
        """Edit the original queued message."""
        kwargs = dict(
            chat_id=job.chat_id,
            message_id=job.message_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        if markup:
            kwargs["reply_markup"] = markup
        try:
            await self.bot.edit_message_text(**kwargs)
        except Exception as e:
            logger.warning("edit_message_failed", error=str(e))
            # Fallback: send new message so user isn't left with nothing
            try:
                await self.bot.send_message(
                    chat_id=job.chat_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=markup,
                )
            except Exception:
                pass

    async def _send_error(self, job: Job, error_code: str) -> None:
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Coba Lagi", callback_data=f"exec_{job.pair}_{job.style}")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="main_home")],
        ])
        try:
            await self.bot.edit_message_text(
                chat_id=job.chat_id,
                message_id=job.message_id,
                text=format_error_md(error_code),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup,
            )
        except Exception:
            pass

    async def _loading_animation(self, job: Job, pair: str = "", frames: int = 5) -> None:
        """Animate progress bar by editing message (up to 5 frames × 0.7s)."""
        label = pair or job.pair
        for i, (emoji, pct, bar) in enumerate(_LOADING_FRAMES[:frames]):
            verb = "Menyempurnakan Sinyal" if i == 4 else f"Menganalisis {label}"
            verb_esc = verb.replace(".", "\\.").replace("-", "\\-")
            text = f"{emoji} *{verb_esc}\\.\\.\\.*\n\n`{bar}`  {pct}"
            try:
                await self.bot.edit_message_text(
                    chat_id=job.chat_id,
                    message_id=job.message_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            except Exception:
                pass
            await asyncio.sleep(0.7)
