"""
High-fidelity simulated Paper Broker execution engine.
Simulates realistic order execution with slippage, taker commissions,
mark-to-market position tracking, dynamic trailing stops, and database logging.
"""

import time
import uuid
import logging
from typing import List, Dict, Optional
try:
    from trading_system.execution.base_executor import BaseExecutor
    from trading_system.core.models import (
        Order, OrderSide, OrderType, OrderStatus,
        Position, PositionStatus, Signal, SignalDirection,
        AccountSummary, TradeRecord, MarketData
    )
    from trading_system.core.risk_manager import RiskManager
    from trading_system.core.database import Database
    from trading_system.config.settings import RiskSettings
except (ImportError, ValueError):
    from execution.base_executor import BaseExecutor
    from core.models import (
        Order, OrderSide, OrderType, OrderStatus,
        Position, PositionStatus, Signal, SignalDirection,
        AccountSummary, TradeRecord, MarketData
    )
    from core.risk_manager import RiskManager
    from core.database import Database
    from config.settings import RiskSettings

logger = logging.getLogger("PaperBroker")

class PaperBroker(BaseExecutor):
    def __init__(self, risk_settings: Optional[RiskSettings] = None, database: Optional[Database] = None):
        self.risk_settings = risk_settings or RiskSettings()
        self.database = database or Database()
        self.risk_manager = RiskManager(self.risk_settings)

        self.cash_balance: float = self.risk_settings.initial_capital
        self.open_positions: Dict[str, Position] = {} # position_id -> Position
        self.position_fees: Dict[str, float] = {}     # position_id -> entry_fee
        self.trade_history: List[TradeRecord] = []
        self.total_realized_pnl: float = 0.0

        # Sync any existing historical statistics from DB
        stats = self.database.get_trade_statistics()
        self.total_realized_pnl = stats["total_net_pnl"]

    def get_account_summary(self) -> AccountSummary:
        """Calculate complete mark-to-market portfolio statistics."""
        allocated_margin = sum(p.entry_price * p.quantity for p in self.open_positions.values())
        unrealized_pnl = sum(p.unrealized_pnl for p in self.open_positions.values())
        total_equity = self.cash_balance + allocated_margin + unrealized_pnl

        # Performance stats
        stats = self.database.get_trade_statistics()
        
        return AccountSummary(
            total_equity=round(total_equity, 2),
            cash_balance=round(self.cash_balance, 2),
            allocated_margin=round(allocated_margin, 2),
            unrealized_pnl=round(unrealized_pnl, 2),
            realized_pnl=round(self.total_realized_pnl, 2),
            win_rate_pct=stats["win_rate_pct"],
            total_trades=stats["total_trades"],
            winning_trades=stats["winning_trades"],
            losing_trades=stats["losing_trades"],
            profit_factor=stats["profit_factor"]
        )

    def execute_signal(self, signal: Signal, current_equity: float) -> Optional[Order]:
        """Convert an actionable signal into an executed paper order."""
        if signal.direction == SignalDirection.HOLD:
            return None

        side = OrderSide.BUY if signal.direction == SignalDirection.BUY else OrderSide.SELL
        active_symbols = [p.symbol for p in self.open_positions.values()]
        
        # Risk management pre-trade checks
        account = self.get_account_summary()
        allowed, reason = self.risk_manager.can_open_position(
            account=account,
            current_open_count=len(self.open_positions),
            symbol=signal.symbol,
            active_symbols=active_symbols
        )

        if not allowed:
            logger.info(f"Signal for {signal.symbol} rejected by RiskManager: {reason}")
            return None

        # Position sizing
        quantity = self.risk_manager.calculate_position_size(
            account_equity=account.total_equity,
            available_cash=self.cash_balance,
            entry_price=signal.current_price,
            stop_loss=signal.suggested_stop_loss
        )

        if quantity <= 0:
            logger.info(f"Calculated zero quantity for {signal.symbol}, skipping.")
            return None

        # Realistic execution price with slippage
        slippage_mult = (1.0 + self.risk_settings.slippage_pct) if side == OrderSide.BUY else (1.0 - self.risk_settings.slippage_pct)
        fill_price = round(signal.current_price * slippage_mult, 6)
        notional_cost = fill_price * quantity
        fee = round(notional_cost * self.risk_settings.fee_rate_pct, 4)

        if self.cash_balance < (notional_cost + fee):
            logger.info(f"Insufficient cash to execute {signal.symbol}. Needed: ${notional_cost + fee:.2f}, Have: ${self.cash_balance:.2f}")
            return None

        # Create Order
        order = Order(
            symbol=signal.symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=quantity,
            price=fill_price,
            status=OrderStatus.FILLED,
            fee=fee,
            filled_at=time.time()
        )

        # Deduct cash & allocate position
        self.cash_balance -= (notional_cost + fee)
        
        position = Position(
            symbol=signal.symbol,
            side=side,
            entry_price=fill_price,
            current_price=fill_price,
            quantity=quantity,
            stop_loss=signal.suggested_stop_loss,
            take_profit=signal.suggested_take_profit,
            status=PositionStatus.OPEN,
            opened_at=time.time()
        )

        self.open_positions[position.position_id] = position
        self.position_fees[position.position_id] = fee

        # Persist signal to database
        self.database.record_signal(signal)
        
        logger.info(f"[ORDER FILLED] {side.value} {quantity:.4f} {signal.symbol} @ ${fill_price:.4f} | SL: ${signal.suggested_stop_loss:.4f} | TP: ${signal.suggested_take_profit:.4f}")
        return order

    def update_markets(self, markets: Dict[str, MarketData]):
        """
        Mark-to-market loop.
        Updates open positions with current prices, evaluates trailing stops,
        and triggers stop loss or take profit exits.
        """
        positions_to_close = []

        for pos_id, pos in list(self.open_positions.items()):
            market = markets.get(pos.symbol)
            if not market:
                continue

            current_price = market.current_price
            pos.update_price(current_price)

            # Check trailing stop upgrade
            self.risk_manager.update_trailing_stop(pos)

            # Check stop loss / take profit trigger
            exit_trigger = self.risk_manager.evaluate_exit(pos)
            if exit_trigger:
                positions_to_close.append((pos_id, exit_trigger, current_price))

        # Close triggered positions
        for pos_id, exit_reason, exit_price in positions_to_close:
            self._close_position_internal(pos_id, exit_price, exit_reason)

    def _close_position_internal(self, position_id: str, exit_price: float, reason: str) -> Optional[Position]:
        """Internal close helper calculating slippage, fees, and realized PnL."""
        pos = self.open_positions.get(position_id)
        if not pos:
            return None

        # Apply slippage on exit
        slippage_mult = (1.0 - self.risk_settings.slippage_pct) if pos.side == OrderSide.BUY else (1.0 + self.risk_settings.slippage_pct)
        final_exit_price = round(exit_price * slippage_mult, 6)

        gross_value = final_exit_price * pos.quantity
        exit_fee = round(gross_value * self.risk_settings.fee_rate_pct, 4)
        entry_fee = self.position_fees.get(position_id, 0.0)
        total_fees = entry_fee + exit_fee

        if pos.side == OrderSide.BUY:
            raw_pnl = (final_exit_price - pos.entry_price) * pos.quantity
        else: # SHORT
            raw_pnl = (pos.entry_price - final_exit_price) * pos.quantity

        net_realized_pnl = round(raw_pnl - total_fees, 2)
        pnl_pct = round((raw_pnl / (pos.entry_price * pos.quantity)) * 100.0, 2)

        # Return capital to cash balance: (initial entry cost + net pnl)
        initial_cost = pos.entry_price * pos.quantity
        self.cash_balance += (initial_cost + net_realized_pnl)
        self.total_realized_pnl += net_realized_pnl

        pos.status = PositionStatus.CLOSED
        pos.closed_at = time.time()
        pos.close_price = final_exit_price
        pos.close_reason = reason
        pos.realized_pnl = net_realized_pnl

        # Log TradeRecord
        trade = TradeRecord(
            trade_id=str(uuid.uuid4())[:8],
            symbol=pos.symbol,
            side=pos.side.value,
            entry_price=pos.entry_price,
            exit_price=final_exit_price,
            quantity=pos.quantity,
            realized_pnl=net_realized_pnl,
            pnl_pct=pnl_pct,
            fees=total_fees,
            opened_at=pos.opened_at,
            closed_at=pos.closed_at,
            duration_seconds=round(pos.closed_at - pos.opened_at, 1),
            exit_reason=reason
        )
        self.trade_history.append(trade)
        self.database.record_trade(trade)

        # Snapshot account equity
        self.database.record_equity_snapshot(self.get_account_summary())

        # Cleanup
        del self.open_positions[position_id]
        if position_id in self.position_fees:
            del self.position_fees[position_id]

        status_emoji = "🟢 WIN" if net_realized_pnl >= 0 else "🔴 LOSS"
        logger.info(f"[POSITION CLOSED - {status_emoji}] {pos.symbol} | PnL: ${net_realized_pnl:.2f} ({pnl_pct:+.2f}%) | Reason: {reason} | Exit: ${final_exit_price:.4f}")
        return pos

    def close_position(self, position_id: str, reason: str = "MANUAL_CLOSE") -> Optional[Position]:
        """Manually close an open position by ID."""
        pos = self.open_positions.get(position_id)
        if not pos:
            return None
        return self._close_position_internal(position_id, pos.current_price, reason)

    def close_all_positions(self, reason: str = "EMERGENCY_CLOSE") -> List[Position]:
        """Close all open positions immediately."""
        closed = []
        for pos_id in list(self.open_positions.keys()):
            pos = self.close_position(pos_id, reason)
            if pos:
                closed.append(pos)
        return closed

    def get_open_positions(self) -> List[Position]:
        return list(self.open_positions.values())
