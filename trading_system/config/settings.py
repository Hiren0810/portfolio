"""
Global configuration settings for the automated trading system.
Provides defaults, environment variable overrides, and risk constraints.
"""

import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class RiskSettings:
    initial_capital: float = 10000.0       # Starting paper wallet ($ USD/USDT)
    risk_per_trade_pct: float = 0.015      # Risk 1.5% of total equity per trade
    max_open_positions: int = 5            # Max simultaneous open positions
    max_portfolio_exposure_pct: float = 0.60 # Max 60% of total capital allocated
    max_position_size_pct: float = 0.20    # Max 20% in any single market
    stop_loss_atr_multiplier: float = 2.0  # Dynamic Stop Loss: 2 * ATR
    take_profit_rr_ratio: float = 2.0      # Dynamic Take Profit: 2:1 Reward:Risk
    trailing_stop_enabled: bool = True     # Dynamic trailing stop loss
    trailing_stop_activation_pct: float = 0.015 # Activate trailing stop at +1.5% profit
    trailing_stop_distance_pct: float = 0.010   # Trail by 1.0% from peak
    max_daily_drawdown_pct: float = 0.035  # 3.5% daily loss halts new entries (Circuit Breaker)
    slippage_pct: float = 0.0005           # 0.05% realistic execution slippage
    fee_rate_pct: float = 0.00075          # 0.075% taker fee (Binance VIP0 standard)

@dataclass
class ScannerSettings:
    default_asset_class: str = "crypto"    # "crypto", "equities", "mock"
    default_market_count: int = 50         # Number of concurrent markets to scan (50+)
    timeframe: str = "15m"                 # Default candle timeframe: 1m, 5m, 15m, 1h, 4h, 1d
    candle_history_limit: int = 100        # Number of historical candles per pair
    scan_interval_seconds: int = 15        # Scan cycle every 15 seconds
    concurrency_limit: int = 15            # Number of parallel async workers
    request_timeout_seconds: float = 8.0   # HTTP request timeout per market
    min_confluence_score: float = 60.0     # Minimum score (0-100) to trigger an order

@dataclass
class SystemSettings:
    mode: str = "paper"                    # "paper", "live", "scan-only"
    feed_type: str = "mock"                # "crypto", "mock", "equities" (mock defaults for offline/sandbox)
    dashboard_enabled: bool = True
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8080
    database_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trading.db")
    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    api_key: str = os.getenv("EXCHANGE_API_KEY", "")
    api_secret: str = os.getenv("EXCHANGE_API_SECRET", "")
    risk: RiskSettings = field(default_factory=RiskSettings)
    scanner: ScannerSettings = field(default_factory=ScannerSettings)

# Global default instance
DEFAULT_SETTINGS = SystemSettings()
