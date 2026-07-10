# Unit of Work — Story Map（定期予約機能）

すべてのストーリーは単一ユニット `recurring-reservations` に割り当てられる。

## ストーリー↔ユニット マッピング

| Story | 概要 | Unit | 主担当コンポーネント |
|---|---|---|---|
| US-R01 | 定期予約シリーズの作成 | recurring-reservations | series.router / service / recurrence / schemas / repository / db.models |
| US-R02 | 重複時のシリーズ全体拒否（原子性） | recurring-reservations | series.service + availability.service（再利用） |
| US-R03 | 作成時の入力検証 | recurring-reservations | series.service / recurrence |
| US-R04 | シリーズ全体キャンセル（未来 active 回のみ） | recurring-reservations | series.router / service / reservations.repository |
| US-R05 | 個別回キャンセル（既存 API 流用） | recurring-reservations | 既存 reservations（変更なし） |
| US-R06 | 予約一覧・詳細でのシリーズ情報表示 | recurring-reservations | reservations.schemas（series_id）/ repository |
| US-R07 | シリーズ単位の照会（任意） | recurring-reservations | series.router / service |
| US-R08 | 既存 API・既存テストの不変性維持 | recurring-reservations | 横断（設計制約 C-1〜C-4） |

## カバレッジ確認
- [x] 全8ストーリーがユニットに割当済み
- [x] 未割当ストーリーなし
- [x] ユニット境界は「予約」ドメイン内の定期予約サブ機能として一貫
- [x] US-R05/US-R08 は既存資産の再利用/制約であり、新規コンポーネントを増やさない

## 次段階（CONSTRUCTION — recurring-reservations ユニット）
Per-Unit Loop を本ユニットに対して実行:
1. Functional Design（series データモデル・recurrence ロジック・原子的重複処理、PBT-01 property 識別）
2. NFR Requirements（原子性・後方互換・PBT フレームワーク Hypothesis 選定）
3. NFR Design（トランザクション境界・後方互換方式・PBT パターン）
4. Infrastructure Design（テーブル作成/マイグレーション方針）
5. Code Generation（実装）
その後 Build and Test。
