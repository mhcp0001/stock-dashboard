from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.db.database import create_tables
from app.routers import analysis, market, trade, watchlist


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Stock Dashboard API",
    description="Stock swing trading dashboard with LLM-powered analysis",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(trade.router, prefix="/api/trade", tags=["trade"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
