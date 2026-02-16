"""AI Analysis Chat page."""

import httpx
import streamlit as st

API_BASE = "http://localhost:8000/api"

st.title("💬 AI分析チャット")

# Ticker input
ticker = st.sidebar.text_input("銘柄コード", placeholder="例: 7203.T (トヨタ)")

if ticker:
    # Fetch and display indicators
    try:
        resp = httpx.get(f"{API_BASE}/market/indicators/{ticker}", timeout=30)
        if resp.status_code == 200:
            ind = resp.json()
            st.sidebar.markdown("### テクニカル指標")
            if ind.get("rsi_14"):
                rsi = ind["rsi_14"]
                rsi_color = "🔴" if rsi > 70 else "🟢" if rsi < 30 else "⚪"
                st.sidebar.markdown(f"{rsi_color} RSI(14): **{rsi}**")
            if ind.get("macd"):
                st.sidebar.markdown(f"MACD: **{ind['macd']}** / Signal: {ind.get('macd_signal', 'N/A')}")
            if ind.get("bb_position") is not None:
                st.sidebar.markdown(f"BB位置: **{ind['bb_position']}** (0=下限, 1=上限)")
            if ind.get("volume_ratio"):
                st.sidebar.markdown(f"出来高倍率: **{ind['volume_ratio']}x**")
    except httpx.ConnectError:
        st.sidebar.warning("バックエンドに接続できません")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("銘柄について質問..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("分析中..."):
            try:
                resp = httpx.post(
                    f"{API_BASE}/analysis/chat",
                    json={
                        "message": prompt,
                        "ticker": ticker or None,
                        "conversation_id": st.session_state.conversation_id,
                    },
                    timeout=60,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.markdown(data["response"])
                    st.session_state.messages.append({"role": "assistant", "content": data["response"]})
                    st.session_state.conversation_id = data["conversation_id"]
                else:
                    st.error(f"API Error: {resp.status_code}")
            except httpx.ConnectError:
                st.error("バックエンドに接続できません。docker compose up を確認してください。")
