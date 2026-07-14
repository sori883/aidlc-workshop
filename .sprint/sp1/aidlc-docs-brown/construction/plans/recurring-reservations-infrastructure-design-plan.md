# Infrastructure Design Plan — recurring-reservations

## Approved Decision（対話形式で取得、2026-07-10）

### Q1: 既存 reservations.db へのスキーマ反映
[Answer]: 軽量な自動 ALTER ヘルパ。起動時に create_all（新テーブル作成）に加え、reservations に series_id 列が無ければ ALTER TABLE で追加する冪等ヘルパーを導入。既存DB・新規DB ともシームレスに動作。

## カテゴリ適用性評価
- **Deployment Environment**: ローカル単一プロセス（uvicorn）。クラウドなし。
- **Compute**: ローカルホスト。N/A（スケールなし）。
- **Storage**: SQLite（既存 reservations.db）。新テーブル + 列追加。
- **Messaging**: N/A。
- **Networking**: 127.0.0.1:8000（既存設定）。API Gateway/LB なし。
- **Monitoring**: N/A（Resiliency 無効）。
- **Shared Infrastructure**: なし（共有インフラ文書は不要）。

## Execution Checklist
- [x] infrastructure-design.md — インフラマッピングとマイグレーション方針
- [x] deployment-architecture.md — デプロイ構成（ローカル）
