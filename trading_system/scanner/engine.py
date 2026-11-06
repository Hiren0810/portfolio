"""
High-Throughput Asynchronous Multi-Market Scanner Engine.
Monitors 50+ markets concurrently with sub-second parallel processing,
pluggable strategy scoring, risk-managed order dispatch, and real-time state broadcasting.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Callable

try:
    from trading_system.config.settings import SystemSettings, DEFAULT_SETTINGS
    from trading_system.config.markets import get_market_universe
    from trading_system.core.models import MarketData, IndicatorValues, Signal, AccountSummary
    from trading_system.core.indicators import compute_all_indicators
    from trading_system.feeds.base_feed import BaseFeed
    from trading_system.feeds import get_feed
    from trading_system.strategies.base_strategy import BaseStrategy
    from trading_system.strategies import get_strategy
    from trading_system.execution.base_executor import BaseExecutor
    from trading_system.execution.paper_broker import PaperBroker
    from trading_system.execution.live_executor import LiveExecutor
    from trading_system.execution.notifier import Notifier
except (ImportError, ValueError):
    from config.settings import SystemSettings, DEFAULT_SETTINGS
    from config.markets import get_market_universe
    from core.models import MarketData, IndicatorValues, Signal, AccountSummary
    from core.indicators import compute_all_indicators
    from feeds.base_feed import BaseFeed
    from feeds import get_feed
    from strategies.base_strategy import BaseStrategy
    from strategies import get_strategy
    from execution.base_executor import BaseExecutor
    from execution.paper_broker import PaperBroker
    from execution.live_executor import LiveExecutor
    from execution.notifier import Notifier

logger = logging.getLogger("ScannerEngine")

class ScannerEngine:
    def __init__(
        self,
        settings: Optional[SystemSettings] = None,
        strategy_name: str = "confluence",
        market_count: int = 50,
        asset_class: str = "crypto",
        state_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.settings = settings or DEFAULT_SETTINGS
        self.strategy_name = strategy_name
        self.market_count = market_count
        self.asset_class = asset_class
        self.state_callback = state_callback

        # Universe of 50+ symbols
        self.symbols: List[str] = get_market_universe(name=asset_class, limit=market_count)

        # Feed adapter
        self.feed: BaseFeed = get_feed(feed_type=self.settings.feed_type)

        # Strategy
        self.strategy: BaseStrategy = get_strategy(name=strategy_name)

        # Execution Broker
        if self.settings.mode == "live":
            self.broker: BaseExecutor = LiveExecutor(
                api_key=self.settings.api_key,
                api_secret=self.settings.api_secret
            )
        else:
            self.broker = PaperBroker(risk_settings=self.settings.risk)

        # Notifier
        self.notifier = Notifier(
            discord_webhook=self.settings.discord_webhook_url,
            telegram_token=self.settings.telegram_bot_token,
            telegram_chat_id=self.settings.telegram_chat_id
        )

        # State cache for Web UI & monitoring
        self.is_running: bool = False
        self.scan_count: int = 0
        self.last_scan_time: float = 0.0
        self.last_scan_duration_ms: float = 0.0
        self.market_matrix: Dict[str, Dict[str, Any]] = {}
        self.recent_signals: List[Dict[str, Any]] = []
        self._scan_task: Optional[asyncio.Task] = None
        self._manual_trigger_event = asyncio.Event()

    async def start(self):
        """Start the background scanning task."""
        if self.is_running:
            return
        self.is_running = True
        logger.info(f"🚀 Starting Scanner Engine | Monitoring {len(self.symbols)} {self.asset_class.upper()} markets | Mode: {self.settings.mode.upper()}")
        self._scan_task = asyncio.create_task(self._run_loop())

    async def stop(self):
        """Stop the background scanning task cleanly."""
        self.is_running = False
        if self._scan_task:
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass
        logger.info("Scanner Engine stopped.")

    def trigger_instant_scan(self):
        """Request an immediate scan cycle without waiting for interval."""
        self._manual_trigger_event.set()

    async def scan_once(self) -> Dict[str, Any]:
        """Execute a single complete scan cycle across all 50+ markets."""
        start_t = time.time()
        self.scan_count += 1

        # 1. Concurrently fetch all 50+ markets
        markets: Dict[str, MarketData] = await self.feed.get_all_markets(
            symbols=self.symbols,
            timeframe=self.settings.scanner.timeframe,
            limit=self.settings.scanner.candle_history_limit
        )

        # 2. Update broker mark-to-market positions
        self.broker.update_markets(markets)

        # 3. Concurrently calculate indicators & evaluate strategy
        signals: List[Signal] = []
        matrix_rows: Dict[str, Dict[str, Any]] = {}

        for sym, m in markets.items():
            indicators: IndicatorValues = compute_all_indicators(m.candles)
            signal: Optional[Signal] = self.strategy.evaluate(m, indicators)

            action = "NEUTRAL"
            score = 0.0
            reasons = []

            if signal:
                action = signal.direction.value
                score = signal.confluence_score
                reasons = signal.reasons
                signals.append(signal)

            matrix_rows[sym] = {
                "symbol": sym,
                "price": m.current_price,
                "change_24h_pct": m.change_24h_pct,
                "high_24h": m.high_24h,
                "low_24h": m.low_24h,
                "volume_24h": m.volume_24h,
                "rsi": indicators.rsi,
                "macd_hist": indicators.macd_hist,
                "ema_9": indicators.ema_9,
                "ema_21": indicators.ema_21,
                "ema_50": indicators.ema_50,
                "bb_percent_b": indicators.bb_percent_b,
                "bb_bandwidth": indicators.bb_bandwidth,
                "atr": indicators.atr,
                "volume_ratio": indicators.volume_ratio,
                "trend_bias": indicators.trend_bias,
                "confluence_score": score,
                "action": action,
                "reasons": reasons
            }

        self.market_matrix = matrix_rows

        # 4. Process actionable trade signals
        account = self.broker.get_account_summary()
        for sig in signals:
            if abs(sig.confluence_score) >= self.settings.scanner.min_confluence_score:
                self.notifier.notify_signal(sig)
                self.recent_signals.insert(0, sig.to_dict())
                if len(self.recent_signals) > 100:
                    self.recent_signals.pop()

                # Dispatch order through broker
                order = self.broker.execute_signal(sig, account.total_equity)
                if order:
                    pos = next((p for p in self.broker.get_open_positions() if p.symbol == sig.symbol), None)
                    if pos:
                        self.notifier.notify_fill(order, pos)

        duration_ms = (time.time() - start_t) * 1000.0
        self.last_scan_duration_ms = round(duration_ms, 1)
        self.last_scan_time = time.time()

        # Build state snapshot
        state = self.get_state()

        if self.state_callback:
            try:
                self.state_callback(state)
            except Exception as e:
                logger.debug(f"State callback error: {e}")

        logger.debug(f"Scan cycle #{self.scan_count} completed in {self.last_scan_duration_ms}ms across {len(markets)} markets.")
        return state

    async def _run_loop(self):
        """Continuous async loop executing scans at configured intervals."""
        while self.is_running:
            try:
                await self.scan_once()
            except Exception as e:
                logger.error(f"Error during scan cycle: {e}", exc_info=True)

            # Sleep or respond to manual trigger
            interval = self.settings.scanner.scan_interval_seconds
            try:
                await asyncio.wait_for(self._manual_trigger_event.wait(), timeout=interval)
                self._manual_trigger_event.clear()
            except asyncio.TimeoutError:
                pass

    def get_state(self) -> Dict[str, Any]:
        """Generate comprehensive real-time system state for Web UI and API."""
        account = self.broker.get_account_summary()
        open_positions = [p.to_dict() for p in self.broker.get_open_positions()]
        
        # Sort matrix rows by confluence score descending (strongest setups first)
        sorted_matrix = sorted(
            self.market_matrix.values(),
            key=lambda x: abs(x["confluence_score"]),
            reverse=True
        )

        # Get recent trades from broker/db
        recent_trades = []
        if isinstance(self.broker, PaperBroker):
            recent_trades = [t.to_dict() for t in self.broker.trade_history[-25:]]
            recent_trades.reverse()

        return {
            "status": "RUNNING" if self.is_running else "PAUSED",
            "mode": self.settings.mode.upper(),
            "feed_type": self.feed.name,
            "strategy": self.strategy.name,
            "scan_count": self.scan_count,
            "last_scan_time": self.last_scan_time,
            "last_scan_duration_ms": self.last_scan_duration_ms,
            "total_markets_scanned": len(self.market_matrix),
            "account": account.to_dict(),
            "open_positions": open_positions,
            "markets": sorted_matrix,
            "recent_signals": self.recent_signals[:20],
            "recent_trades": recent_trades,
            "settings": {
                "risk_per_trade_pct": self.settings.risk.risk_per_trade_pct * 100.0,
                "max_open_positions": self.settings.risk.max_open_positions,
                "scan_interval": self.settings.scanner.scan_interval_seconds,
                "timeframe": self.settings.scanner.timeframe,
                "min_confluence": self.settings.scanner.min_confluence_score
            }
        }
