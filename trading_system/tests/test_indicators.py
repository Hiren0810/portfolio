"""
Unit tests for technical indicators calculation engine.
Validates mathematical properties of EMA, SMA, RSI, MACD, Bollinger Bands, and ATR.
"""

import unittest
from trading_system.core.models import Candle
from trading_system.core.indicators import (
    calculate_sma, calculate_ema, calculate_rsi,
    calculate_macd, calculate_bollinger_bands, calculate_atr,
    compute_all_indicators
)

class TestIndicators(unittest.TestCase):
    def setUp(self):
        # Generate predictable synthetic candle sequence
        self.prices = [100.0 + i for i in range(50)]
        self.candles = [
            Candle(
                timestamp=1000 + i * 60,
                open=p - 0.5,
                high=p + 1.0,
                low=p - 1.0,
                close=p,
                volume=1000.0 + i * 10
            ) for i, p in enumerate(self.prices)
        ]

    def test_sma_calculation(self):
        sma_10 = calculate_sma(self.prices, 10)
        self.assertEqual(len(sma_10), len(self.prices) - 9)
        # Expected last 10 SMA: average of 140 to 149 = 144.5
        self.assertAlmostEqual(sma_10[-1], 144.5, places=4)

    def test_ema_calculation(self):
        ema_9 = calculate_ema(self.prices, 9)
        self.assertEqual(len(ema_9), len(self.prices) - 8)
        # In a monotonic upward trend, latest EMA should be close to latest price
        self.assertGreater(ema_9[-1], self.prices[30])

    def test_rsi_bounds(self):
        # Monotonically increasing prices should produce high RSI (> 80)
        rsi = calculate_rsi(self.prices, 14)
        self.assertGreater(rsi, 80.0)
        self.assertLessEqual(rsi, 100.0)

        # Monotonically decreasing prices should produce low RSI (< 20)
        decreasing = list(reversed(self.prices))
        rsi_down = calculate_rsi(decreasing, 14)
        self.assertLess(rsi_down, 20.0)
        self.assertGreaterEqual(rsi_down, 0.0)

    def test_macd_calculation(self):
        macd, signal, hist = calculate_macd(self.prices, 12, 26, 9)
        # In strong uptrend, MACD line should be positive
        self.assertGreater(macd, 0.0)

    def test_bollinger_bands(self):
        upper, mid, lower, pb, bw = calculate_bollinger_bands(self.prices, 20, 2.0)
        self.assertGreater(upper, mid)
        self.assertGreater(mid, lower)
        self.assertGreater(pb, 0.0)

    def test_atr(self):
        highs = [c.high for c in self.candles]
        lows = [c.low for c in self.candles]
        closes = [c.close for c in self.candles]
        atr = calculate_atr(highs, lows, closes, 14)
        self.assertGreater(atr, 0.0)

    def test_compute_all_indicators(self):
        ind = compute_all_indicators(self.candles)
        self.assertIsNotNone(ind)
        self.assertGreater(ind.rsi, 0.0)
        self.assertGreater(ind.ema_9, 0.0)
        self.assertIn(ind.trend_bias, ["STRONG_BULL", "BULLISH", "NEUTRAL", "BEARISH", "STRONG_BEAR"])

if __name__ == "__main__":
    unittest.main()
