# NFR Requirements — recurring-reservations

## スコープ前提
社内向け・小規模・SQLite ローカル実行のワークショップアプリ。高負荷・HA・DR・タイムゾーンはスコープ外（Vision / requirements NFR-5）。Security/Resiliency 拡張は無効。

## NFR 一覧

### NFR-RS-1: データ整合性 / 原子性（最重要）
- シリーズ作成は**全成功または全ロールバック**。重複チェック（各回 `has_conflict`）と series + 全回 INSERT を**単一トランザクション**内で実施。1回でも重複なら 409 で何も残さない。
- 検証: US-R02 の AC-2（409 後に0件）。

### NFR-RS-2: 後方互換性
- 既存の単発予約 API のリクエスト/レスポンス契約を破壊しない。`ReservationCreate` 不変、`ReservationOut` は `series_id` 追加のみ（Optional）。
- 既存テストを一切改変せず全パス（C-4）。新規テストは `brown.tests.conftest` 規約に準拠。
- 検証: US-R08 の AC-1〜AC-5。

### NFR-RS-3: 信頼性 / エラーハンドリング
- ドメイン例外→HTTP（400/404/409/422）を既存 `common.errors` で一元処理。新規 API も同方針（C-3）。
- 半開区間ロジックを変更しないことで重複判定の一貫性を担保（C-2）。

### NFR-RS-4: 保守性 / テスト容易性
- 週次生成・終了条件解決を純粋関数（`recurrence`）に分離し、DB 非依存で単体テスト/PBT 可能。
- 既存のレイヤード構成（router/service/repository）を踏襲し、既存モジュールと一貫。

### NFR-RS-5: パフォーマンス（軽量要件）
- 1シリーズ最大52回のため、作成時の重複チェックは最大52回 × 会議室の active 予約走査。小規模前提で許容。既存 `has_conflict` の実装（room_id, status インデックス利用）をそのまま活用。
- 明示的な応答時間 SLA は設定しない（社内小規模）。

### NFR-RS-6: テスト（PBT Partial）
- PBT-02（Round-trip）: schemas のシリアライズ↔デシリアライズ往復。
- PBT-03（Invariant）: `generate_occurrences` の不変条件（生成数=count、7日間隔、until 境界）、series_id 一貫性、原子性（重複時は0件）。
- PBT-07（Generator quality）: 会議室・日時・count/until のドメイン生成器。
- PBT-08（Shrinking/reproducibility）: Hypothesis の shrinking 有効、seed ログ。
- PBT-09（Framework）: Hypothesis を選定・依存追加。
- 例示ベーステスト（PBT-10 は Partial では助言）: 主要 AC を例示テストでピン留め。

## 非対象（明示）
- スケーラビリティ（水平/自動スケール）、可用性（HA/フェイルオーバー）、DR、認証/認可、監視/アラート、タイムゾーン。
