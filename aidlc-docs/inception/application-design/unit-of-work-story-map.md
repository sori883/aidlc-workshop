# ストーリー・ユニット対応表 (Unit of Work — Story Map)

すべてのストーリーは単一ユニット **Unit-1: 会議室予約サービス** に割り当てられる。

| ストーリー | 概要 | 担当モジュール | ユニット |
|---|---|---|---|
| US-01 | 会議室を登録する | rooms | Unit-1 |
| US-02 | 会議室の一覧・詳細を見る | rooms | Unit-1 |
| US-03 | 会議室を更新・削除する | rooms | Unit-1 |
| US-04 | 会議室を予約する | reservations（+rooms, availability） | Unit-1 |
| US-05 | 重複予約を拒否される | availability | Unit-1 |
| US-06 | 予約の一覧・詳細を見る | reservations | Unit-1 |
| US-07 | 予約をキャンセルする | reservations | Unit-1 |
| US-08 | 空いている会議室を検索する | availability（+rooms, reservations） | Unit-1 |

## カバレッジ検証
- [x] 全8ストーリーがユニットに割当済み（未割当なし）。
- [x] 各ストーリーの担当モジュールが明確。
- [x] ユニット境界は単一で、境界越えの依存なし。
