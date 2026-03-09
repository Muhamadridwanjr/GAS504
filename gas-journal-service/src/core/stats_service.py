from src.db.repositories.trade_repo import TradeRepository
from src.redis.client import redis_client
from uuid import UUID
from decimal import Decimal
from src.lib.logger import logger
import json


class StatsService:
    def __init__(self, repo: TradeRepository):
        self.repo = repo

    async def get_stats(
        self,
        user_id: UUID,
        symbol: str = None,
        from_date=None,
        to_date=None,
    ) -> dict:
        """Calculate trading statistics for a user."""
        # Try cache first
        cache_key = f"stats:{user_id}:{symbol or 'all'}:{from_date or 'none'}:{to_date or 'none'}"
        cached = await redis_client.get_cached(cache_key)
        if cached:
            logger.debug(f"Stats cache hit for user {user_id}")
            return cached

        # Get closed trades from DB
        trades = await self.repo.get_closed_trades_for_stats(
            user_id=user_id,
            symbol=symbol,
            from_date=from_date,
            to_date=to_date,
        )

        total_trades = len(trades)
        if total_trades == 0:
            stats = {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "breakeven_trades": 0,
                "win_rate": 0.0,
                "total_profit": 0.0,
                "total_commission": 0.0,
                "total_swap": 0.0,
                "net_profit": 0.0,
                "average_profit": 0.0,
                "average_loss": 0.0,
                "average_rr": 0.0,
                "max_drawdown": 0.0,
                "profit_factor": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
            }
            await redis_client.set_cached(cache_key, stats, ttl=300)
            return stats

        # Calculations
        winning = [t for t in trades if (t.profit or 0) > 0]
        losing = [t for t in trades if (t.profit or 0) < 0]
        breakeven = [t for t in trades if (t.profit or 0) == 0]

        total_profit = sum(float(t.profit or 0) for t in trades)
        total_commission = sum(float(t.commission or 0) for t in trades)
        total_swap = sum(float(t.swap or 0) for t in trades)
        net_profit = total_profit - total_commission - total_swap

        win_profits = [float(t.profit) for t in winning]
        loss_amounts = [abs(float(t.profit)) for t in losing]

        avg_profit = sum(win_profits) / len(win_profits) if win_profits else 0.0
        avg_loss = sum(loss_amounts) / len(loss_amounts) if loss_amounts else 0.0

        # Average Risk/Reward ratio
        average_rr = round(avg_profit / avg_loss, 2) if avg_loss > 0 else 0.0

        # Profit factor = gross profit / gross loss
        gross_profit = sum(win_profits) if win_profits else 0.0
        gross_loss = sum(loss_amounts) if loss_amounts else 0.0
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else 0.0

        # Max drawdown (peak-to-trough in equity curve)
        max_drawdown = self._calculate_max_drawdown(trades)

        stats = {
            "total_trades": total_trades,
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "breakeven_trades": len(breakeven),
            "win_rate": round(len(winning) / total_trades * 100, 2),
            "total_profit": round(total_profit, 2),
            "total_commission": round(total_commission, 2),
            "total_swap": round(total_swap, 2),
            "net_profit": round(net_profit, 2),
            "average_profit": round(avg_profit, 2),
            "average_loss": round(avg_loss, 2),
            "average_rr": average_rr,
            "max_drawdown": round(max_drawdown, 2),
            "profit_factor": profit_factor,
            "largest_win": round(max(win_profits) if win_profits else 0.0, 2),
            "largest_loss": round(max(loss_amounts) if loss_amounts else 0.0, 2),
        }

        # Cache for 5 minutes
        await redis_client.set_cached(cache_key, stats, ttl=300)
        logger.info(f"Stats calculated for user {user_id}: {total_trades} trades, win rate {stats['win_rate']}%")
        return stats

    def _calculate_max_drawdown(self, trades) -> float:
        """Calculate maximum drawdown from equity curve."""
        if not trades:
            return 0.0

        equity = 0.0
        peak = 0.0
        max_dd = 0.0

        for trade in trades:
            equity += float(trade.profit or 0)
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            if drawdown > max_dd:
                max_dd = drawdown

        return max_dd
