"""Claude API integration for stock analysis."""

import os
import uuid

import anthropic

_client: anthropic.Anthropic | None = None
# In-memory conversation store: {conversation_id: [messages]}
_conversations: dict[str, list[dict]] = {}

SYSTEM_PROMPT = """あなたは株式スイングトレード（数日〜数週間の短中期売買）の分析アシスタントです。

## 役割
- テクニカル・ファンダメンタル両面から銘柄を分析
- エントリー/イグジットのタイミングについて客観的な見解を提示
- リスク要因を必ず併記（楽観バイアスを避ける）
- 過去のトレード実績がある場合、パターンを踏まえた助言

## 制約
- 投資助言ではなく分析支援であることを認識
- 「絶対」「必ず」等の断定表現を避ける
- データが不十分な場合は明示する
- 日本語で回答

## 出力フォーマット
分析時は以下の構造で回答:
1. **サマリー**: 1-2文で結論
2. **テクニカル分析**: 提供された指標の解釈
3. **注目ポイント**: エントリー/イグジットの判断材料
4. **リスク**: 下落シナリオや注意点
"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def build_context(ticker: str | None = None, indicators: dict | None = None, trade_stats: dict | None = None) -> str:
    """Build contextual data string to prepend to user message."""
    parts = []

    if ticker and indicators:
        parts.append(f"## {ticker} テクニカルデータ")
        for key, value in indicators.items():
            if key == "date":
                parts.append(f"- データ日付: {value}")
            elif key == "rsi_14":
                parts.append(f"- RSI(14): {value}")
            elif key == "macd":
                parts.append(f"- MACD: {value} / Signal: {indicators.get('macd_signal', 'N/A')}")
            elif key == "bb_position":
                parts.append(f"- BB位置: {value} (0=下限, 1=上限)")
            elif key == "volume_ratio":
                parts.append(f"- 出来高倍率(vs 20日平均): {value}x")
            elif key == "sma_20":
                parts.append(f"- SMA20: {value} / SMA50: {indicators.get('sma_50', 'N/A')}")

    if trade_stats:
        parts.append("\n## 過去のトレード実績")
        for key, value in trade_stats.items():
            parts.append(f"- {key}: {value}")

    return "\n".join(parts)


def chat(
    message: str,
    conversation_id: str | None = None,
    context: str = "",
    model: str = "claude-sonnet-4-5-20250929",
) -> tuple[str, str]:
    """Send a message to Claude and get a response.

    Returns (response_text, conversation_id).
    """
    client = _get_client()

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in _conversations:
        _conversations[conversation_id] = []

    # Prepend context to user message if available
    full_message = f"{context}\n\n---\n\n{message}" if context else message

    _conversations[conversation_id].append({"role": "user", "content": full_message})

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=_conversations[conversation_id],
    )

    assistant_text = response.content[0].text
    _conversations[conversation_id].append({"role": "assistant", "content": assistant_text})

    return assistant_text, conversation_id
