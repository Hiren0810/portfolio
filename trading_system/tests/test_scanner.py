"""
Unit tests for Asynchronous Multi-Market Scanner Engine.
Validates concurrent scanning across 50+ markets simultaneously.
"""

import unittest
import asyncio
import time
import os
from trading_system.config.settings import SystemSettings, ScannerSettings
from trading_system.scanner.engine import ScannerEngine

class TestScannerEngine(unittest.TestCase):
    def setUp(self):
        self.settings = SystemSettings(
            mode="paper",
            feed_type="mock",
            dashboard_enabled=False
        )
        self.settings.scanner.default_market_count = 55
        self.settings.scanner.scan_interval_seconds = 60

    def test_concurrent_scan_50_plus_markets(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        engine = ScannerEngine(
            settings=self.settings,
            market_count=55,
            asset_class="crypto"
        )

        start_t = time.time()
        state = loop.run_until_complete(engine.scan_once())
        duration = time.time() - start_t
        loop.close()

        # Assert all 50+ markets were scanned concurrently
        self.assertEqual(state["total_markets_scanned"], 55)
        self.assertEqual(len(state["markets"]), 55)
        
        # Verify that parallel execution completed fast (typically < 3.0s)
        self.assertLess(duration, 5.0, f"Scanning 55 markets took {duration:.2f}s, expected < 5.0s")
        
        # Verify market matrix attributes
        first_market = state["markets"][0]
        self.assertIn("symbol", first_market)
        self.assertIn("price", first_market)
        self.assertIn("rsi", first_market)
        self.assertIn("macd_hist", first_market)
        self.assertIn("confluence_score", first_market)
        self.assertIn("action", first_market)

if __name__ == "__main__":
    unittest.main()
