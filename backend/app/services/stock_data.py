"""yfinance wrapper with caching."""

import time
from datetime import datetime, timedelta

import yfinance as yf

# Simple in-memory cache: {key: (data, expiry_time)}
_cache: dict[str, tuple[object, float]] = {}
CACHE_TTL = 60 * 60 * 4  # 4 hours for daily data
_last_call = 0.0
API_DELAY = 1.0  # seconds between API calls


def _rate_limit():
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < API_DELAY:
        time.sleep(API_DELAY - elapsed)
    _last_call = time.time()


def _get_cached(key: str):
    if key in _cache:
        data, expiry = _cache[key]
        if time.time() < expiry:
            return data
        del _cache[key]
    return None


def _set_cached(key: str, data: object, ttl: int = CACHE_TTL):
    _cache[key] = (data, time.time() + ttl)


def get_ticker_info(ticker: str) -> dict:
    """Get basic ticker info (name, sector, market cap, etc.)."""
    cache_key = f"info:{ticker}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    _rate_limit()
    t = yf.Ticker(ticker)
    info = t.info or {}
    _set_cached(cache_key, info)
    return info


def get_history(ticker: str, period: str = "6mo", interval: str = "1d"):
    """Get price history as a pandas DataFrame."""
    cache_key = f"history:{ticker}:{period}:{interval}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    _rate_limit()
    t = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval)
    if not df.empty:
        _set_cached(cache_key, df)
    return df


def get_quote(ticker: str) -> dict:
    """Get current quote summary."""
    info = get_ticker_info(ticker)
    hist = get_history(ticker, period="5d")

    price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    prev_close = info.get("previousClose", price)
    change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0

    return {
        "ticker": ticker,
        "name": info.get("shortName") or info.get("longName"),
        "price": price,
        "change_pct": round(change_pct, 2),
        "volume": info.get("volume", 0),
        "market_cap": info.get("marketCap"),
    }


def search_tickers(query: str, exchange: str = "JPX") -> list[dict]:
    """Search for tickers by name or code."""
    _rate_limit()
    results = yf.search(query)
    return results.get("quotes", []) if isinstance(results, dict) else []
