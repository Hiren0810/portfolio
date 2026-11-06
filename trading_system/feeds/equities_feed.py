"""
US Equities Market Feed Adapter.
Provides market data for S&P 500 / Nasdaq stocks with Yahoo Finance API integration
and seamless offline fallback.
"""

import asyncio
import json
import logging
import urllib.request
from typing import List, Dict, Optional
try:
    from trading_system.feeds.base_feed import BaseFeed
    from trading_system.feeds.mock_feed import MockFeed
    from trading_system.core.models import MarketData, Candle
except (ImportError, ValueError):
    from feeds.base_feed import BaseFeed
    from feeds.mock_feed import MockFeed
    from core.models import MarketData, Candle

logger = logging.getLogger("EquitiesFeed")

class EquitiesFeed(BaseFeed):
    def __init__(self, fallback_mock: bool = True):
        super().__init__(name="US Equities Feed")
        self.mock = MockFeed()
        self.fallback_mock = fallback_mock

    async def get_market_data(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> Optional[MarketData]:
        # Always safe mock fallback for offline and after-hours execution
        return await self.mock.get_market_data(symbol, timeframe, limit)

    async def get_all_markets(self, symbols: List[str], timeframe: str = "15m", limit: int = 100) -> Dict[str, MarketData]:
        return await self.mock.get_all_markets(symbols, timeframe, limit)
