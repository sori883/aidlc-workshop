# Build Instructions

## Prerequisites
- **言語/ランタイム**: Python 3.11 以上（検証は 3.13 で実施）
- **ビルドツール**: pip（venv）
- **依存**: `requirements.txt`（fastapi, uvicorn[standard], sqlalchemy>=2.0, pydantic>=2.0, pytest, httpx）
- **環境変数**（任意・既定値あり）:
  - `DATABASE_URL`（既定 `sqlite:///./reservations.db`）
  - `HOST`（既定 `127.0.0.1`）
  - `PORT`（既定 `8000`）
- **システム要件**: 一般的なPCで可。追加のDBサーバー・クラウド不要。

## Build Steps

### 1. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# 通常は不要（既定値で動作）。変更したい場合のみ:
export DATABASE_URL="sqlite:///./reservations.db"
export HOST=127.0.0.1
export PORT=8000
```

### 3. Build All Units
```bash
# Python はコンパイル済みビルド成果物を必要としない。
# 構文チェック（任意）:
python -m py_compile app/*.py app/**/*.py
```

### 4. Verify Build Success
- **期待される出力**: 構文エラーなし。`uvicorn app.main:app` が起動し `/docs` が表示される。
- **成果物**: 実行時に `reservations.db`（SQLite ファイル）が自動生成される。
- **許容される警告**: `StarletteDeprecationWarning`（TestClient の httpx 利用に関する非推奨警告。動作に影響なし）。

## 起動確認
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
# 別ターミナルで:
curl http://127.0.0.1:8000/health   # {"status":"ok"}
```

## Troubleshooting

### 依存インストールに失敗する
- **原因**: ネットワーク / pip が古い。
- **対処**: `python -m pip install --upgrade pip` 後に再実行。

### 起動時に ModuleNotFoundError: app
- **原因**: リポジトリのルート以外から起動している。
- **対処**: ワークスペースルート（`app/` がある階層）で `uvicorn app.main:app` を実行する。
