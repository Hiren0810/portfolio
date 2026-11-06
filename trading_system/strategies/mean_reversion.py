"""
Mean Reversion & Oversold Bounce Strategy.
Capitalizes on extreme statistical stretching away from mean prices.
Triggers long when RSI is severely oversold (< 28) and price touches lower Bollinger Band,
and short/take-profit when RSI > 72 at upper band.
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

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, risk_manager: Optional[RiskManager] = None):
        super().__init__(name="Mean Reversion", risk_manager=risk_manager)

    def evaluate(self, market: MarketData, indicators: IndicatorValues) -> Optional[Signal]:
        price = market.current_price
        if price <= 0 or not market.candles:
            return None

        # Oversold Reversal Setup: RSI < 28 and Price at or below lower Bollinger Band (%B <= 0.08)
        if indicators.rsi <= 28.0 and indicators.bb_percent_b <= 0.08:
            reasons = [
                f"Extreme Oversold RSI ({indicators.rsi:.1f} <= 28.0)",
                f"Price piercing Lower Bollinger Band (%B: {indicators.bb_percent_b:.2f})",
                "High statistical probability of snapback to 20-SMA"
            ]
            # In mean reversion, target is 20-SMA / BB middle
            take_profit = indicators.bb_middle
            stop_loss = price - (indicators.atr * 1.5)
            
            return Signal(
                symbol=market.symbol,
                direction=SignalDirection.BUY,
                confluence_score=75.0,
                strategy=self.name,
                current_price=price,
                suggested_stop_loss=round(stop_loss, 6),
                suggested_take_profit=round(take_profit, 6),
                reasons=reasons,
                indicators=indicators
            )

        # Overbought Reversal Setup: RSI >= 72 and Price at or above upper Bollinger Band (%B >= 0.92)
        if indicators.rsi >= 72.0 and indicators.bb_percent_b >= 0.92:
            reasons = [
                f"Extreme Overbought RSI ({indicators.rsi:.1f} >= 72.0)",
                f"Price touching Upper Bollinger Band (%B: {indicators.bb_percent_b:.2f})",
                "Mean reversion exhaustion pattern"
            ]
            take_profit = indicators.bb_middle
            stop_loss = price + (indicators.atr * 1.5)
            
            return Signal(
                symbol=market.symbol,
                direction=SignalDirection.SELL,
                confluence_score=-75.0,
                strategy=self.name,
                current_price=price,
                suggested_stop_loss=round(stop_loss, 6),
                suggested_take_profit=round(take_profit, 6),
                reasons=reasons,
                indicators=indicators
            )

        return None
