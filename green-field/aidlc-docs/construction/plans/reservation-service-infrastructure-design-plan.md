# Infrastructure Design 計画 — Unit-1: reservation-service

## 質問カテゴリの評価（適用可否）
制約「ローカル実行で完結」（NFR-01）によりインフラ選択は確定済み。新規の質問は不要（曖昧点なし）。

| カテゴリ | 適用 | 判断 |
|---|---|---|
| Deployment Environment | 確定 | ローカルマシン（開発者PC）。クラウドなし |
| Compute Infrastructure | 確定 | uvicorn プロセス（単一）。コンテナ/VM/サーバーレスなし |
| Storage Infrastructure | 確定 | SQLite ファイル（ローカル）。RDS等なし |
| Messaging Infrastructure | N/A | キュー/イベント基盤なし |
| Networking Infrastructure | 限定的 | localhost:8000。LB/API Gateway なし |
| Monitoring Infrastructure | 限定的 | 標準出力ログのみ。監視基盤なし |
| Shared Infrastructure | N/A | 単一ユニット・共有基盤なし |

## 実行チェックリスト
- [x] infrastructure-design.md 生成（論理→インフラのマッピング）
- [x] deployment-architecture.md 生成（ローカル配置と起動手順）
