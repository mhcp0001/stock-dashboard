from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Trade
from app.models.schemas import TradeClose, TradeCreate, TradeResponse
from app.services import obsidian, stock_data, technical

router = APIRouter()


def _trade_to_response(trade: Trade) -> TradeResponse:
    return TradeResponse(
        id=trade.id,
        ticker=trade.ticker,
        direction=trade.direction,
        entry_date=trade.entry_date,
        entry_price=trade.entry_price,
        target_price=trade.target_price,
        stop_loss=trade.stop_loss,
        exit_date=trade.exit_date,
        exit_price=trade.exit_price,
        entry_reason=trade.entry_reason,
        exit_reason=trade.exit_reason,
        pnl=trade.pnl,
        pnl_pct=trade.pnl_pct,
        status=trade.status,
        tags=trade.tags,
        created_at=trade.created_at,
    )


@router.post("/", response_model=TradeResponse)
async def create_trade(req: TradeCreate, db: Session = Depends(get_db)):
    """Record a new trade entry."""
    trade = Trade(
        ticker=req.ticker,
        direction=req.direction,
        entry_date=date.today(),
        entry_price=req.entry_price,
        target_price=req.target_price,
        stop_loss=req.stop_loss,
        entry_reason=req.entry_reason,
    )
    trade.tags = req.tags
    db.add(trade)
    db.commit()
    db.refresh(trade)

    # Write Obsidian journal
    df = stock_data.get_history(req.ticker, period="6mo")
    indicators = technical.calculate_indicators(df) if not df.empty else None
    obsidian.write_trade_journal(
        ticker=req.ticker,
        direction=req.direction,
        entry_date=trade.entry_date,
        entry_price=req.entry_price,
        entry_reason=req.entry_reason,
        target_price=req.target_price,
        stop_loss=req.stop_loss,
        indicators=indicators,
        tags=req.tags,
    )

    return _trade_to_response(trade)


@router.post("/{trade_id}/close", response_model=TradeResponse)
async def close_trade(trade_id: int, req: TradeClose, db: Session = Depends(get_db)):
    """Close an existing trade."""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    if trade.status != "open":
        raise HTTPException(status_code=400, detail=f"Trade is already {trade.status}")

    trade.exit_date = date.today()
    trade.exit_price = req.exit_price
    trade.exit_reason = req.exit_reason
    trade.status = "closed"

    # Calculate P/L
    if trade.direction == "long":
        trade.pnl = req.exit_price - trade.entry_price
    else:
        trade.pnl = trade.entry_price - req.exit_price
    trade.pnl_pct = (trade.pnl / trade.entry_price) * 100

    db.commit()
    db.refresh(trade)

    # Update Obsidian journal
    obsidian.update_trade_close(
        ticker=trade.ticker,
        entry_date=trade.entry_date,
        exit_date=trade.exit_date,
        exit_price=req.exit_price,
        exit_reason=req.exit_reason,
        pnl=trade.pnl,
        pnl_pct=trade.pnl_pct,
    )

    return _trade_to_response(trade)


@router.get("/", response_model=list[TradeResponse])
async def list_trades(status: str | None = None, db: Session = Depends(get_db)):
    """List trades, optionally filtered by status."""
    query = db.query(Trade).order_by(Trade.created_at.desc())
    if status:
        query = query.filter(Trade.status == status)
    return [_trade_to_response(t) for t in query.all()]


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get a single trade by ID."""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return _trade_to_response(trade)
