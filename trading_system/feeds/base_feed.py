"""
Abstract market data feed provider.
Defines interface for both live and simulated market streams.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
try:
    from trading_system.core.models import MarketData, Candle
except (ImportError, ValueError):
    from core.models import MarketData, Candle

class BaseFeed(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def get_market_data(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> Optional[MarketData]:
        """Fetch market data and historical candles for a single symbol."""
        pass

    @abstractmethod
    async def get_all_markets(self, symbols: List[str], timeframe: str = "15m", limit: int = 100) -> Dict[str, MarketData]:
        """Fetch market data concurrently for 50+ markets."""
        pass
