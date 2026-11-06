"""
High-performance pure-Python technical indicator calculation engine.
Requires zero external C-dependencies (no TA-Lib needed), runs anywhere.
Implements EMA, SMA, RSI (Wilder's), MACD, Bollinger Bands, ATR, and Volume ratios.
"""

import math
from typing import List, Tuple, Optional
try:
    from trading_system.core.models import Candle, IndicatorValues
except (ImportError, ValueError):
    from core.models import Candle, IndicatorValues

def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Calculate Simple Moving Average across price series."""
    if len(prices) < period or period <= 0:
        return [prices[-1]] if prices else [0.0]
    
    sma_values = []
    window_sum = sum(prices[:period])
    sma_values.append(window_sum / period)
    
    for i in range(period, len(prices)):
        window_sum += prices[i] - prices[i - period]
        sma_values.append(window_sum / period)
        
    return sma_values

def calculate_ema(prices: List[float], period: int) -> List[float]:
    """
    Calculate Exponential Moving Average.
    Multiplier k = 2 / (period + 1).
    Initial seed uses SMA of the first period.
    """
    if not prices:
        return [0.0]
    if len(prices) < period:
        # Fallback to cumulative average if insufficient length
        return [sum(prices) / len(prices)]
    
    k = 2.0 / (period + 1.0)
    # Seed with SMA
    ema = sum(prices[:period]) / period
    ema_series = [ema]
    
    for price in prices[period:]:
        ema = (price * k) + (ema * (1.0 - k))
        ema_series.append(ema)
        
    return ema_series

def calculate_rsi(closes: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI) using Wilder's smoothing.
    Returns scalar RSI of the latest candle (0.0 to 100.0).
    """
    if len(closes) < period + 1:
        return 50.0  # Neutral fallback for insufficient data
    
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    
    gains = [max(d, 0.0) for d in deltas[:period]]
    losses = [max(-d, 0.0) for d in deltas[:period]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    for d in deltas[period:]:
        gain = max(d, 0.0)
        loss = max(-d, 0.0)
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period
        
    if avg_loss == 0.0:
        return 100.0 if avg_gain > 0 else 50.0
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return round(rsi, 2)

def calculate_macd(closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
    """
    Calculate MACD Line, Signal Line, and Histogram for the latest bar.
    MACD = EMA(fast) - EMA(slow)
    Signal = EMA(signal) of MACD
    Histogram = MACD - Signal
    """
    if len(closes) < slow + signal:
        return 0.0, 0.0, 0.0
    
    fast_ema = calculate_ema(closes, fast)
    slow_ema = calculate_ema(closes, slow)
    
    # Align the two series: fast_ema started at index `fast - 1`, slow_ema started at `slow - 1`
    offset = slow - fast
    macd_series = [f - s for f, s in zip(fast_ema[offset:], slow_ema)]
    
    if len(macd_series) < signal:
        return 0.0, 0.0, 0.0
    
    signal_series = calculate_ema(macd_series, signal)
    
    latest_macd = macd_series[-1]
    latest_signal = signal_series[-1]
    latest_hist = latest_macd - latest_signal
    
    return round(latest_macd, 6), round(latest_signal, 6), round(latest_hist, 6)

def calculate_bollinger_bands(closes: List[float], period: int = 20, num_std: float = 2.0) -> Tuple[float, float, float, float, float]:
    """
    Calculate Bollinger Bands for the latest bar.
    Returns: (upper, middle, lower, percent_b, bandwidth)
    """
    if len(closes) < period:
        latest = closes[-1] if closes else 0.0
        return latest, latest, latest, 0.5, 0.0
    
    window = closes[-period:]
    mean = sum(window) / period
    variance = sum((x - mean) ** 2 for x in window) / period
    std_dev = math.sqrt(variance)
    
    upper = mean + (num_std * std_dev)
    lower = mean - (num_std * std_dev)
    
    latest_close = closes[-1]
    band_width_span = upper - lower
    
    percent_b = (latest_close - lower) / band_width_span if band_width_span > 0 else 0.5
    bandwidth = (band_width_span / mean) * 100.0 if mean > 0 else 0.0
    
    return round(upper, 6), round(mean, 6), round(lower, 6), round(percent_b, 4), round(bandwidth, 4)

def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    """
    Calculate Average True Range (ATR) with Wilder's smoothing.
    """
    if len(closes) < period + 1:
        if highs and lows:
            return round(highs[-1] - lows[-1], 6)
        return 0.0
    
    tr_series = []
    for i in range(1, len(closes)):
        h = highs[i]
        l = lows[i]
        prev_c = closes[i - 1]
        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        tr_series.append(tr)
        
    if not tr_series:
        return 0.0
        
    atr = sum(tr_series[:period]) / period
    for tr in tr_series[period:]:
        atr = ((atr * (period - 1)) + tr) / period
        
    return round(atr, 6)

def calculate_volume_metrics(volumes: List[float], period: int = 20) -> Tuple[float, float]:
    """
    Calculate Volume SMA and Current Volume to SMA Ratio.
    """
    if not volumes:
        return 0.0, 1.0
    
    recent_vol = volumes[-1]
    if len(volumes) < period:
        avg_vol = sum(volumes) / len(volumes)
    else:
        avg_vol = sum(volumes[-period:]) / period
        
    ratio = (recent_vol / avg_vol) if avg_vol > 0 else 1.0
    return round(avg_vol, 2), round(ratio, 2)

def compute_all_indicators(candles: List[Candle]) -> IndicatorValues:
    """
    Compute comprehensive indicator suite for a list of market candles.
    Returns populated IndicatorValues dataclass.
    """
    if not candles:
        return IndicatorValues()
    
    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    volumes = [c.volume for c in candles]
    
    # EMAs
    ema_9_series = calculate_ema(closes, 9)
    ema_21_series = calculate_ema(closes, 21)
    ema_50_series = calculate_ema(closes, 50)
    ema_200_series = calculate_ema(closes, 200) if len(closes) >= 50 else calculate_ema(closes, len(closes))
    
    ema_9 = ema_9_series[-1] if ema_9_series else closes[-1]
    ema_21 = ema_21_series[-1] if ema_21_series else closes[-1]
    ema_50 = ema_50_series[-1] if ema_50_series else closes[-1]
    ema_200 = ema_200_series[-1] if ema_200_series else closes[-1]
    
    # RSI
    rsi = calculate_rsi(closes, 14)
    
    # MACD
    macd, macd_signal, macd_hist = calculate_macd(closes, 12, 26, 9)
    
    # Bollinger Bands
    bb_upper, bb_mid, bb_lower, percent_b, bandwidth = calculate_bollinger_bands(closes, 20, 2.0)
    
    # ATR
    atr = calculate_atr(highs, lows, closes, 14)
    if atr == 0.0:
        atr = closes[-1] * 0.02  # 2% default fallback
        
    # Volume Metrics
    vol_sma, vol_ratio = calculate_volume_metrics(volumes, 20)
    
    # Determine overall Trend Bias
    latest_close = closes[-1]
    if latest_close > ema_9 > ema_21 > ema_50 and macd_hist > 0:
        trend_bias = "STRONG_BULL"
    elif latest_close > ema_21 and ema_9 > ema_21:
        trend_bias = "BULLISH"
    elif latest_close < ema_9 < ema_21 < ema_50 and macd_hist < 0:
        trend_bias = "STRONG_BEAR"
    elif latest_close < ema_21 and ema_9 < ema_21:
        trend_bias = "BEARISH"
    else:
        trend_bias = "NEUTRAL"
        
    return IndicatorValues(
        rsi=rsi,
        macd=macd,
        macd_signal=macd_signal,
        macd_hist=macd_hist,
        ema_9=round(ema_9, 6),
        ema_21=round(ema_21, 6),
        ema_50=round(ema_50, 6),
        ema_200=round(ema_200, 6),
        bb_upper=bb_upper,
        bb_middle=bb_mid,
        bb_lower=bb_lower,
        bb_percent_b=percent_b,
        bb_bandwidth=bandwidth,
        atr=atr,
        volume_sma=vol_sma,
        volume_ratio=vol_ratio,
        trend_bias=trend_bias
    )
