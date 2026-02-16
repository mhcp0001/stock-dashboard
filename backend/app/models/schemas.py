from datetime import date, datetime

from pydantic import BaseModel, Field


# --- Market ---
class StockQuote(BaseModel):
    ticker: str
    name: str | None = None
    price: float
    change_pct: float
    volume: int
    market_cap: float | None = None


class TechnicalIndicators(BaseModel):
    ticker: str
    date: date
    rsi_14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    bb_position: float | None = None  # 0-1, current price position within bands
    sma_20: float | None = None
    sma_50: float | None = None
    volume_ratio: float | None = None  # vs 20-day average


# --- Trade ---
class TradeCreate(BaseModel):
    ticker: str
    direction: str = Field(pattern="^(long|short)$")
    entry_price: float
    target_price: float | None = None
    stop_loss: float | None = None
    entry_reason: str = ""
    tags: list[str] = []


class TradeClose(BaseModel):
    exit_price: float
    exit_reason: str = ""


class TradeResponse(BaseModel):
    id: int
    ticker: str
    direction: str
    entry_date: date
    entry_price: float
    target_price: float | None
    stop_loss: float | None
    exit_date: date | None
    exit_price: float | None
    entry_reason: str
    exit_reason: str | None
    pnl: float | None
    pnl_pct: float | None
    status: str
    tags: list[str]
    created_at: datetime


# --- Watchlist ---
class WatchlistAdd(BaseModel):
    ticker: str
    memo: str = ""


class WatchlistItem(BaseModel):
    id: int
    ticker: str
    name: str | None = None
    sector: str | None = None
    added_date: date
    memo: str
    status: str


# --- Analysis ---
class AnalysisRequest(BaseModel):
    message: str
    ticker: str | None = None
    conversation_id: str | None = None


class AnalysisResponse(BaseModel):
    response: str
    conversation_id: str
    indicators: TechnicalIndicators | None = None
