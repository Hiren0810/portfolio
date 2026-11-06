"""
SQLite database persistence engine for the trading bot.
Stores trade history, position audit trails, signal records, and equity snapshots.
"""

import sqlite3
import json
import os
import time
from typing import List, Dict, Any, Optional
try:
    from trading_system.core.models import TradeRecord, Position, Signal, AccountSummary
except (ImportError, ValueError):
    from core.models import TradeRecord, Position, Signal, AccountSummary

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "trading.db")

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Create necessary database tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    realized_pnl REAL NOT NULL,
                    pnl_pct REAL NOT NULL,
                    fees REAL NOT NULL,
                    opened_at REAL NOT NULL,
                    closed_at REAL NOT NULL,
                    duration_seconds REAL NOT NULL,
                    exit_reason TEXT NOT NULL
                )
            """)

            # Positions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    position_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    status TEXT NOT NULL,
                    unrealized_pnl REAL NOT NULL,
                    realized_pnl REAL NOT NULL,
                    opened_at REAL NOT NULL,
                    closed_at REAL,
                    close_reason TEXT
                )
            """)

            # Signals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    signal_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    confluence_score REAL NOT NULL,
                    strategy TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    stop_loss REAL,
                    take_profit REAL,
                    reasons TEXT,
                    timestamp REAL NOT NULL
                )
            """)

            # Portfolio Equity Snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equity_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    total_equity REAL NOT NULL,
                    cash_balance REAL NOT NULL,
                    allocated_margin REAL NOT NULL,
                    unrealized_pnl REAL NOT NULL,
                    realized_pnl REAL NOT NULL
                )
            """)

            conn.commit()

    def record_trade(self, trade: TradeRecord):
        """Persist closed trade record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO trades (
                    trade_id, symbol, side, entry_price, exit_price, quantity,
                    realized_pnl, pnl_pct, fees, opened_at, closed_at,
                    duration_seconds, exit_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.trade_id, trade.symbol, trade.side, trade.entry_price,
                trade.exit_price, trade.quantity, trade.realized_pnl, trade.pnl_pct,
                trade.fees, trade.opened_at, trade.closed_at, trade.duration_seconds,
                trade.exit_reason
            ))
            conn.commit()

    def record_signal(self, signal: Signal):
        """Persist generated signal."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO signals (
                    signal_id, symbol, direction, confluence_score, strategy,
                    current_price, stop_loss, take_profit, reasons, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.id, signal.symbol, signal.direction.value, signal.confluence_score,
                signal.strategy, signal.current_price, signal.suggested_stop_loss,
                signal.suggested_take_profit, json.dumps(signal.reasons), signal.timestamp
            ))
            conn.commit()

    def record_equity_snapshot(self, account: AccountSummary):
        """Record account equity state snapshot."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO equity_snapshots (
                    timestamp, total_equity, cash_balance, allocated_margin, unrealized_pnl, realized_pnl
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                time.time(), account.total_equity, account.cash_balance,
                account.allocated_margin, account.unrealized_pnl, account.realized_pnl
            ))
            conn.commit()

    def get_recent_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent trades sorted newest first."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades ORDER BY closed_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent signals sorted newest first."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = []
            for row in cursor.fetchall():
                d = dict(row)
                if d.get("reasons"):
                    try:
                        d["reasons"] = json.loads(d["reasons"])
                    except Exception:
                        pass
                rows.append(d)
            return rows

    def get_equity_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve historical equity snapshots for graphing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equity_snapshots ORDER BY timestamp ASC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_trade_statistics(self) -> Dict[str, Any]:
        """Calculate aggregate performance metrics from trades."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT realized_pnl, fees FROM trades")
            trades = cursor.fetchall()

        if not trades:
            return {
                "total_trades": 0,
                "win_rate_pct": 0.0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_net_pnl": 0.0,
                "profit_factor": 0.0
            }

        pnls = [row["realized_pnl"] for row in trades]
        wins = [p for p in pnls if p > 0]
        losses = [abs(p) for p in pnls if p < 0]
        
        gross_profit = sum(wins)
        gross_loss = sum(losses)
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0)
        win_rate = (len(wins) / len(pnls)) * 100.0 if pnls else 0.0

        return {
            "total_trades": len(pnls),
            "win_rate_pct": round(win_rate, 2),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "total_net_pnl": round(sum(pnls), 2),
            "profit_factor": round(profit_factor, 2)
        }
