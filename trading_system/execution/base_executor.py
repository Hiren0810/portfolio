"""
Abstract base executor interface.
Defines methods for order execution, position tracking, and account querying.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
try:
    from trading_system.core.models import Order, Position, Signal, AccountSummary, MarketData
except (ImportError, ValueError):
    from core.models import Order, Position, Signal, AccountSummary, MarketData

class BaseExecutor(ABC):
    @abstractmethod
    def execute_signal(self, signal: Signal, current_equity: float) -> Optional[Order]:
        """Process incoming signal and dispatch trade order."""
        pass

    @abstractmethod
    def update_markets(self, markets: Dict[str, MarketData]):
        """Update open positions mark-to-market and check stop/profit exits."""
        pass

    @abstractmethod
    def get_open_positions(self) -> List[Position]:
        """Return all currently open positions."""
        pass

    @abstractmethod
    def get_account_summary(self) -> AccountSummary:
        """Return current account balance, equity, and performance stats."""
        pass

    @abstractmethod
    def close_position(self, position_id: str, reason: str = "MANUAL_CLOSE") -> Optional[Position]:
        """Manually close an open position."""
        pass

    @abstractmethod
    def close_all_positions(self, reason: str = "EMERGENCY_CLOSE") -> List[Position]:
        """Close all open positions immediately."""
        pass
