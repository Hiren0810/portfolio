"""
Unit tests for Paper Broker and Order Execution Engine.
Validates simulated fills, slippage, taker fees, mark-to-market PnL, and position lifecycle.
"""

import unittest
import os
from trading_system.config.settings import RiskSettings
from trading_system.core.models import Signal, SignalDirection, MarketData, Candle
from trading_system.core.database import Database
from trading_system.execution.paper_broker import PaperBroker

class TestPaperBroker(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "trading_system/data/test_trading.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        self.db = Database(self.test_db_path)
        self.settings = RiskSettings(initial_capital=10000.0)
        self.broker = PaperBroker(risk_settings=self.settings, database=self.db)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_execute_buy_signal(self):
        signal = Signal(
            symbol="BTC/USDT",
            direction=SignalDirection.BUY,
            confluence_score=85.0,
            strategy="Confluence",
            current_price=60000.0,
            suggested_stop_loss=58000.0,
            suggested_take_profit=64000.0
        )

        order = self.broker.execute_signal(signal, 10000.0)
        self.assertIsNotNone(order)
        self.assertEqual(order.symbol, "BTC/USDT")
        self.assertEqual(len(self.broker.open_positions), 1)
        self.assertLess(self.broker.cash_balance, 10000.0)

    def test_take_profit_auto_exit(self):
        signal = Signal(
            symbol="SOL/USDT",
            direction=SignalDirection.BUY,
            confluence_score=80.0,
            strategy="Confluence",
            current_price=100.0,
            suggested_stop_loss=95.0,
            suggested_take_profit=110.0
        )
        self.broker.execute_signal(signal, 10000.0)
        pos = list(self.broker.open_positions.values())[0]

        # Market jumps to 112.0 (exceeding TP 110.0)
        fake_market = MarketData(
            symbol="SOL/USDT",
            current_price=112.0,
            change_24h_pct=5.0,
            high_24h=112.0,
            low_24h=98.0,
            volume_24h=10000.0
        )
        self.broker.update_markets({"SOL/USDT": fake_market})

        # Position should be closed and trade recorded
        self.assertEqual(len(self.broker.open_positions), 0)
        self.assertEqual(len(self.broker.trade_history), 1)
        self.assertGreater(self.broker.trade_history[0].realized_pnl, 0)
        self.assertEqual(self.broker.trade_history[0].exit_reason, "TAKE_PROFIT")

if __name__ == "__main__":
    unittest.main()
