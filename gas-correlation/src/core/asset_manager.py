import numpy as np
from typing import Dict, List
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

class AssetManager:
    """Manages the list of tracked assets and their mock return series."""

    def __init__(self):
        self._assets: List[str] = settings.assets

    @property
    def assets(self) -> List[str]:
        return self._assets

    async def get_return_series(self, count: int = 100) -> Dict[str, List[float]]:
        """
        Fetch return series for all monitored assets.
        In production, this would call gas-feature-engine.
        For now, returns mock data seeded by asset name for reproducibility.
        """
        result = {}
        for i, sym in enumerate(self._assets):
            np.random.seed(hash(sym) % 2**31)
            base = np.random.randn(count) * 0.01
            # Add some cross-correlation patterns
            if sym == "DXY":
                np.random.seed(42)
                base = np.random.randn(count) * 0.005
            elif sym == "XAUUSD":
                np.random.seed(42)
                base = -np.random.randn(count) * 0.008  # Negative correlation with DXY
            result[sym] = base.tolist()
        return result

    async def get_latest_returns(self) -> Dict[str, float]:
        """Return the most recent single-period return for each asset (mock)."""
        series = await self.get_return_series(count=2)
        return {sym: vals[-1] for sym, vals in series.items()}
