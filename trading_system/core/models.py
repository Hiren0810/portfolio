"""
Core data models and domain entities for the trading system.
Provides strongly typed dataclasses for candles, indicators, signals, orders, and positions.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any
import time
import uuid

class SignalDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class OrderSide(str, Enum):
    BUY = "BUY"      # Long
    SELL = "SELL"    # Short / Close Long

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

@dataclass
class Candle:
    timestamp: int     # Epoch timestamp in milliseconds
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class MarketData:
    symbol: str
    current_price: float
    change_24h_pct: float
    high_24h: float
    low_24h: float
    volume_24h: float
    candles: List[Candle] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "current_price": self.current_price,
            "change_24h_pct": self.change_24h_pct,
            "high_24h": self.high_24h,
            "low_24h": self.low_24h,
            "volume_24h": self.volume_24h,
            "timestamp": self.timestamp,
            "candle_count": len(self.candles)
        }

@dataclass
class IndicatorValues:
    rsi: float = 50.0
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_hist: float = 0.0
    ema_9: float = 0.0
    ema_21: float = 0.0
    ema_50: float = 0.0
    ema_200: float = 0.0
    bb_upper: float = 0.0
    bb_middle: float = 0.0
    bb_lower: float = 0.0
    bb_percent_b: float = 0.5
    bb_bandwidth: float = 0.0
    atr: float = 0.0
    volume_sma: float = 0.0
    volume_ratio: float = 1.0
    trend_bias: str = "NEUTRAL" # "STRONG_BULL", "BULLISH", "NEUTRAL", "BEARISH", "STRONG_BEAR"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Signal:
    symbol: str
    direction: SignalDirection
    confluence_score: float         # Scaled -100 (Strong Sell) to +100 (Strong Buy)
    strategy: str
    current_price: float
    suggested_stop_loss: float
    suggested_take_profit: float
    reasons: List[str] = field(default_factory=list)
    indicators: Optional[IndicatorValues] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["direction"] = self.direction.value
        return d

@dataclass
class Order:
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    fee: float = 0.0
    order_id: str = field(default_factory=lambda: f"ord_{str(uuid.uuid4())[:8]}")
    created_at: float = field(default_factory=time.time)
    filled_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "stop_price": self.stop_price,
            "status": self.status.value,
            "fee": self.fee,
            "created_at": self.created_at,
            "filled_at": self.filled_at
        }

@dataclass
class Position:
    symbol: str
    side: OrderSide
    entry_price: float
    current_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    trailing_stop_active: bool = False
    peak_price: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    status: PositionStatus = PositionStatus.OPEN
    position_id: str = field(default_factory=lambda: f"pos_{str(uuid.uuid4())[:8]}")
    opened_at: float = field(default_factory=time.time)
    closed_at: Optional[float] = None
    close_price: Optional[float] = None
    close_reason: Optional[str] = None
    realized_pnl: float = 0.0

    def __post_init__(self):
        if self.peak_price == 0.0:
            self.peak_price = self.entry_price

    def update_price(self, current_price: float):
        """Update current price, peak tracking, and unrealized PnL."""
        self.current_price = current_price
        if self.side == OrderSide.BUY:
            if current_price > self.peak_price:
                self.peak_price = current_price
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
            self.unrealized_pnl_pct = (current_price - self.entry_price) / self.entry_price * 100.0
        else: # SHORT
            if current_price < self.peak_price or self.peak_price == self.entry_price:
                self.peak_price = current_price
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity
            self.unrealized_pnl_pct = (self.entry_price - current_price) / self.entry_price * 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position_id": self.position_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "entry_price": round(self.entry_price, 6),
            "current_price": round(self.current_price, 6),
            "quantity": round(self.quantity, 6),
            "stop_loss": round(self.stop_loss, 6),
            "take_profit": round(self.take_profit, 6),
            "trailing_stop_active": self.trailing_stop_active,
            "peak_price": round(self.peak_price, 6),
            "unrealized_pnl": round(self.unrealized_pnl, 2),
            "unrealized_pnl_pct": round(self.unrealized_pnl_pct, 2),
            "status": self.status.value,
            "opened_at": self.opened_at,
            "closed_at": self.closed_at,
            "close_price": round(self.close_price, 6) if self.close_price else None,
            "close_reason": self.close_reason,
            "realized_pnl": round(self.realized_pnl, 2)
        }

@dataclass
class TradeRecord:
    trade_id: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    realized_pnl: float
    pnl_pct: float
    fees: float
    opened_at: float
    closed_at: float
    duration_seconds: float
    exit_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AccountSummary:
    total_equity: float
    cash_balance: float
    allocated_margin: float
    unrealized_pnl: float
    realized_pnl: float
    win_rate_pct: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    profit_factor: float = 0.0
    max_drawdown_pct: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
