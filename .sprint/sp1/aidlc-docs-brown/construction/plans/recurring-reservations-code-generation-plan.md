# Code Generation Plan — recurring-reservations

**このプランが Code Generation の唯一の真実源（single source of truth）。**

## Unit Context
- **Unit**: recurring-reservations（単一、モノリス内論理モジュール）
- **Stories**: US-R01〜US-R08
- **Workspace Root**: /Users/const/sori883/aidlc-workshop/brown-field
- **Project Type**: Brownfield（既存構造 `app/` を踏襲。ブラウンフィールドのため既存ファイルは in-place 変更、重複作成禁止）
- **Application Code**: `app/` 配下（NEVER aidlc-docs/）。ドキュメント要約は `aidlc-docs/construction/recurring-reservations/code/`。
- **依存/インターフェース**: 既存 `AvailabilityService.has_conflict`（不変再利用）、`common.exceptions`、`db.database`。
- **Owned Entities**: `ReservationSeries`（新）、`Reservation.series_id`（列追加）。

## 制約（厳守）
- C-1: `ReservationCreate` 不変、既存単発 API 契約不変。
- C-2: `availability.service` / `overlaps` 不変。
- C-3: HTTP ステータス方針踏襲。
- C-4: 既存テスト改変不可・全パス。新規テストは `brown.tests.conftest` 規約に準拠。

## 生成ステップ（順序 = 実装クリティカルパス）

### Step 1: データモデル層（変更）— db.models
- [x] `app/db/models.py` を**変更**: `ReservationSeries` モデル追加、`Reservation` に `series_id: Mapped[str | None]`（FK reservation_series.id, nullable）追加、リレーション設定。
- Story: US-R01, US-R06。

### Step 2: マイグレーション/テーブル作成（変更）— db.database
- [x] `app/db/database.py` の `create_all()` を**変更**: 冪等な `_ensure_series_id_column(engine)` ヘルパを追加し、`reservations` に `series_id` 列が無ければ `ALTER TABLE ... ADD COLUMN`（PRAGMA table_info 判定）。
- Infra: infrastructure-design.md。

### Step 3: ビジネスロジック層（新規）— series.recurrence（純粋関数）
- [x] `app/series/__init__.py`（新規・空）
- [x] `app/series/recurrence.py`（新規）: `generate_occurrences(start_time, end_time, count, until, max_count=52)` 純粋関数。
- Story: US-R01, US-R03。BR-RS-G*, BR-RS-C6/C7。

### Step 4: スキーマ層（新規 + 変更）
- [x] `app/series/schemas.py`（新規）: `RecurringReservationCreate`, `RecurringReservationOut`, `SeriesOut`。
- [x] `app/reservations/schemas.py` を**変更**: `ReservationOut` に `series_id: str | None` 追加（ReservationCreate は不変）。
- Story: US-R01, US-R04, US-R06, US-R07。BR-RS-D1。

### Step 5: リポジトリ層（新規 + 変更）
- [x] `app/series/repository.py`（新規）: `SeriesRepository`（add / get）。
- [x] `app/reservations/repository.py` を**変更**: `list_by_series`, `list_future_active_by_series` 追加（既存メソッド不変）。
- Story: US-R01, US-R04, US-R07。

### Step 6: サービス層（新規）— series.service
- [x] `app/series/service.py`（新規）: `RecurringReservationService`（create_series / cancel_series / get_series）。`AvailabilityService.has_conflict` 再利用、原子的登録。
- Story: US-R01, US-R02, US-R03, US-R04, US-R07。BR-RS-C*/OV*/X*/Q*。

### Step 7: API 層（新規 + 変更）
- [x] `app/series/router.py`（新規）: `POST /reservations/recurring`, `POST /reservations/recurring/{series_id}/cancel`, `GET /reservations/recurring/{series_id}`。
- [x] `app/main.py` を**変更**: `series_router` を登録。
- Story: US-R01, US-R04, US-R07, US-R08。

### Step 8: 依存追加（変更）— requirements.txt
- [x] `requirements.txt` を**変更**: `hypothesis` 追加（バージョン未固定）。
- NFR: PBT-09。

### Step 9: テスト（新規）— 例示ベース
- [x] `tests/test_recurrence.py`（新規）: `generate_occurrences` の境界（count/until/上限/7日間隔）。
- [x] `tests/test_recurring_api.py`（新規）: シリーズ作成/全体拒否409/検証/シリーズキャンセル/個別回キャンセル/series_id 表示/シリーズ照会。`brown.tests.conftest` 規約準拠。
- Story: US-R01〜R08。

### Step 10: テスト（新規）— PBT（Hypothesis, Partial）
- [x] `tests/test_recurring_pbt.py`（新規）: PBT-02（schemas round-trip）、PBT-03（generate_occurrences 不変・series_id 一貫）、PBT-07（ドメイン生成器）、PBT-08（seed/shrinking は Hypothesis 既定）。
- NFR: PBT-02/03/07/08/09。

### Step 11: ドキュメント要約（新規）
- [x] `aidlc-docs/construction/recurring-reservations/code/code-summary.md`（生成/変更ファイル一覧、ストーリー対応）。
- [x] `README.md` を**変更**: 定期予約エンドポイントを API 概要に追記。

## ファイル変更サマリ（予定）
**新規**: app/series/{__init__,recurrence,schemas,repository,service,router}.py、tests/{test_recurrence,test_recurring_api,test_recurring_pbt}.py
**変更**: app/db/models.py、app/db/database.py、app/reservations/schemas.py、app/reservations/repository.py、app/main.py、requirements.txt、README.md

## Story Traceability
| Story | Steps |
|---|---|
| US-R01 | 1,3,4,5,6,7,9,10 |
| US-R02 | 6,9,10 |
| US-R03 | 3,6,9,10 |
| US-R04 | 5,6,7,9 |
| US-R05 | 9（既存 API 流用、新規コードなし） |
| US-R06 | 1,4,9 |
| US-R07 | 4,5,6,7,9 |
| US-R08 | 4,7,9（回帰: 既存テスト全パス確認は Build & Test） |
