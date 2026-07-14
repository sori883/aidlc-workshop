# デプロイアーキテクチャ (Deployment Architecture) — reservation-service

## デプロイモデル
- **形態**: ローカル単一プロセス実行（開発者マシン）。
- **デプロイ単位**: 1つの FastAPI アプリ（Unit-1）。
- **プロセス**: `uvicorn` により起動。1インスタンス。

## セットアップ手順（想定・Code Generation で README に反映）
```
# 1. 仮想環境
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. 依存インストール
pip install -r requirements.txt

# 3. 起動（初回起動時にテーブル自動作成）
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 4. 動作確認
#    ブラウザで http://127.0.0.1:8000/docs (Swagger UI)
```

## データライフサイクル
- 初回起動時に SQLite ファイルとテーブルを自動生成（存在しなければ作成）。
- データはファイルに永続化。削除したい場合は `reservations.db` を削除して再起動。
- テスト実行時は本番ファイルと分離（インメモリ or 一時ファイル DB を使用）。

## 起動時処理
1. 設定読込（DATABASE_URL / HOST / PORT）。
2. SQLAlchemy エンジン生成・`Base.metadata.create_all()` でテーブル作成。
3. FastAPI アプリに各 router を登録。
4. uvicorn が待受開始。

## 運用上の注意
- 単一ユーザー〜少人数のローカル利用向け。公開サーバーへの配置は本設計の対象外。
- バックアップは `reservations.db` ファイルのコピーで代替可能（手動）。

## ロールバック
- コード: git で戻す。
- データ: `reservations.db` を以前のコピーに差し替え。
