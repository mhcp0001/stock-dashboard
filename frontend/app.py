"""Stock Dashboard - Streamlit Frontend."""

import httpx
import streamlit as st

from config import API_BASE

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 Stock Dashboard")
st.markdown("スイングトレード支援ダッシュボード — LLM対話 × テクニカル分析 × トレードジャーナル")

st.sidebar.title("ナビゲーション")
st.sidebar.page_link("pages/chat.py", label="💬 AI分析チャット")
st.sidebar.page_link("pages/watchlist.py", label="👀 ウォッチリスト")
st.sidebar.page_link("pages/journal.py", label="📓 トレードジャーナル")

st.markdown("---")

# Dashboard metrics from backend
open_count = "—"
monthly_pl = "—"
win_rate = "—"

try:
    open_resp = httpx.get(f"{API_BASE}/trade/?status=open", timeout=5)
    closed_resp = httpx.get(f"{API_BASE}/trade/?status=closed", timeout=5)

    if open_resp.status_code == 200:
        open_count = str(len(open_resp.json()))

    if closed_resp.status_code == 200:
        closed = closed_resp.json()
        if closed:
            wins = sum(1 for t in closed if (t.get("pnl") or 0) > 0)
            win_rate = f"{wins / len(closed) * 100:.0f}%"
            total_pl = sum(t.get("pnl") or 0 for t in closed)
            monthly_pl = f"{'+'if total_pl >= 0 else ''}{total_pl:,.0f}円"
except httpx.ConnectError:
    st.warning("バックエンドに接続できません。`uvicorn app.main:app --reload` を確認してください。")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("オープンポジション", open_count, help="現在保有中のポジション数")
with col2:
    st.metric("今月P/L", monthly_pl, help="確定損益合計")
with col3:
    st.metric("勝率", win_rate, help="クローズ済みトレードの勝率")
