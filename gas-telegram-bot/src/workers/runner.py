"""
GAS Bot — Worker Runner
Call run_workers(bot) from main.py to launch the full worker pool
as asyncio tasks alongside the bot polling loop.

Worker pool:
  3× SignalWorker   — q:high  (fast, cached 30s)
  2× AnalysisWorker — q:medium + q:high drain
  1× AnalystWorker  — q:low   (full power, no cache)
  1× ScannerWorker  — q:low   (multi-pair)
  1× FeedWorker     — interval (news + calendar cache)
"""
import asyncio
from telegram import Bot

from src.workers.signal_worker   import SignalWorker
from src.workers.analysis_worker import AnalysisWorker
from src.workers.analyst_worker  import AnalystWorker
from src.workers.scanner_worker  import ScannerWorker
from src.workers.feed_worker     import FeedWorker
from src.utils.logger import logger


async def run_workers(bot: Bot) -> None:
    """Launch all workers. Runs until cancelled."""
    logger.info("worker_pool_starting")

    coros = [
        # 3 fast signal workers (high priority)
        SignalWorker(bot).run(),
        SignalWorker(bot).run(),
        SignalWorker(bot).run(),
        # 2 analysis workers (medium priority, also drain high)
        AnalysisWorker(bot).run(),
        AnalysisWorker(bot).run(),
        # 1 full-power analyst (low priority, serialized)
        AnalystWorker(bot).run(),
        # 1 scanner (low priority)
        ScannerWorker(bot).run(),
        # 1 feed fetcher (background interval)
        FeedWorker().run(),
    ]

    logger.info("worker_pool_ready", workers=len(coros))
    await asyncio.gather(*coros, return_exceptions=True)
