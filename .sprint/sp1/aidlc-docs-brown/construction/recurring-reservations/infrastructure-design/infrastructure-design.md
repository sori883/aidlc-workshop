# Infrastructure Design — recurring-reservations

## 概要
既存のローカル実行モデル（uvicorn + SQLite）を踏襲。クラウド・コンテナ・IaC は導入しない。本ユニットのインフラ関心事は**スキーマ反映（マイグレーション）**のみ。

## 論理→インフラ マッピング

| 論理コンポーネント | インフラ実体 | 備考 |
|---|---|---|
| Recurring API Boundary | uvicorn(ASGI) 上の FastAPI ルート | 既存プロセスに同居 |
| Recurring Orchestrator / Core | 同一プロセスの Python モジュール | 追加インフラなし |
| Series/Reservation Persistence | SQLite ファイル（reservations.db） | 新テーブル + 列追加 |
| Conflict Kernel / Error Mapping | 同一プロセス（再利用） | 変更なし |

## スキーマ反映（マイグレーション方針）

### 決定: 軽量な自動 ALTER ヘルパ（冪等）
既存 `create_all()` を拡張し、起動時に以下を冪等に実施:

1. `Base.metadata.create_all(bind=engine)` — 未作成テーブル（`reservation_series`）を作成。
2. **列追加ヘルパ**: `reservations` テーブルに `series_id` 列が存在しなければ `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を実行。
   - 存在チェックは `PRAGMA table_info(reservations)` の結果で判定（SQLite）。
   - 既に列があれば何もしない（冪等）。

### 擬似コード（Infrastructure 指針。実装は Code Generation で確定）
```python
def create_all() -> None:
    from app.db import models  # マッパー登録
    Base.metadata.create_all(bind=engine)
    _ensure_series_id_column(engine)   # 冪等な列追加ヘルパ

def _ensure_series_id_column(engine) -> None:
    # PRAGMA table_info(reservations) に series_id が無ければ ADD COLUMN
    ...
```

### 特性・制約
- **冪等**: 複数回起動しても安全。
- **SQLite 限定**: `PRAGMA table_info` / `ADD COLUMN` は SQLite 前提（既存も SQLite 固定）。FK 制約は SQLite の ADD COLUMN では厳密に付与できないため、`series_id` はアプリ層で整合を担保（ORM リレーション）。
- **テストへの影響なし**: テストは毎回一時DBを `metadata.create_all` で構築するため、ORM モデルに `series_id` を定義すれば新規テーブルとして列も含まれる。ALTER ヘルパは既存ファイルDB向けの保険。
- **新規DB**: `reservations.db` を削除して再作成した場合も create_all で全スキーマが揃う。

## ネットワーク / デプロイ
- 変更なし。`uvicorn app.main:app --host 127.0.0.1 --port 8000`（既存 README）。

## 監視・ロギング
- 追加なし（Resiliency 拡張無効）。エラーは HTTP ステータス + detail。
