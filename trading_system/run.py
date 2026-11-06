"""
Unified CLI Entrypoint for the Antigravity Multi-Market Trading Bot.
Coordinates the Scanner Engine, Execution Broker, and Real-Time Web Dashboard.
"""

import argparse
import asyncio
import logging
import signal
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from trading_system.config.settings import SystemSettings, DEFAULT_SETTINGS
    from trading_system.scanner.engine import ScannerEngine
    from trading_system.web.server import WebServer
except (ImportError, ValueError):
    from config.settings import SystemSettings, DEFAULT_SETTINGS
    from scanner.engine import ScannerEngine
    from web.server import WebServer

# Configure clean logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AntigravityTrading")

def print_banner(settings: SystemSettings, market_count: int, strategy: str):
    banner = f"""
\033[1;36m╔══════════════════════════════════════════════════════════════════════════╗
║               🚀 ANTIGRAVITY MULTI-MARKET TRADING SYSTEM                 ║
╚══════════════════════════════════════════════════════════════════════════╝\033[0m
  \033[1;32m● Status:\033[0m       ACTIVE
  \033[1;34m● Markets:\033[0m      \033[1m{market_count} Simultaneous Markets\033[0m ({settings.scanner.default_asset_class.upper()})
  \033[1;34m● Feed Type:\033[0m    {settings.feed_type.upper()}
  \033[1;34m● Strategy:\033[0m     {strategy.upper()}
  \033[1;34m● Timeframe:\033[0m    {settings.scanner.timeframe}
  \033[1;34m● Mode:\033[0m         {settings.mode.upper()}
  \033[1;34m● Risk/Trade:\033[0m   {settings.risk.risk_per_trade_pct * 100:.1f}% (${settings.risk.initial_capital * settings.risk.risk_per_trade_pct:.2f})
  \033[1;34m● Max Positions:\033[0m {settings.risk.max_open_positions}
  \033[1;34m● Dashboard:\033[0m    \033[1;32mhttp://{settings.dashboard_host}:{settings.dashboard_port}\033[0m
\033[1;36m════════════════════════════════════════════════════════════════════════════\033[0m
"""
    print(banner)

async def main():
    parser = argparse.ArgumentParser(description="Antigravity Multi-Market Trading Bot")
    parser.add_argument("--mode", type=str, default="paper", choices=["paper", "live", "scan-only"], help="Execution mode")
    parser.add_argument("--feed", type=str, default="mock", choices=["mock", "crypto", "equities"], help="Market data feed (mock defaults for offline/sandbox)")
    parser.add_argument("--markets", type=int, default=50, help="Number of concurrent markets to scan (e.g. 50)")
    parser.add_argument("--strategy", type=str, default="confluence", choices=["confluence", "breakout", "mean_reversion"], help="Trading strategy")
    parser.add_argument("--asset", type=str, default="crypto", choices=["crypto", "equities", "forex"], help="Asset class universe")
    parser.add_argument("--interval", type=int, default=15, help="Scan interval in seconds")
    parser.add_argument("--timeframe", type=str, default="15m", help="Candle timeframe")
    parser.add_argument("--port", type=int, default=8080, help="Dashboard web port")
    parser.add_argument("--no-dashboard", action="store_true", help="Run in headless terminal mode without Web UI")
    args = parser.parse_args()

    # Build settings
    settings = DEFAULT_SETTINGS
    settings.mode = args.mode
    settings.feed_type = args.feed
    settings.dashboard_port = args.port
    settings.dashboard_enabled = not args.no_dashboard
    settings.scanner.default_asset_class = args.asset
    settings.scanner.default_market_count = args.markets
    settings.scanner.scan_interval_seconds = args.interval
    settings.scanner.timeframe = args.timeframe

    print_banner(settings, args.markets, args.strategy)

    # Initialize Engine
    engine = ScannerEngine(
        settings=settings,
        strategy_name=args.strategy,
        market_count=args.markets,
        asset_class=args.asset
    )

    # Web Dashboard Server
    web_server = None
    if settings.dashboard_enabled:
        web_server = WebServer(
            scanner_engine=engine,
            host=settings.dashboard_host,
            port=settings.dashboard_port
        )
        web_server.start()

    # Register Graceful Shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def handle_exit():
        logger.info("\n🛑 Shutdown signal received. Cleaning up...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_exit)
        except NotImplementedError:
            # Signal handling on Windows
            pass

    # Start the scanner loop
    await engine.start()

    try:
        await stop_event.wait()
    finally:
        await engine.stop()
        if web_server:
            web_server.stop()
        logger.info("Antigravity Trading System stopped gracefully. Safe trading!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
