"""
Abstract base strategy class.
Defines interface for multi-market signal generation.
"""

from abc import ABC, abstractmethod
from typing import Optional
try:
    from trading_system.core.models import MarketData, IndicatorValues, Signal
    from trading_system.core.risk_manager import RiskManager
except (ImportError, ValueError):
    from core.models import MarketData, IndicatorValues, Signal
    from core.risk_manager import RiskManager

class BaseStrategy(ABC):
    def __init__(self, name: str, risk_manager: Optional[RiskManager] = None):
        self.name = name
        self.risk_manager = risk_manager or RiskManager()

    @abstractmethod
    def evaluate(self, market: MarketData, indicators: IndicatorValues) -> Optional[Signal]:
        """
        Evaluate market conditions and indicator values.
        Returns a Signal if conditions align with strategy criteria, or None.
        """
        pass
