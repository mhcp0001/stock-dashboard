# Stock Dashboard デプロイガイド

## 対象環境

| 項目 | 値 |
|------|-----|
| ホスト | CT104 (LXC, Debian 12) |
| リソース | 512MB / 1CPU / 4GB disk |
| IP | 192.168.100.104 (VLAN 100) |
| 公開URL | stock.mhcp0001.dev → CF Access → Tunnel → Traefik → CT104 |

## ディレクトリ構成

```
/opt/stock-dashboard/
├── backend/
│   ├── .venv/           # Python 3.12 venv
│   └── app/             # FastAPI アプリ
├── frontend/
│   ├── .venv/           # Python 3.12 venv
│   └── app.py           # Streamlit アプリ
├── data/
│   └── stock.db         # SQLite
├── obsidian-vault/      # Obsidian連携 (optional)
└── .env                 # 環境変数 (Ansible Vault管理)
```

## セットアップ手順

### 1. システムユーザー作成

```bash
sudo useradd -r -s /usr/sbin/nologin -d /opt/stock-dashboard stock-dashboard
sudo mkdir -p /opt/stock-dashboard/data
```

### 2. コードの配置

```bash
sudo -u stock-dashboard git clone <repo-url> /opt/stock-dashboard/src
# backend/ と frontend/ を /opt/stock-dashboard/ に配置
```

### 3. venv作成 + 依存インストール

```bash
# Backend
cd /opt/stock-dashboard/backend
python3.12 -m venv .venv
.venv/bin/pip install -e .

# Frontend
cd /opt/stock-dashboard/frontend
python3.12 -m venv .venv
.venv/bin/pip install streamlit httpx
```

### 4. 環境変数

```bash
# dot-env.example を元に作成
sudo cp deploy/dot-env.example /opt/stock-dashboard/.env
sudo chown stock-dashboard:stock-dashboard /opt/stock-dashboard/.env
sudo chmod 600 /opt/stock-dashboard/.env
# ANTHROPIC_API_KEY を設定
```

### 5. systemd service インストール

```bash
sudo cp deploy/stock-dashboard-backend.service /etc/systemd/system/
sudo cp deploy/stock-dashboard-frontend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now stock-dashboard-backend stock-dashboard-frontend
```

### 6. 動作確認

```bash
systemctl status stock-dashboard-backend
systemctl status stock-dashboard-frontend
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8501/_stcore/health
```

## ローカル動作確認手順（開発機）

systemd service の ExecStart と同一コマンドでの手動起動テスト。

### Backend

```bash
cd backend/
python3.12 -m venv .venv        # 初回のみ
.venv/bin/pip install -e .       # 初回のみ

# ExecStart 再現（環境変数を手動設定）
DB_PATH=./data/stock.db \
OBSIDIAN_VAULT_PATH=/mnt/e/workspace/obsidian-vault \
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

# 確認
curl http://127.0.0.1:8000/api/health
# → {"status":"ok"}
```

### Frontend

```bash
cd frontend/
python3.12 -m venv .venv                  # 初回のみ
.venv/bin/pip install streamlit httpx      # 初回のみ

# ExecStart 再現
API_BASE=http://127.0.0.1:8000/api \
.venv/bin/streamlit run app.py \
    --server.port=8501 \
    --server.address=127.0.0.1 \
    --server.headless=true \
    --browser.gatherUsageStats=false

# 確認
curl http://127.0.0.1:8501/_stcore/health
# → ok
```

### 統合テスト

両方起動した状態で以下が全て200を返すこと:

```bash
# Backend API
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:8000/api/market/quote/7203.T
curl -s http://127.0.0.1:8000/api/market/indicators/7203.T
curl -s -X POST http://127.0.0.1:8000/api/analysis/chat \
  -H "Content-Type: application/json" -d '{"message":"test"}'
# → 503 (APIキー未設定時は正常)

# Frontend
curl -s http://127.0.0.1:8501/_stcore/health
curl -so /dev/null -w "%{http_code}" http://127.0.0.1:8501
curl -so /dev/null -w "%{http_code}" http://127.0.0.1:8501/pages/chat
curl -so /dev/null -w "%{http_code}" http://127.0.0.1:8501/pages/watchlist
curl -so /dev/null -w "%{http_code}" http://127.0.0.1:8501/pages/journal
```

## テスト結果（2026-02-19 ローカル検証）

| # | テスト | 結果 |
|---|--------|------|
| 1 | Backend health | PASS |
| 2 | Backend quote 7203.T | PASS |
| 3 | Backend indicators 7203.T | PASS |
| 4 | Backend analysis/chat (503) | PASS |
| 5 | Backend trade list | PASS |
| 6 | Backend watchlist list | PASS |
| 7 | Frontend streamlit health | PASS |
| 8 | Frontend main page | PASS |
| 9 | Frontend chat page | PASS |
| 10 | Frontend watchlist page | PASS |
| 11 | Frontend journal page | PASS |

**11/11 PASS** — systemd ExecStart と同一コマンドでの起動を確認済み。

## ログ確認

```bash
journalctl -u stock-dashboard-backend -f
journalctl -u stock-dashboard-frontend -f
```

## 再起動

```bash
sudo systemctl restart stock-dashboard-backend   # frontendも連動再起動
```
