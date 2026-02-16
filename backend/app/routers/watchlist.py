from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Watchlist
from app.models.schemas import WatchlistAdd, WatchlistItem
from app.services import stock_data

router = APIRouter()


@router.post("/", response_model=WatchlistItem)
async def add_to_watchlist(req: WatchlistAdd, db: Session = Depends(get_db)):
    """Add a ticker to the watchlist."""
    existing = db.query(Watchlist).filter(Watchlist.ticker == req.ticker).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already in watchlist")

    info = stock_data.get_ticker_info(req.ticker)
    item = Watchlist(
        ticker=req.ticker,
        name=info.get("shortName") or info.get("longName"),
        sector=info.get("sector"),
        memo=req.memo,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return WatchlistItem(
        id=item.id,
        ticker=item.ticker,
        name=item.name,
        sector=item.sector,
        added_date=item.added_date,
        memo=item.memo,
        status=item.status,
    )


@router.get("/", response_model=list[WatchlistItem])
async def list_watchlist(db: Session = Depends(get_db)):
    """List all watchlist items."""
    items = db.query(Watchlist).filter(Watchlist.status == "active").all()
    return [
        WatchlistItem(
            id=item.id,
            ticker=item.ticker,
            name=item.name,
            sector=item.sector,
            added_date=item.added_date,
            memo=item.memo,
            status=item.status,
        )
        for item in items
    ]


@router.delete("/{item_id}")
async def remove_from_watchlist(item_id: int, db: Session = Depends(get_db)):
    """Archive a watchlist item."""
    item = db.query(Watchlist).filter(Watchlist.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = "archived"
    db.commit()
    return {"status": "archived"}
