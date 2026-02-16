import json
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # long / short
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    target_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    stop_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    exit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    entry_reason: Mapped[str] = mapped_column(Text, default="")
    exit_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)  # open / closed / cancelled
    _tags: Mapped[str] = mapped_column("tags", Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def tags(self) -> list[str]:
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value: list[str]):
        self._tags = json.dumps(value, ensure_ascii=False)


class Watchlist(Base):
    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(50), nullable=True)
    added_date: Mapped[date] = mapped_column(Date, default=date.today)
    memo: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="active")  # active / archived
