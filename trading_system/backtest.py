"""
Multi-Market Strategy Backtester.
Simulates trading across 50+ markets over historical candle series.
Evaluates Net Profit, Win Rate, Profit Factor, Max Drawdown, and Risk-Adjusted Returns.
"""

import argparse
import asyncio
import time
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from typing import List, Dict
try:
    from trading_system.config.markets import get_market_universe
    from trading_system.config.settings import RiskSettings
    from trading_system.feeds import get_feed
    from trading_system.strategies import get_strategy
    from trading_system.execution.paper_broker import PaperBroker
    from trading_system.core.models import Candle, MarketData, SignalDirection
    from trading_system.core.indicators import compute_all_indicators
except (ImportError, ValueError):
    from config.markets import get_market_universe
    from config.settings import RiskSettings
    from feeds import get_feed
    from strategies import get_strategy
    from execution.paper_broker import PaperBroker
    from core.models import Candle, MarketData, SignalDirection
    from core.indicators import compute_all_indicators

def run_backtest(
    strategy_name: str = "confluence",
    market_count: int = 50,
    asset_class: str = "crypto",
    candles_count: int = 200,
    feed_type: str = "mock"
):
    print("\n" + "="*70)
    print(f"🚀 ANTIGRAVITY BACKTESTER: {strategy_name.upper()} STRATEGY")
    print(f"   Universe: {market_count} {asset_class.upper()} Markets | History: {candles_count} candles/market")
    print("="*70)

    symbols = get_market_universe(name=asset_class, limit=market_count)
    feed = get_feed(feed_type=feed_type)
    strategy = get_strategy(name=strategy_name)

    # Fetch historical data for all markets
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print(f"[*] Pre-loading historical candles across {len(symbols)} markets...")
    all_markets = loop.run_until_complete(feed.get_all_markets(symbols, limit=candles_count))
    loop.close()

    risk_settings = RiskSettings(initial_capital=10000.0)
    broker = PaperBroker(risk_settings=risk_settings)

    start_time = time.time()
    min_warmup = 35  # Bars needed for 26-period MACD and 20-period BB

    # Bar-by-bar time-series walk forward
    max_bars = min(len(m.candles) for m in all_markets.values())
    print(f"[*] Simulating {max_bars - min_warmup} sequential time steps across {len(all_markets)} markets...")

    for step in range(min_warmup, max_bars):
        current_market_slice: Dict[str, MarketData] = {}

        # 1. Update prices for this step
        for sym, full_market in all_markets.items():
            sub_candles = full_market.candles[:step]
            current_bar = sub_candles[-1]
            first_bar = sub_candles[0]
            chg = ((current_bar.close - first_bar.close) / first_bar.close) * 100.0
            
            slice_m = MarketData(
                symbol=sym,
                current_price=current_bar.close,
                change_24h_pct=round(chg, 2),
                high_24h=max(c.high for c in sub_candles),
                low_24h=min(c.low for c in sub_candles),
                volume_24h=sum(c.volume for c in sub_candles),
                candles=sub_candles
            )
            current_market_slice[sym] = slice_m

        # 2. Broker updates mark-to-market positions and executes stop/profit orders
        broker.update_markets(current_market_slice)

        # 3. Strategy evaluates markets for new setups
        for sym, m in current_market_slice.items():
            indicators = compute_all_indicators(m.candles)
            signal = strategy.evaluate(m, indicators)
            if signal and abs(signal.confluence_score) >= 60.0:
                broker.execute_signal(signal, broker.get_account_summary().total_equity)

    # Close remaining positions at last known prices
    broker.close_all_positions(reason="BACKTEST_END")

    duration = time.time() - start_time
    summary = broker.get_account_summary()
    trades = broker.trade_history

    wins = [t for t in trades if t.realized_pnl > 0]
    losses = [t for t in trades if t.realized_pnl <= 0]
    gross_profit = sum(t.realized_pnl for t in wins)
    gross_loss = abs(sum(t.realized_pnl for t in losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0)
    net_pnl = summary.realized_pnl
    return_pct = (net_pnl / 10000.0) * 100.0

    print("\n" + "-"*70)
    print("📊 BACKTEST PERFORMANCE SUMMARY")
    print("-"*70)
    print(f" Initial Capital:         $10,000.00")
    print(f" Final Portfolio Equity:  ${summary.total_equity:,.2f}")
    print(f" Net Realized Profit:     ${net_pnl:+,.2f} ({return_pct:+.2f}%)")
    print(f" Total Trades Executed:   {len(trades)}")
    print(f" Win Rate:                {summary.win_rate_pct:.1f}% ({len(wins)} Wins / {len(losses)} Losses)")
    print(f" Profit Factor:           {profit_factor:.2f}")
    print(f" Simulation Duration:     {duration:.2f} seconds ({len(all_markets) * (max_bars - min_warmup)} market-bars)")
    print("="*70 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Market Backtest Engine")
    parser.add_argument("--strategy", type=str, default="confluence", choices=["confluence", "breakout", "mean_reversion"])
    parser.add_argument("--markets", type=int, default=50)
    parser.add_argument("--asset", type=str, default="crypto", choices=["crypto", "equities"])
    parser.add_argument("--candles", type=int, default=150)
    parser.add_argument("--feed", type=str, default="mock", choices=["mock", "crypto", "equities"])
    args = parser.parse_args()

    run_backtest(
        strategy_name=args.strategy,
        market_count=args.markets,
        asset_class=args.asset,
        candles_count=args.candles,
        feed_type=args.feed
    )
