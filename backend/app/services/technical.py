"""Technical indicator calculations using pandas_ta."""

import pandas as pd
import pandas_ta as ta


def calculate_indicators(df: pd.DataFrame) -> dict:
    """Calculate technical indicators from OHLCV DataFrame.

    Returns a dict of the latest values for each indicator.
    """
    if df.empty or len(df) < 20:
        return {}

    close = df["Close"]
    volume = df["Volume"]

    # RSI
    rsi = ta.rsi(close, length=14)

    # MACD
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)

    # Bollinger Bands
    bb_df = ta.bbands(close, length=20, std=2)

    # SMA
    sma_20 = ta.sma(close, length=20)
    sma_50 = ta.sma(close, length=50) if len(df) >= 50 else None

    # Volume ratio (current vs 20-day average)
    vol_sma_20 = ta.sma(volume, length=20)

    latest = len(df) - 1
    result = {
        "date": df.index[latest].date().isoformat() if hasattr(df.index[latest], "date") else str(df.index[latest]),
    }

    if rsi is not None and not rsi.empty:
        result["rsi_14"] = round(float(rsi.iloc[latest]), 2)

    if macd_df is not None and not macd_df.empty:
        cols = macd_df.columns
        result["macd"] = round(float(macd_df[cols[0]].iloc[latest]), 2)
        result["macd_signal"] = round(float(macd_df[cols[1]].iloc[latest]), 2)
        result["macd_hist"] = round(float(macd_df[cols[2]].iloc[latest]), 2)

    if bb_df is not None and not bb_df.empty:
        cols = bb_df.columns
        bb_lower = float(bb_df[cols[0]].iloc[latest])
        bb_mid = float(bb_df[cols[1]].iloc[latest])
        bb_upper = float(bb_df[cols[2]].iloc[latest])
        current_price = float(close.iloc[latest])
        bb_width = bb_upper - bb_lower

        result["bb_upper"] = round(bb_upper, 2)
        result["bb_middle"] = round(bb_mid, 2)
        result["bb_lower"] = round(bb_lower, 2)
        result["bb_position"] = round((current_price - bb_lower) / bb_width, 3) if bb_width > 0 else 0.5

    if sma_20 is not None and not sma_20.empty:
        result["sma_20"] = round(float(sma_20.iloc[latest]), 2)

    if sma_50 is not None and not sma_50.empty:
        result["sma_50"] = round(float(sma_50.iloc[latest]), 2)

    if vol_sma_20 is not None and not vol_sma_20.empty:
        avg_vol = float(vol_sma_20.iloc[latest])
        cur_vol = float(volume.iloc[latest])
        result["volume_ratio"] = round(cur_vol / avg_vol, 2) if avg_vol > 0 else 1.0

    return result
