"""
Multi-Indicator Confluence Strategy.
Combines EMA Trend Alignment, MACD Momentum, RSI pullback filters,
Bollinger Band positioning, and Volume confirmation into a composite score (-100 to +100).
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

class ConfluenceStrategy(BaseStrategy):
    def __init__(self, min_score: float = 65.0, risk_manager: Optional[RiskManager] = None):
        super().__init__(name="Multi-Indicator Confluence", risk_manager=risk_manager)
        self.min_score = min_score

    def evaluate(self, market: MarketData, indicators: IndicatorValues) -> Optional[Signal]:
        price = market.current_price
        if price <= 0 or not market.candles:
            return None

        bullish_score = 0.0
        bearish_score = 0.0
        bullish_reasons = []
        bearish_reasons = []

        # 1. EMA Trend Structure (Max 35 pts)
        if price > indicators.ema_9 > indicators.ema_21:
            bullish_score += 20.0
            bullish_reasons.append("Price > EMA9 > EMA21 (Bullish short-term ribbon)")
        elif price < indicators.ema_9 < indicators.ema_21:
            bearish_score += 20.0
            bearish_reasons.append("Price < EMA9 < EMA21 (Bearish short-term ribbon)")

        if indicators.ema_21 > indicators.ema_50:
            bullish_score += 10.0
            bullish_reasons.append("EMA21 > EMA50 (Medium-term bull trend)")
        elif indicators.ema_21 < indicators.ema_50:
            bearish_score += 10.0
            bearish_reasons.append("EMA21 < EMA50 (Medium-term bear trend)")

        if indicators.ema_200 > 0:
            if price > indicators.ema_200:
                bullish_score += 5.0
            else:
                bearish_score += 5.0

        # 2. MACD Momentum (Max 25 pts)
        if indicators.macd > indicators.macd_signal:
            bullish_score += 15.0
            bullish_reasons.append(f"MACD line above Signal ({indicators.macd:.4f} > {indicators.macd_signal:.4f})")
        else:
            bearish_score += 15.0
            bearish_reasons.append(f"MACD line below Signal ({indicators.macd:.4f} < {indicators.macd_signal:.4f})")

        if indicators.macd_hist > 0:
            bullish_score += 10.0
            bullish_reasons.append("MACD histogram positive")
        else:
            bearish_score += 10.0
            bearish_reasons.append("MACD histogram negative")

        # 3. RSI Momentum & Filter (Max 20 pts)
        rsi = indicators.rsi
        if 48.0 <= rsi <= 68.0:
            bullish_score += 20.0
            bullish_reasons.append(f"RSI healthy bullish continuation ({rsi:.1f})")
        elif 32.0 <= rsi < 48.0 and indicators.macd_hist > 0:
            bullish_score += 10.0
            bullish_reasons.append(f"RSI recovering with positive momentum ({rsi:.1f})")
        elif rsi > 75.0:
            bullish_score -= 20.0  # Overbought penalty
            bullish_reasons.append(f"RSI overbought warning ({rsi:.1f})")

        if 32.0 <= rsi <= 52.0:
            bearish_score += 20.0
            bearish_reasons.append(f"RSI bearish momentum ({rsi:.1f})")
        elif rsi < 25.0:
            bearish_score -= 20.0  # Oversold penalty for selling
            bearish_reasons.append(f"RSI oversold warning ({rsi:.1f})")

        # 4. Volume Surge Confirmation (Max 15 pts)
        if indicators.volume_ratio >= 1.5:
            bullish_score += 15.0
            bearish_score += 15.0
            bullish_reasons.append(f"Volume spike ({indicators.volume_ratio:.1f}x of 20-SMA)")
            bearish_reasons.append(f"High volume sell activity ({indicators.volume_ratio:.1f}x)")
        elif indicators.volume_ratio >= 1.1:
            bullish_score += 8.0
            bearish_score += 8.0

        # 5. Bollinger Bands Positioning (Max 10 pts)
        pb = indicators.bb_percent_b
        if 0.40 <= pb <= 0.88:
            bullish_score += 10.0
            bullish_reasons.append(f"BB %B optimal continuation ({pb:.2f})")
        elif pb > 1.02:
            bullish_score -= 10.0  # Piercing upper band

        if 0.12 <= pb <= 0.60:
            bearish_score += 10.0
            bearish_reasons.append(f"BB %B in lower band ({pb:.2f})")

        # Determine net confluence
        net_score = bullish_score - bearish_score
        
        # Clamp to [-100, 100]
        net_score = max(-100.0, min(100.0, net_score))

        direction = SignalDirection.HOLD
        reasons = []

        if net_score >= self.min_score:
            direction = SignalDirection.BUY
            reasons = bullish_reasons
            stop_loss, take_profit = self.risk_manager.calculate_stops(OrderSide.BUY, price, indicators.atr)
        elif net_score <= -self.min_score:
            direction = SignalDirection.SELL
            reasons = bearish_reasons
            stop_loss, take_profit = self.risk_manager.calculate_stops(OrderSide.SELL, price, indicators.atr)
        else:
            return None

        return Signal(
            symbol=market.symbol,
            direction=direction,
            confluence_score=round(net_score, 1),
            strategy=self.name,
            current_price=price,
            suggested_stop_loss=stop_loss,
            suggested_take_profit=take_profit,
            reasons=reasons,
            indicators=indicators
        )
