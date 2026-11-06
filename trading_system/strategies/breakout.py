"""
Volatility Squeeze & Breakout Strategy.
Detects Bollinger Band squeeze / contraction followed by explosive breakouts
supported by volume surge and expanding ATR.
"""

from typing import Optional
try:
    from trading_system.strategies.base_strategy import BaseStrategy
    from trading_system.core.models import MarketData, IndicatorValues, Signal, SignalDirection, OrderSide
    from trading_system.core.risk_manager import RiskManager
except (ImportError, ValueError):
    from strategies.base_strategy import BaseStrategy
    from core.models import MarketData, IndicatorValues, Signal, SignalDirection, OrderSide
    from core.risk_manager import RiskManager

class BreakoutStrategy(BaseStrategy):
    def __init__(self, risk_manager: Optional[RiskManager] = None):
        super().__init__(name="Volatility Breakout", risk_manager=risk_manager)

    def evaluate(self, market: MarketData, indicators: IndicatorValues) -> Optional[Signal]:
        price = market.current_price
        if price <= 0 or not market.candles:
            return None

        # Squeeze condition: Bollinger bandwidth relatively narrow (< 6.0%)
        is_squeeze = indicators.bb_bandwidth < 6.0
        
        # Bullish Breakout: Price crosses above Upper BB with strong volume
        if indicators.bb_percent_b >= 1.0 and indicators.volume_ratio >= 1.6:
            reasons = [
                f"Breakout above Upper Bollinger Band (%B: {indicators.bb_percent_b:.2f})",
                f"Volume surge {indicators.volume_ratio:.1f}x of 20-SMA",
                f"Bandwidth expansion ({indicators.bb_bandwidth:.1f}%)"
            ]
            if is_squeeze:
                reasons.append("Preceded by low-volatility squeeze")
                
            stop_loss, take_profit = self.risk_manager.calculate_stops(OrderSide.BUY, price, indicators.atr)
            return Signal(
                symbol=market.symbol,
                direction=SignalDirection.BUY,
                confluence_score=80.0 if is_squeeze else 70.0,
                strategy=self.name,
                current_price=price,
                suggested_stop_loss=stop_loss,
                suggested_take_profit=take_profit,
                reasons=reasons,
                indicators=indicators
            )

        # Bearish Breakdown: Price crosses below Lower BB with volume
        if indicators.bb_percent_b <= 0.0 and indicators.volume_ratio >= 1.6:
            reasons = [
                f"Breakdown below Lower Bollinger Band (%B: {indicators.bb_percent_b:.2f})",
                f"Volume expansion {indicators.volume_ratio:.1f}x",
                f"Bandwidth: {indicators.bb_bandwidth:.1f}%"
            ]
            stop_loss, take_profit = self.risk_manager.calculate_stops(OrderSide.SELL, price, indicators.atr)
            return Signal(
                symbol=market.symbol,
                direction=SignalDirection.SELL,
                confluence_score=-75.0,
                strategy=self.name,
                current_price=price,
                suggested_stop_loss=stop_loss,
                suggested_take_profit=take_profit,
                reasons=reasons,
                indicators=indicators
            )

        return None
