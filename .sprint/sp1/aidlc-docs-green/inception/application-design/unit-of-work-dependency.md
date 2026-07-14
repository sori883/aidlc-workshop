# ユニット依存関係 (Unit of Work Dependencies)

## ユニット間依存
- 総ユニット数は **1**（会議室予約サービス）。
- **ユニット間依存は存在しない**（単一ユニットのため）。

## ユニット内モジュール依存マトリクス
| 依存元 \ 依存先 | rooms | reservations | availability | db/core |
|---|---|---|---|---|
| rooms | — | | | ✓ |
| reservations | (room存在確認) ✓ | — | ✓ | ✓ |
| availability | ✓ | ✓ | — | ✓ |
| db/core | | | | — |

## 補足
- `reservations` は予約作成時に `rooms`（会議室存在確認）と `availability`（重複チェック）を利用。
- `availability` は `rooms` / `reservations` のリポジトリを参照して判定・検索を行う。
- 依存方向は一方向で循環なし（詳細は application-design/component-dependency.md 参照）。

## 更新戦略
- 単一ユニットのため、更新順序・並行化の考慮は不要。
- テストは1ユニット内で完結（ユニットテスト＋統合テスト）。
