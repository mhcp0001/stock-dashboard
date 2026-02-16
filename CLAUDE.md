# Stock Dashboard

## 言語設定

日本語で応答してください。

## プロジェクト概要

スイングトレード（数日〜数週間）を支援する株式分析ダッシュボード。
LLM対話 × テクニカル分析 × トレードジャーナル（Obsidian連携）。

## アーキテクチャ

```
frontend/ (Streamlit)  →  backend/ (FastAPI)  →  yfinance (株価データ)
                                ↓                     Claude API (LLM分析)
                           SQLite (trades/watchlist)
                                ↓
                        Obsidian Vault (トレードジャーナル書き出し)
```

## 技術スタック

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy + yfinance + pandas_ta + anthropic SDK
- **Frontend**: Streamlit (Phase 1 MVP) → Next.js (Phase 2)
- **LLM**: Claude Sonnet 4.5 (通常分析) / Opus (重要判断時)
- **DB**: SQLite (Phase 1) → PostgreSQL (Phase 2)
- **Infrastructure**: Docker Compose → Proxmox VM150

## ディレクトリ構造

```
backend/
  app/
    main.py          # FastAPIエントリーポイント
    routers/         # APIエンドポイント (market, analysis, trade, watchlist)
    services/        # ビジネスロジック (stock_data, technical, llm, obsidian)
    models/          # Pydanticスキーマ
    db/              # SQLAlchemy モデル + DB接続
frontend/
  app.py             # Streamlitメイン
  pages/             # chat, watchlist, journal
```

## 開発コマンド

```bash
# バックエンド起動
cd backend && pip install -e . && uvicorn app.main:app --reload

# フロントエンド起動
cd frontend && streamlit run app.py

# Docker起動
docker compose up --build

# テスト
cd backend && pytest
```

## Git運用

- 日本語コミットメッセージ + 絵文字マーカー
- Co-Authored-By: Claude <noreply@anthropic.com> 必須

## Phase ロードマップ

- **Phase 1 (MVP)**: Streamlit + FastAPI + Claude API + Obsidian書き出し + SQLite
- **Phase 2**: Next.js移行, Lightweight Charts, スクリーニング, アラート
- **Phase 3**: 自動統計分析, 月次レビュー, バックテスト
- **Phase 4**: MCP Server化, J-Quants移行, PWA
