"""Stock Dashboard - Streamlit Frontend."""

import streamlit as st

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

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("オープンポジション", "—", help="現在保有中のポジション数")
with col2:
    st.metric("今月P/L", "—", help="今月の確定損益合計")
with col3:
    st.metric("勝率", "—", help="クローズ済みトレードの勝率")

st.info("バックエンドAPI (http://localhost:8000) に接続して動作します。")
