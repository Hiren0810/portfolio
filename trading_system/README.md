# 🚀 Antigravity Multi-Market Automated Trading System

An institutional-grade, asynchronous algorithmic trading system and market scanner engineered in Python. Concurrently monitors and analyzes **50+ markets simultaneously** (Cryptocurrency, US Equities, and Forex) with sub-second parallel processing, composite technical confluence scoring, mathematical risk management, and a real-time web command center.

Built with clean architecture and **zero required external runtime dependencies** (operates 100% on Python 3.9+ standard library), with optional plug-and-play connectors for CCXT, live exchanges, and webhook alerting.

---

## ⚡ Highlights & Key Capabilities

- **🌐 50+ Simultaneous Market Scanner**: High-throughput asynchronous coroutine pool (`asyncio.gather` with rate-limiting token bucket) capable of scanning 50 to 100+ markets in under 1.5 seconds without hitting exchange rate limits.
- **📈 Pure Python Indicator Engine**: Vectorized mathematical calculations for technical indicators without requiring brittle C-extensions or external dependencies:
  - **EMA Ribbon**: EMA 9, 21, 50, and 200 for micro and macro trend alignment.
  - **RSI (Wilder's Smoothing)**: 14-period Relative Strength Index with oversold/overbought zone filters.
  - **MACD**: 12/26/9 Fast/Slow/Signal line and momentum histogram crossovers.
  - **Bollinger Bands**: 20-period, 2-std bands with `%B` and Bandwidth squeeze detection.
  - **ATR (Average True Range)**: Dynamic volatility metric for adaptive stop-loss and position sizing.
  - **Volume Surge Filter**: Compares bar volume against 20-period Volume SMA.
- **🧠 Multi-Indicator Confluence Strategy**: Calculates a normalized composite score from `-100` (Strong Bearish / Short) to `+100` (Strong Bullish / Long) by checking alignment across trend, momentum, volatility, and volume.
- **🛡️ Institutional Risk Management Engine**:
  - **Risk-Adjusted Position Sizing**: Formula sizing based on fixed capital risk percentage (e.g. 1.5% per trade) divided by ATR stop distance: $\text{Size} = \frac{\text{Equity} \times \text{Risk\%}}{|\text{Entry} - \text{StopLoss}|}$.
  - **Dynamic ATR Stops**: Trailing and fixed stops that adjust dynamically to market volatility.
  - **Trailing Stop Loss**: Dynamic stop adjustment that locks in profit as prices advance.
  - **Max Portfolio Exposure**: Hard limits on concurrent active positions and total allocated capital.
  - **Circuit Breaker**: Daily maximum drawdown halt that locks out new trade entries if daily loss exceeds threshold.
- **💼 High-Fidelity Paper Trading Broker**:
  - Full exchange simulator with realistic slippage (0.05%) and taker fee deduction (0.075%).
  - Real-time mark-to-market position evaluation and automated stop loss / take profit execution.
  - Thread-safe SQLite audit trail for closed trades, win rate %, profit factor, and equity history.
- **🖥️ Real-Time Glassmorphic Web Dashboard**:
  - Dark-mode TradingView/Bloomberg style terminal served via built-in async HTTP & Server-Sent Events (SSE).
  - Live 50+ market table with instant search, signal filtering, RSI heatmap, and confluence scores.
  - Active positions panel with live unrealized PnL and 1-click manual close buttons.
  - Actionable signal stream and historical trade audit log.
- **📊 Multi-Market Backtester**: Walk-forward historical backtesting engine simulating hundreds of bars across 50 markets in seconds.

---

## 📁 System Architecture

```text
trading_system/
├── config/
│   ├── settings.py           # Risk parameters, timeouts, database paths, and API keys
│   └── markets.py            # Presets: Top 65 Crypto pairs, Top 50 US Equities, Forex majors
├── core/
│   ├── models.py             # Strongly-typed Dataclasses: Candle, MarketData, Signal, Position, Order
│   ├── indicators.py         # Pure Python indicator engine (EMA, RSI, MACD, BB, ATR, Volume)
│   ├── risk_manager.py       # Capital allocation, ATR stops, trailing stops, circuit breakers
│   └── database.py           # SQLite persistence for trades, signals, and equity snapshots
├── feeds/
│   ├── base_feed.py          # Abstract market data provider interface
│   ├── crypto_feed.py        # Asynchronous Binance/public market feed with rate-limit pooling
│   ├── mock_feed.py          # High-fidelity realistic market feed simulator (offline/sandbox)
│   └── equities_feed.py      # US Equities adapter (Yahoo Finance / Alpaca)
├── strategies/
│   ├── base_strategy.py      # Abstract strategy interface
│   ├── confluence.py         # Flagship Multi-Indicator Confluence Strategy (-100 to +100)
│   ├── breakout.py           # Bollinger Band squeeze & volatility breakout
│   └── mean_reversion.py     # RSI extreme snapback to 20-SMA
├── execution/
│   ├── base_executor.py      # Abstract execution interface
│   ├── paper_broker.py       # Simulated exchange broker (slippage, fees, mark-to-market)
│   ├── live_executor.py      # Exchange API order dispatcher (ready for API keys)
│   └── notifier.py           # Terminal color logs, Discord webhooks, Telegram alerts
├── scanner/
│   └── engine.py             # Asynchronous multi-market concurrency engine
├── web/
│   ├── server.py             # Built-in zero-dependency HTTP & SSE server
│   └── static/
│       ├── index.html        # Modern glassmorphic dark trading terminal
│       ├── app.js            # SSE telemetry listener, dynamic tables, manual controls
│       └── style.css         # Custom animations & styling
├── tests/
│   ├── test_indicators.py    # Math accuracy tests for indicators
│   ├── test_risk.py          # Risk rules, sizing, and circuit breaker tests
│   ├── test_paper_broker.py  # Order execution, fee, and PnL tests
│   └── test_scanner.py       # 50+ concurrent market scanning tests
├── backtest.py               # Historical backtester across 50+ pairs
├── run.py                    # Unified CLI entry point
└── requirements.txt          # Minimal / optional dependencies
```

---

## 🚀 Quickstart

### 1. Launch Paper Trading Bot & Real-Time Web Dashboard
To start scanning 50 markets simultaneously with live Paper Trading and the Web Dashboard:

```bash
# From workspace root
python3 trading_system/run.py --markets 50 --feed mock --interval 15
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:8080`**

### 2. Live Public Crypto Feed (Binance API)
To scan real live market prices across top 60 crypto pairs (no API keys required):

```bash
python3 trading_system/run.py --feed crypto --markets 50 --mode paper
```

### 3. Run Multi-Market Historical Backtest
To backtest a strategy across 50 markets over 100 historical candles:

```bash
# Test Confluence Strategy
python3 trading_system/backtest.py --markets 50 --strategy confluence --candles 100

# Test Volatility Breakout Strategy
python3 trading_system/backtest.py --markets 50 --strategy breakout --candles 100

# Test Mean Reversion Strategy
python3 trading_system/backtest.py --markets 50 --strategy mean_reversion --candles 100
```

### 4. Run Test Suite
Run the comprehensive unit test suite:

```bash
python3 -m unittest discover -s trading_system/tests -v
```

---

## ⚙️ Configuration & Risk Controls

Customize risk parameters in `trading_system/config/settings.py` or pass them via CLI:

| Parameter | Default | Description |
|---|---|---|
| `initial_capital` | `$10,000.00` | Starting paper wallet balance |
| `risk_per_trade_pct` | `1.5%` | Equity risked per trade |
| `max_open_positions` | `5` | Maximum simultaneous open positions |
| `max_portfolio_exposure_pct`| `60%` | Maximum capital allocated across all positions |
| `max_position_size_pct` | `20%` | Maximum single position allocation |
| `stop_loss_atr_multiplier` | `2.0` | Stop loss distance $= 2 \times \text{ATR}$ |
| `take_profit_rr_ratio` | `2.0` | 2:1 reward-to-risk ratio |
| `trailing_stop_enabled` | `True` | Locks in profit when trade is up $+1.5\%$ |
| `max_daily_drawdown_pct` | `3.5%` | Emergency circuit breaker halting new entries |
| `concurrency_limit` | `15` | Parallel async workers in semaphore pool |
| `scan_interval_seconds` | `15s` | Time between market scan sweeps |

---

## 🔔 Alerting (Discord & Telegram)

Set environment variables to receive instant alerts when trade signals occur:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python3 trading_system/run.py --markets 50
```

---

## 🛡️ License
MIT License. Created for high-performance quantitative trading research and algorithmic execution.
