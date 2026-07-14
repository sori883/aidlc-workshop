# Build Instructions

## Prerequisites
- **ランタイム**: Python 3.13
- **依存**: `requirements.txt`（fastapi / uvicorn[standard] / sqlalchemy>=2.0 / pydantic>=2.0 / pytest / httpx / **hypothesis**）
- **環境変数**（任意・既定あり）: `DATABASE_URL`（既定 `sqlite:///./reservations.db`）, `HOST`, `PORT`
- **システム要件**: 追加なし（ローカル実行）

## Build Steps

### 1. 仮想環境と依存インストール
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 環境設定（任意）
```bash
# 既定で ./reservations.db を使用。別DBを使う場合のみ:
export DATABASE_URL="sqlite:///./reservations.db"
```

### 3. 起動（＝スキーマ自動反映）
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- 起動時に `create_all()` が実行され、`reservation_series` テーブル作成と、既存
  `reservations` への `series_id` 列追加（冪等な自動 ALTER）が行われる。

### 4. ビルド成功の確認
- **期待**: 起動ログにエラーなし。`http://127.0.0.1:8000/docs` で定期予約エンドポイントが表示される。
- **生成物**: SQLite DB（`reservations.db`）に `reservation_series` と `reservations.series_id`。

## Troubleshooting

### `No module named 'brown'`（テスト収集時）
- **原因**: テストが規約 `from brown.tests.conftest import create_room` を使用。
- **解決**: ルート `conftest.py` が `brown` エイリアスを登録するため、リポジトリルート（`brown-field/`）から `pytest` を実行すれば解決する。

### 依存エラー
- **解決**: 仮想環境を有効化し `pip install -r requirements.txt` を再実行。
