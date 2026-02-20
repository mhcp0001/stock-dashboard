"""LLM integration for stock analysis.

Supports multiple providers via LLM_PROVIDER env var:
- "gemini" (default): Google Gemini API
- "anthropic": Anthropic Claude API
"""

import os
import uuid

import anthropic
from google import genai
from google.genai import types

# In-memory conversation store: {conversation_id: [messages]}
_conversations: dict[str, list[dict]] = {}

_anthropic_client: anthropic.Anthropic | None = None
_gemini_client: genai.Client | None = None

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


def get_provider() -> str:
    """Get the configured LLM provider."""
    return os.getenv("LLM_PROVIDER", "gemini").lower()


def _get_anthropic_client() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        _anthropic_client = anthropic.Anthropic(api_key=api_key)
    return _anthropic_client


def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


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


def _chat_anthropic(
    message: str,
    conversation_id: str,
    context: str,
    model: str,
) -> str:
    """Send a message via Anthropic Claude API."""
    client = _get_anthropic_client()

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
    return assistant_text


def _chat_gemini(
    message: str,
    conversation_id: str,
    context: str,
    model: str,
) -> str:
    """Send a message via Google Gemini API."""
    client = _get_gemini_client()

    full_message = f"{context}\n\n---\n\n{message}" if context else message

    # Convert existing conversation history to Gemini format
    history = []
    for msg in _conversations[conversation_id]:
        role = "model" if msg["role"] == "assistant" else msg["role"]
        history.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    response = client.models.generate_content(
        model=model,
        contents=history + [types.Content(role="user", parts=[types.Part.from_text(text=full_message)])],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2048,
        ),
    )

    assistant_text = response.text
    # Store in common format for consistency
    _conversations[conversation_id].append({"role": "user", "content": full_message})
    _conversations[conversation_id].append({"role": "assistant", "content": assistant_text})
    return assistant_text


# Default models per provider
_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5-20250929",
    "gemini": "gemini-2.5-flash",
}


def chat(
    message: str,
    conversation_id: str | None = None,
    context: str = "",
    model: str | None = None,
) -> tuple[str, str]:
    """Send a message to the configured LLM and get a response.

    Returns (response_text, conversation_id).
    """
    provider = get_provider()

    if model is None:
        model = _DEFAULT_MODELS.get(provider, _DEFAULT_MODELS["gemini"])

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in _conversations:
        _conversations[conversation_id] = []

    if provider == "anthropic":
        text = _chat_anthropic(message, conversation_id, context, model)
    elif provider == "gemini":
        text = _chat_gemini(message, conversation_id, context, model)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")

    return text, conversation_id
