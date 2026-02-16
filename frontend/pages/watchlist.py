"""Watchlist management page."""

import httpx
import streamlit as st

from config import API_BASE

st.title("👀 ウォッチリスト")

# Add to watchlist
with st.form("add_watchlist"):
    col1, col2 = st.columns([1, 2])
    with col1:
        new_ticker = st.text_input("銘柄コード", placeholder="7203.T")
    with col2:
        memo = st.text_input("メモ", placeholder="注目理由...")
    submitted = st.form_submit_button("追加")

    if submitted and new_ticker:
        try:
            resp = httpx.post(
                f"{API_BASE}/watchlist/",
                json={"ticker": new_ticker, "memo": memo},
                timeout=30,
            )
            if resp.status_code == 200:
                st.success(f"{new_ticker} を追加しました")
                st.rerun()
            elif resp.status_code == 409:
                st.warning("既にウォッチリストに登録済みです")
            else:
                st.error(f"Error: {resp.status_code}")
        except httpx.ConnectError:
            st.error("バックエンドに接続できません")

# Display watchlist
st.markdown("---")
try:
    resp = httpx.get(f"{API_BASE}/watchlist/", timeout=10)
    if resp.status_code == 200:
        items = resp.json()
        if not items:
            st.info("ウォッチリストは空です。銘柄を追加してください。")
        else:
            for item in items:
                col1, col2, col3, col4 = st.columns([1, 2, 3, 1])
                with col1:
                    st.markdown(f"**{item['ticker']}**")
                with col2:
                    st.markdown(item.get("name") or "")
                with col3:
                    st.markdown(item.get("memo") or "")
                with col4:
                    if st.button("削除", key=f"del_{item['id']}"):
                        httpx.delete(f"{API_BASE}/watchlist/{item['id']}", timeout=10)
                        st.rerun()
except httpx.ConnectError:
    st.error("バックエンドに接続できません")
