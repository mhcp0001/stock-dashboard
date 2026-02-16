"""Trade Journal page."""

import httpx
import streamlit as st

API_BASE = "http://localhost:8000/api"

st.title("📓 トレードジャーナル")

tab_open, tab_closed = st.tabs(["オープン", "クローズ済み"])

try:
    # Open trades
    with tab_open:
        resp = httpx.get(f"{API_BASE}/trade/?status=open", timeout=10)
        if resp.status_code == 200:
            trades = resp.json()
            if not trades:
                st.info("オープンポジションはありません")
            for trade in trades:
                with st.expander(f"{trade['ticker']} {trade['direction'].upper()} @{trade['entry_price']}"):
                    st.markdown(f"**エントリー日**: {trade['entry_date']}")
                    if trade.get("target_price"):
                        st.markdown(f"**目標**: {trade['target_price']} / **損切**: {trade.get('stop_loss', 'N/A')}")
                    st.markdown(f"**根拠**: {trade.get('entry_reason', '')}")
                    st.markdown(f"**タグ**: {', '.join(trade.get('tags', []))}")

                    # Close form
                    with st.form(f"close_{trade['id']}"):
                        exit_price = st.number_input("決済価格", min_value=0.0, step=1.0, key=f"ep_{trade['id']}")
                        exit_reason = st.text_input("決済理由", key=f"er_{trade['id']}")
                        if st.form_submit_button("クローズ"):
                            resp = httpx.post(
                                f"{API_BASE}/trade/{trade['id']}/close",
                                json={"exit_price": exit_price, "exit_reason": exit_reason},
                                timeout=10,
                            )
                            if resp.status_code == 200:
                                st.success("クローズしました")
                                st.rerun()

    # Closed trades
    with tab_closed:
        resp = httpx.get(f"{API_BASE}/trade/?status=closed", timeout=10)
        if resp.status_code == 200:
            trades = resp.json()
            if not trades:
                st.info("クローズ済みトレードはありません")
            for trade in trades:
                pnl = trade.get("pnl", 0)
                pnl_pct = trade.get("pnl_pct", 0)
                emoji = "🟢" if pnl and pnl > 0 else "🔴"
                with st.expander(f"{emoji} {trade['ticker']} {trade['direction'].upper()} P/L: {pnl_pct:.1f}%"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Entry**: {trade['entry_date']} @{trade['entry_price']}")
                    with col2:
                        st.markdown(f"**Exit**: {trade.get('exit_date')} @{trade.get('exit_price')}")
                    st.markdown(f"**根拠**: {trade.get('entry_reason', '')}")
                    st.markdown(f"**決済理由**: {trade.get('exit_reason', '')}")

except httpx.ConnectError:
    st.error("バックエンドに接続できません")
