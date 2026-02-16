from fastapi import APIRouter

from app.models.schemas import StockQuote, TechnicalIndicators
from app.services import stock_data, technical

router = APIRouter()


@router.get("/quote/{ticker}", response_model=StockQuote)
async def get_quote(ticker: str):
    """Get current quote for a ticker."""
    quote = stock_data.get_quote(ticker)
    return StockQuote(**quote)


@router.get("/indicators/{ticker}", response_model=TechnicalIndicators)
async def get_indicators(ticker: str, period: str = "6mo"):
    """Get technical indicators for a ticker."""
    df = stock_data.get_history(ticker, period=period)
    indicators = technical.calculate_indicators(df)
    return TechnicalIndicators(ticker=ticker, **indicators)
