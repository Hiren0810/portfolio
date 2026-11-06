"""
Risk Management and Capital Allocation Engine.
Protects trading capital through dynamic ATR stops, trailing stops,
position sizing limits, maximum concurrent exposure, and drawdown circuit breakers.
"""

from typing import Tuple, Optional
try:
    from trading_system.config.settings import RiskSettings
    from trading_system.core.models import Position, OrderSide, AccountSummary
except (ImportError, ValueError):
    from config.settings import RiskSettings
    from core.models import Position, OrderSide, AccountSummary

class RiskManager:
    def __init__(self, settings: Optional[RiskSettings] = None):
        self.settings = settings or RiskSettings()
        self.circuit_breaker_tripped: bool = False
        self.day_start_equity: float = self.settings.initial_capital

    def reset_daily_baseline(self, current_equity: float):
        """Reset starting baseline at the start of a new trading session."""
        self.day_start_equity = current_equity
        self.circuit_breaker_tripped = False

    def check_circuit_breaker(self, current_equity: float) -> bool:
        """
        Check if daily drawdown exceeded maximum threshold.
        If tripped, all new trade entries are prohibited.
        """
        if self.day_start_equity <= 0:
            return False
            
        drawdown_pct = (self.day_start_equity - current_equity) / self.day_start_equity
        if drawdown_pct >= self.settings.max_daily_drawdown_pct:
            self.circuit_breaker_tripped = True
            return True
            
        return False

    def can_open_position(self, account: AccountSummary, current_open_count: int, symbol: str, active_symbols: list) -> Tuple[bool, str]:
        """Verify whether risk rules permit opening a new position."""
        # 1. Circuit breaker check
        if self.check_circuit_breaker(account.total_equity):
            return False, f"Daily Drawdown Circuit Breaker active (Limit: {self.settings.max_daily_drawdown_pct * 100:.1f}%)"

        # 2. Max open positions check
        if current_open_count >= self.settings.max_open_positions:
            return False, f"Maximum open positions limit reached ({current_open_count}/{self.settings.max_open_positions})"

        # 3. Duplicate market check (no doubling up on same market)
        if symbol in active_symbols:
            return False, f"Position already open for {symbol}"

        # 4. Total portfolio exposure check
        if account.total_equity > 0:
            current_exposure_pct = account.allocated_margin / account.total_equity
            if current_exposure_pct >= self.settings.max_portfolio_exposure_pct:
                return False, f"Max portfolio exposure reached ({current_exposure_pct*100:.1f}% >= {self.settings.max_portfolio_exposure_pct*100:.1f}%)"

        # 5. Minimum free cash balance check
        min_cash_required = account.total_equity * 0.05
        if account.cash_balance < min_cash_required:
            return False, f"Insufficient free cash reserves (${account.cash_balance:.2f} < ${min_cash_required:.2f})"

        return True, "OK"

    def calculate_stops(self, side: OrderSide, entry_price: float, atr: float) -> Tuple[float, float]:
        """
        Calculate dynamic ATR-based Stop Loss and Take Profit levels.
        Reward-to-risk ratio is enforced (default 2:1).
        """
        atr_stop_distance = max(atr * self.settings.stop_loss_atr_multiplier, entry_price * 0.005)
        
        if side == OrderSide.BUY:
            stop_loss = entry_price - atr_stop_distance
            risk_distance = entry_price - stop_loss
            take_profit = entry_price + (risk_distance * self.settings.take_profit_rr_ratio)
        else: # SHORT / SELL
            stop_loss = entry_price + atr_stop_distance
            risk_distance = stop_loss - entry_price
            take_profit = entry_price - (risk_distance * self.settings.take_profit_rr_ratio)
            
        return round(stop_loss, 6), round(take_profit, 6)

    def calculate_position_size(self, account_equity: float, available_cash: float, entry_price: float, stop_loss: float) -> float:
        """
        Calculate risk-adjusted position size (fractional quantity).
        Risk Amount = Equity * RiskPerTradePct (e.g. 1.5%).
        Quantity = Risk Amount / |Entry - StopLoss|.
        Capped by max single position allocation and available cash.
        """
        if entry_price <= 0:
            return 0.0

        risk_amount = account_equity * self.settings.risk_per_trade_pct
        stop_distance = abs(entry_price - stop_loss)
        
        if stop_distance <= 0:
            stop_distance = entry_price * 0.02  # 2% default fallback
            
        raw_quantity = risk_amount / stop_distance
        
        # Enforce maximum position size in USD/USDT
        max_position_cost = account_equity * self.settings.max_position_size_pct
        cash_adjusted_cost = min(max_position_cost, available_cash * 0.95) # 5% buffer for fees
        
        max_quantity_by_capital = cash_adjusted_cost / entry_price
        final_quantity = min(raw_quantity, max_quantity_by_capital)
        
        return round(final_quantity, 6)

    def update_trailing_stop(self, position: Position) -> bool:
        """
        Update position stop loss dynamically if trailing stop conditions are met.
        Returns True if stop loss was modified.
        """
        if not self.settings.trailing_stop_enabled:
            return False

        modified = False
        if position.side == OrderSide.BUY:
            # Check activation threshold (e.g. profit >= +1.5%)
            gain_pct = (position.current_price - position.entry_price) / position.entry_price
            if gain_pct >= self.settings.trailing_stop_activation_pct:
                position.trailing_stop_active = True
                
            if position.trailing_stop_active:
                # Trail by configured distance from peak high
                candidate_stop = position.peak_price * (1.0 - self.settings.trailing_stop_distance_pct)
                if candidate_stop > position.stop_loss:
                    position.stop_loss = round(candidate_stop, 6)
                    modified = True
        else: # SHORT
            gain_pct = (position.entry_price - position.current_price) / position.entry_price
            if gain_pct >= self.settings.trailing_stop_activation_pct:
                position.trailing_stop_active = True
                
            if position.trailing_stop_active:
                candidate_stop = position.peak_price * (1.0 + self.settings.trailing_stop_distance_pct)
                if candidate_stop < position.stop_loss:
                    position.stop_loss = round(candidate_stop, 6)
                    modified = True

        return modified

    def evaluate_exit(self, position: Position) -> Optional[str]:
        """
        Evaluate if current price violates Stop Loss or reaches Take Profit.
        Returns 'STOP_LOSS', 'TAKE_PROFIT', or None.
        """
        if position.side == OrderSide.BUY:
            if position.current_price <= position.stop_loss:
                return "STOP_LOSS"
            if position.current_price >= position.take_profit:
                return "TAKE_PROFIT"
        else: # SHORT
            if position.current_price >= position.stop_loss:
                return "STOP_LOSS"
            if position.current_price <= position.take_profit:
                return "TAKE_PROFIT"
                
        return None
