"""
High-fidelity simulated multi-market data feed.
Generates realistic geometric Brownian motion, volatility jumps, and volume bursts
for 50+ markets with zero external network dependencies.
"""

import asyncio
import math
import random
import time
from typing import List, Dict, Optional
try:
    from trading_system.feeds.base_feed import BaseFeed
    from trading_system.core.models import MarketData, Candle
except (ImportError, ValueError):
    from feeds.base_feed import BaseFeed
    from core.models import MarketData, Candle

# Realistic benchmark starting prices
BASE_PRICES = {
    "BTC/USDT": 67450.0, "ETH/USDT": 3480.0, "SOL/USDT": 182.5, "BNB/USDT": 592.0,
    "XRP/USDT": 0.58, "DOGE/USDT": 0.145, "ADA/USDT": 0.42, "AVAX/USDT": 28.5,
    "LINK/USDT": 14.8, "SUI/USDT": 2.15, "NEAR/USDT": 5.4, "APT/USDT": 8.9,
    "INJ/USDT": 24.3, "DOT/USDT": 5.1, "PEPE/USDT": 0.0000105, "SHIB/USDT": 0.0000185,
    "ARB/USDT": 0.62, "OP/USDT": 1.75, "TIA/USDT": 6.2, "RENDER/USDT": 6.8,
    "FET/USDT": 1.45, "FIL/USDT": 4.2, "KAS/USDT": 0.15, "ATOM/USDT": 5.2,
    "LTC/USDT": 73.0, "BCH/USDT": 365.0, "UNI/USDT": 8.4, "ICP/USDT": 9.1,
    "STX/USDT": 1.95, "SEI/USDT": 0.48, "BONK/USDT": 0.000024, "WIF/USDT": 2.65,
    "FLOKI/USDT": 0.00016, "JUP/USDT": 1.08, "PYTH/USDT": 0.38, "AAVE/USDT": 162.0,
    "MKR/USDT": 1450.0, "RUNE/USDT": 5.8, "GRT/USDT": 0.18, "IMX/USDT": 1.55,
    "THETA/USDT": 1.42, "FTM/USDT": 0.72, "ALGO/USDT": 0.14, "SAND/USDT": 0.31,
    "MANA/USDT": 0.34, "AXS/USDT": 5.2, "GALA/USDT": 0.024, "CHZ/USDT": 0.075,
    "EOS/USDT": 0.52, "CRV/USDT": 0.32, "LDO/USDT": 1.25, "DYDX/USDT": 1.15,
    "PENDLE/USDT": 4.6, "ENA/USDT": 0.42, "ONDO/USDT": 0.82, "WLD/USDT": 2.1,
    "NOT/USDT": 0.008, "BLUR/USDT": 0.28, "STRK/USDT": 0.45, "TON/USDT": 5.8,
    "MATIC/USDT": 0.44, "ENS/USDT": 18.2, "NEO/USDT": 11.5, "QNT/USDT": 78.0,
    "FLOW/USDT": 0.62,
    # Equities fallback
    "AAPL": 225.0, "MSFT": 430.0, "NVDA": 135.0, "GOOGL": 178.0, "AMZN": 195.0,
    "META": 580.0, "TSLA": 250.0, "BRK.B": 460.0, "LLY": 890.0, "AVGO": 175.0,
    "JPM": 220.0, "V": 280.0, "UNH": 580.0, "XOM": 120.0, "MA": 490.0,
    "JNJ": 160.0, "PG": 170.0, "HD": 395.0, "COST": 895.0, "ABBV": 195.0
}

