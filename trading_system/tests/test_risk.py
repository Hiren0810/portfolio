"""
Unit tests for Risk Management Engine.
Validates position sizing formulas, drawdown limits, trailing stops, and circuit breakers.
"""

import unittest
from trading_system.config.settings import RiskSettings
from trading_system.core.models import OrderSide, Position, PositionStatus, AccountSummary
from trading_system.core.risk_manager import RiskManager

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.settings = RiskSettings(
            initial_capital=10000.0,
            risk_per_trade_pct=0.015,   # $150 risk
            max_open_positions=3,
            max_daily_drawdown_pct=0.03 # $300 drawdown halts trading
        )
        self.risk_manager = RiskManager(self.settings)

    def test_position_sizing(self):
        # Allow sufficient single position size (e.g. 40%) to test unconstrained risk sizing
        self.risk_manager.settings.max_position_size_pct = 0.40
        # Entry $100, Stop Loss $95 -> $5 risk per unit
        # Equity $10,000 * 1.5% = $150 risk amount
        # Quantity = 150 / 5 = 30 units
        qty = self.risk_manager.calculate_position_size(
            account_equity=10000.0,
            available_cash=8000.0,
            entry_price=100.0,
            stop_loss=95.0
        )
        self.assertAlmostEqual(qty, 30.0, places=2)

        # Now test that max_position_size_pct constraint (e.g. 20% = $2,000) caps the order at 20 units
        self.risk_manager.settings.max_position_size_pct = 0.20
        capped_qty = self.risk_manager.calculate_position_size(
            account_equity=10000.0,
            available_cash=8000.0,
            entry_price=100.0,
            stop_loss=95.0
        )
        self.assertAlmostEqual(capped_qty, 20.0, places=2)

    def test_max_positions_limit(self):
        account = AccountSummary(total_equity=10000.0, cash_balance=5000.0, allocated_margin=5000.0, unrealized_pnl=0.0, realized_pnl=0.0)
        # When current count equals max (3), should be rejected
        allowed, reason = self.risk_manager.can_open_position(
            account=account,
            current_open_count=3,
            symbol="SOL/USDT",
            active_symbols=["BTC/USDT", "ETH/USDT", "BNB/USDT"]
        )
        self.assertFalse(allowed)
        self.assertIn("limit reached", reason)

    def test_duplicate_symbol_rejection(self):
        account = AccountSummary(total_equity=10000.0, cash_balance=8000.0, allocated_margin=2000.0, unrealized_pnl=0.0, realized_pnl=0.0)
        allowed, reason = self.risk_manager.can_open_position(
            account=account,
            current_open_count=1,
            symbol="BTC/USDT",
            active_symbols=["BTC/USDT"]
        )
        self.assertFalse(allowed)
        self.assertIn("already open", reason)

    def test_circuit_breaker(self):
        # 4% loss on $10,000 -> $9,600 equity
        self.assertTrue(self.risk_manager.check_circuit_breaker(9600.0))
        self.assertTrue(self.risk_manager.circuit_breaker_tripped)

        account = AccountSummary(total_equity=9600.0, cash_balance=9600.0, allocated_margin=0.0, unrealized_pnl=0.0, realized_pnl=-400.0)
        allowed, reason = self.risk_manager.can_open_position(
            account=account,
            current_open_count=0,
            symbol="ETH/USDT",
            active_symbols=[]
        )
        self.assertFalse(allowed)
        self.assertIn("Circuit Breaker", reason)

    def test_trailing_stop_movement(self):
        pos = Position(
            symbol="ETH/USDT",
            side=OrderSide.BUY,
            entry_price=3000.0,
            current_price=3000.0,
            quantity=1.0,
            stop_loss=2900.0,
            take_profit=3300.0
        )

        # Price rises by +2% (above 1.5% activation)
        pos.update_price(3060.0)
        updated = self.risk_manager.update_trailing_stop(pos)
        self.assertTrue(updated)
        self.assertTrue(pos.trailing_stop_active)
        # New stop trailed by 1.0% from peak ($3060 * 0.99 = $3029.4)
        self.assertAlmostEqual(pos.stop_loss, 3029.4, places=1)

if __name__ == "__main__":
    unittest.main()
