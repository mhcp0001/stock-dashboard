"""Technical indicator calculations using ta (Technical Analysis Library)."""

import pandas as pd
import ta as ta_lib


def calculate_indicators(df: pd.DataFrame) -> dict:
    """Calculate technical indicators from OHLCV DataFrame.

    Returns a dict of the latest values for each indicator.
    """
    if df.empty or len(df) < 20:
        return {}

    close = df["Close"]
    volume = df["Volume"]
    latest = len(df) - 1

    result = {
        "date": df.index[latest].date().isoformat() if hasattr(df.index[latest], "date") else str(df.index[latest]),
    }

    # RSI
    rsi = ta_lib.momentum.RSIIndicator(close, window=14)
    rsi_val = rsi.rsi()
    if rsi_val is not None and not rsi_val.empty:
        result["rsi_14"] = round(float(rsi_val.iloc[latest]), 2)

    # MACD
    macd = ta_lib.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
    macd_line = macd.macd()
    macd_signal = macd.macd_signal()
    macd_hist = macd.macd_diff()
    if macd_line is not None and not macd_line.empty:
        result["macd"] = round(float(macd_line.iloc[latest]), 2)
        result["macd_signal"] = round(float(macd_signal.iloc[latest]), 2)
        result["macd_hist"] = round(float(macd_hist.iloc[latest]), 2)

    # Bollinger Bands
    bb = ta_lib.volatility.BollingerBands(close, window=20, window_dev=2)
    bb_upper = bb.bollinger_hband()
    bb_mid = bb.bollinger_mavg()
    bb_lower = bb.bollinger_lband()
    if bb_upper is not None and not bb_upper.empty:
        upper_val = float(bb_upper.iloc[latest])
        mid_val = float(bb_mid.iloc[latest])
        lower_val = float(bb_lower.iloc[latest])
        current_price = float(close.iloc[latest])
        bb_width = upper_val - lower_val

        result["bb_upper"] = round(upper_val, 2)
        result["bb_middle"] = round(mid_val, 2)
        result["bb_lower"] = round(lower_val, 2)
        result["bb_position"] = round((current_price - lower_val) / bb_width, 3) if bb_width > 0 else 0.5

    # SMA
    sma_20 = ta_lib.trend.SMAIndicator(close, window=20).sma_indicator()
    if sma_20 is not None and not sma_20.empty:
        result["sma_20"] = round(float(sma_20.iloc[latest]), 2)

    if len(df) >= 50:
        sma_50 = ta_lib.trend.SMAIndicator(close, window=50).sma_indicator()
        if sma_50 is not None and not sma_50.empty:
            result["sma_50"] = round(float(sma_50.iloc[latest]), 2)

    # Volume ratio (current vs 20-day average)
    vol_sma_20 = ta_lib.trend.SMAIndicator(volume, window=20).sma_indicator()
    if vol_sma_20 is not None and not vol_sma_20.empty:
        avg_vol = float(vol_sma_20.iloc[latest])
        cur_vol = float(volume.iloc[latest])
        result["volume_ratio"] = round(cur_vol / avg_vol, 2) if avg_vol > 0 else 1.0

    return result