class MockFeed(BaseFeed):
    def __init__(self, seed: Optional[int] = 42):
        super().__init__(name="High-Fidelity Simulation Feed")
        self.rng = random.Random(seed)
        self.market_cache: Dict[str, MarketData] = {}
        self.trends: Dict[str, float] = {}

    def _get_base_price(self, symbol: str) -> float:
        if symbol in BASE_PRICES:
            return BASE_PRICES[symbol]
        # Hash-based deterministic price generator for unknown symbols
        h = abs(hash(symbol)) % 1000 + 10
        return float(h)

    def _generate_history(self, symbol: str, limit: int = 100, timeframe_seconds: int = 900) -> MarketData:
        base_price = self._get_base_price(symbol)
        
        # Assign persistent trend momentum to market (-0.0005 to +0.0008)
        if symbol not in self.trends:
            self.trends[symbol] = self.rng.uniform(-0.0004, 0.0007)
        trend = self.trends[symbol]

        volatility = 0.008 if "BTC" in symbol or "ETH" in symbol else 0.018

        now_ms = int(time.time() * 1000)
        candles: List[Candle] = []
        price = base_price * (1.0 - (trend * limit))

        for i in range(limit):
            t_ms = now_ms - ((limit - i) * timeframe_seconds * 1000)
            
            # Geometric Brownian step with trend and random volatility
            shock = self.rng.gauss(0, 1)
            ret = trend + (volatility * shock)
            
            open_p = price
            close_p = max(0.000001, price * (1.0 + ret))
            
            high_wick = abs(self.rng.gauss(0, volatility * 0.5))
            low_wick = abs(self.rng.gauss(0, volatility * 0.5))
            high_p = max(open_p, close_p) * (1.0 + high_wick)
            low_p = min(open_p, close_p) * (1.0 - low_wick)
            
            # Base volume with occasional surges
            base_vol = 100000.0 / (close_p if close_p > 1 else 1.0)
            surge = 2.5 if abs(ret) > volatility * 1.5 else 1.0
            volume = base_vol * self.rng.uniform(0.6, 1.4) * surge
            
            candles.append(Candle(
                timestamp=t_ms,
                open=round(open_p, 6),
                high=round(high_p, 6),
                low=round(low_p, 6),
                close=round(close_p, 6),
                volume=round(volume, 2)
            ))
            price = close_p

        first_close = candles[0].close
        last_close = candles[-1].close
        change_24h = ((last_close - first_close) / first_close) * 100.0
        high_24h = max(c.high for c in candles)
        low_24h = min(c.low for c in candles)
        vol_24h = sum(c.volume for c in candles)

        market = MarketData(
            symbol=symbol,
            current_price=last_close,
            change_24h_pct=round(change_24h, 2),
            high_24h=round(high_24h, 6),
            low_24h=round(low_24h, 6),
            volume_24h=round(vol_24h, 2),
            candles=candles,
            timestamp=time.time()
        )
        self.market_cache[symbol] = market
        return market

    async def get_market_data(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> Optional[MarketData]:
        if symbol not in self.market_cache:
            return self._generate_history(symbol, limit)

        # Update latest candle with micro-tick
        market = self.market_cache[symbol]
        trend = self.trends.get(symbol, 0.0002)
        volatility = 0.004
        
        shock = self.rng.gauss(0, 1)
        ret = (trend * 0.2) + (volatility * shock)
        new_price = max(0.000001, market.current_price * (1.0 + ret))
        
        # Update latest candle
        if market.candles:
            last_c = market.candles[-1]
            last_c.close = round(new_price, 6)
            last_c.high = max(last_c.high, new_price)
            last_c.low = min(last_c.low, new_price)
            last_c.volume += self.rng.uniform(10.0, 100.0)

        market.current_price = round(new_price, 6)
        market.high_24h = max(market.high_24h, new_price)
        market.low_24h = min(market.low_24h, new_price)
        market.timestamp = time.time()
        
        return market

    async def get_all_markets(self, symbols: List[str], timeframe: str = "15m", limit: int = 100) -> Dict[str, MarketData]:
        # Fast concurrent update
        tasks = [self.get_market_data(sym, timeframe, limit) for sym in symbols]
        results = await asyncio.gather(*tasks)
        return {sym: m for sym, m in zip(symbols, results) if m is not None}
