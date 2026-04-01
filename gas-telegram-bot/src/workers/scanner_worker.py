"""
GAS Bot — Scanner Worker  [LOW priority queue: q:low]
Scans multiple pairs in parallel, sorts by probability.
- 1 concurrent worker
- 60s cache per scan batch
- Max 5 parallel AI calls within one scan
"""
import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.services.queue import Job
from src.services import cache, bot_api_client
from src.workers.base import BaseWorker
from src.utils.logger import logger

DEFAULT_SCAN_PAIRS = [
    "XAUUSD", "EURUSD", "GBPUSD", "USDJPY",
    "BTCUSD", "ETHUSD", "USOIL",  "US30",
]

_GRADE_EMOJI = {"SS": "🔥", "S": "⭐", "A+": "✅", "A": "🔵", "B": "🟡", "C": "⚪"}
_DIR_EMOJI   = {"BUY": "📈", "SELL": "📉"}


class ScannerWorker(BaseWorker):
    name        = "scanner"
    queue_names = ["q:low"]
    concurrency = 1

    async def process(self, job: Job) -> None:
        pairs  = job.pairs or DEFAULT_SCAN_PAIRS
        style  = (job.style or "intraday").lower()
        n      = len(pairs)

        # Cache check for full scan
        cache_key = f"scan:{style}:{','.join(sorted(pairs))}"
        cached    = await cache.get_scanner(cache_key)
        if cached:
            await self._edit(
                job,
                "📊 *Multi\\-Pair Scanner \\(cache 60s\\)*\n\n" + self._format(cached),
                markup=self._markup(),
            )
            return

        await self._edit(job, f"🔍 *Scanning {n} pairs\\.\\.\\.*\n\n`▓▓░░░░░░░░`  20%")

        # Parallel scan with semaphore (max 5 concurrent AI calls)
        sem = asyncio.Semaphore(5)

        async def scan_one(pair: str) -> dict | None:
            async with sem:
                sig = await cache.get_signal(pair, style)
                if sig:
                    return {"pair": pair, **sig}
                result = await bot_api_client.analyze(job.gas_user_id, pair, style, "technical")
                if "error" not in result:
                    await cache.set_signal(pair, style, result)
                    return {"pair": pair, **result}
                return None

        await self._edit(job, f"🔍 *Scanning {n} pairs\\.\\.\\.*\n\n`▓▓▓▓▓░░░░░`  50%")
        raw     = await asyncio.gather(*[scan_one(p) for p in pairs])
        results = [r for r in raw if r]
        results.sort(key=lambda x: x.get("probability", 0), reverse=True)

        await cache.set_scanner(cache_key, results)

        await self._edit(
            job,
            "📊 *Multi\\-Pair Scanner*\n\n" + self._format(results),
            markup=self._markup(),
        )
        logger.info("scanner_done", pairs=n, results=len(results), style=style, user=job.tg_user_id)

    def _format(self, results: list[dict]) -> str:
        from src.utils.formatter import _esc
        lines = []
        for r in results[:8]:
            grade  = r.get("grade", "B")
            signal = r.get("signal", "WAIT").upper()
            prob   = r.get("probability", 50)
            pair   = r.get("pair", "")
            ge     = _GRADE_EMOJI.get(grade, "⚪")
            de     = _DIR_EMOJI.get(signal, "⏸")
            lines.append(
                f"{ge} `{_esc(pair)}` {de} *{_esc(signal)}* \\| {_esc(grade)} \\| {prob}%"
            )
        return "\n".join(lines) if lines else "_Tidak ada sinyal valid_"

    def _markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Scan Ulang",   callback_data="scan_market")],
            [InlineKeyboardButton("🏠 Menu Utama",   callback_data="main_home")],
        ])
