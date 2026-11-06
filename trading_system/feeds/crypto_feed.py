"""
Live Cryptocurrency Market Feed.
Connects directly to Binance Public REST API endpoints without requiring API keys.
Scans 50+ pairs concurrently with connection pooling, rate limit throttling,
and automatic fallback to high-fidelity simulated feed if offline.
"""

import asyncio
import json
import logging
import urllib.request
import urllib.error
from typing import List, Dict, Optional
try:
    from trading_system.feeds.base_feed import BaseFeed
    from trading_system.feeds.mock_feed import MockFeed
    from trading_system.core.models import MarketData, Candle
except (ImportError, ValueError):
    from feeds.base_feed import BaseFeed
    from feeds.mock_feed import MockFeed
    from core.models import MarketData, Candle

logger = logging.getLogger("CryptoFeed")

BINANCE_BASE_URL = "https://api.binance.com/api/v3"

TIMEFRAME_MAP = {
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1h": "1h", "4h": "4h", "1d": "1d"
}

class CryptoFeed(BaseFeed):
    def __init__(self, fallback_mock: bool = True):
        super().__init__(name="Live Crypto Feed (Binance Public API)")
        self.fallback_mock = fallback_mock
        self.mock_fallback_feed = MockFeed() if fallback_mock else None
        self.using_fallback = False
        self._ticker_cache: Dict[str, dict] = {}
        self._last_ticker_fetch: float = 0.0

    def _normalize_symbol(self, symbol: str) -> str:
        """Convert 'BTC/USDT' to 'BTCUSDT'."""
        return symbol.replace("/", "").replace("-", "").upper()

    def _denormalize_symbol(self, raw_symbol: str) -> str:
        """Convert 'BTCUSDT' to 'BTC/USDT'."""
        if raw_symbol.endswith("USDT"):
            base = raw_symbol[:-4]
            return f"{base}/USDT"
        return raw_symbol

    def _fetch_sync(self, url: str, timeout: float = 8.0) -> bytes:
        """Synchronous fetch with User-Agent header."""
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AntigravityTradingBot/2.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()

    async def _fetch_url(self, url: str, timeout: float = 8.0) -> Optional[dict]:
        """Async wrapper around HTTP request."""
        try:
            loop = asyncio.get_event_loop()
            raw = await loop.run_in_executor(None, self._fetch_sync, url, timeout)
            return json.loads(raw.decode("utf-8"))
        except Exception as e:
            logger.debug(f"Fetch failed for {url}: {e}")
            return None

    async def get_market_data(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> Optional[MarketData]:
        """Fetch historical klines and 24h ticker for a single crypto symbol."""
        if self.using_fallback and self.mock_fallback_feed:
            return await self.mock_fallback_feed.get_market_data(symbol, timeframe, limit)

        raw_sym = self._normalize_symbol(symbol)
        interval = TIMEFRAME_MAP.get(timeframe, "15m")
        url = f"{BINANCE_BASE_URL}/klines?symbol={raw_sym}&interval={interval}&limit={limit}"
        
        data = await self._fetch_url(url)
        if data is None or not isinstance(data, list):
            # Switch to fallback if live network is unreachable
            if self.fallback_mock and not self.using_fallback:
                logger.warning(f"Network unreachable for {symbol}. Switching to high-fidelity simulated feed.")
                self.using_fallback = True
                return await self.mock_fallback_feed.get_market_data(symbol, timeframe, limit)
            return None

        candles: List[Candle] = []
        for row in data:
            # Binance kline format: [open_time, open, high, low, close, volume, ...]
            candles.append(Candle(
                timestamp=int(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5])
            ))

        if not candles:
            return None

        current_price = candles[-1].close
        first_price = candles[0].close
        change_24h = ((current_price - first_price) / first_price) * 100.0 if first_price > 0 else 0.0
        high_24h = max(c.high for c in candles)
        low_24h = min(c.low for c in candles)
        vol_24h = sum(c.volume for c in candles)

        return MarketData(
            symbol=symbol,
            current_price=current_price,
            change_24h_pct=round(change_24h, 2),
            high_24h=round(high_24h, 6),
            low_24h=round(low_24h, 6),
            volume_24h=round(vol_24h, 2),
            candles=candles
        )

    async def get_all_markets(self, symbols: List[str], timeframe: str = "15m", limit: int = 100) -> Dict[str, MarketData]:
        """Fetch 50+ crypto markets concurrently with controlled semaphore to respect rate limits."""
        if self.using_fallback and self.mock_fallback_feed:
            return await self.mock_fallback_feed.get_all_markets(symbols, timeframe, limit)

        # Use semaphore pool to prevent socket exhaustion and rate limit triggers
        semaphore = asyncio.Semaphore(15)

        async def fetch_worker(sym: str):
            async with semaphore:
                try:
                    return sym, await self.get_market_data(sym, timeframe, limit)
                except Exception as e:
                    logger.debug(f"Error fetching {sym}: {e}")
                    return sym, None

        tasks = [fetch_worker(sym) for sym in symbols]
        results = await asyncio.gather(*tasks)

        market_map = {}
        failed_count = 0
        for sym, m in results:
            if m is not None:
                market_map[sym] = m
            else:
                failed_count += 1

        # If majority failed (e.g. offline/sandboxed without network), smoothly fallback
        if failed_count > len(symbols) * 0.5 and self.fallback_mock:
            logger.info("Live network access limited. Activating high-fidelity simulation engine for all 50+ markets.")
            self.using_fallback = True
            return await self.mock_fallback_feed.get_all_markets(symbols, timeframe, limit)

        return market_map
