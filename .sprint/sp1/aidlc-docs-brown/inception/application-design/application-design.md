# Application Design（統合）— 定期予約機能

本書は components.md / component-methods.md / services.md / component-dependency.md を統合した概要。

## 設計方針（承認済み決定）

- **配置**: 新規 `app.series` モジュール（router / service / schemas / repository / recurrence）。既存の縦割り構成に一貫。
- **日付生成**: `app/series/recurrence.py` に純粋関数として切り出し（`overlaps` と同じ設計思想。単体テスト/PBT 容易）。
- **永続化**: 新規 `SeriesRepository`。既存 `ReservationRepository` に series_id 検索メソッドを追加。
- **重複判定**: 既存 `AvailabilityService.has_conflict` を再利用（変更なし、C-2 遵守）。
- **後方互換**: `ReservationCreate` 不変、`ReservationOut` に `series_id` 追加のみ（C-1/C-4 遵守）。

## コンポーネント一覧

| ID | コンポーネント | 区分 | 概要 |
|---|---|---|---|
| C-1 | app.series.router | 新規 | シリーズ作成/全体キャンセル/照会エンドポイント |
| C-2 | app.series.service | 新規 | RecurringReservationService（オーケストレーション） |
| C-3 | app.series.recurrence | 新規(純粋) | 週次生成・終了条件解決 |
| C-4 | app.series.schemas | 新規 | Recurring 入出力スキーマ |
| C-5 | app.series.repository | 新規 | SeriesRepository |
| C-6 | app.db.models | 変更 | ReservationSeries 追加、Reservation.series_id 列 |
| C-7 | app.reservations.schemas | 変更 | ReservationOut に series_id |
| C-8 | app.reservations.repository | 変更 | series_id 検索メソッド追加 |
| C-9 | app.main | 変更 | series_router 登録 |
| R-1 | app.availability.service | 再利用 | has_conflict（不変） |
| R-2 | app.common | 再利用 | 例外/HTTP マッピング |
| R-3 | app.db.database | 再利用 | セッション/テーブル作成 |

## エンドポイント設計

| メソッド | パス | ユースケース | 主なステータス |
|---|---|---|---|
| POST | /reservations/recurring | シリーズ作成（US-R01/02/03） | 201 / 400 / 404 / 409 / 422 |
| POST | /reservations/recurring/{series_id}/cancel | シリーズ全体キャンセル（US-R04） | 200 / 404 |
| GET | /reservations/recurring/{series_id} | シリーズ照会（任意 US-R07） | 200 / 404 |
| POST | /reservations/{reservation_id}/cancel | 個別回キャンセル（US-R05、**既存流用**） | 200 / 404 |
| GET | /reservations, /reservations/{id} | series_id を含む照会（US-R06、**既存拡張**） | 200 / 404 |

## データモデル設計（高レベル）

- **ReservationSeries**: id(UUID), room_id(FK rooms), booker_name, booker_email(任意), 起点/繰り返しメタ（曜日・時刻・終了条件 count|until）, created_at。
- **Reservation（変更）**: `series_id`（String(36), NULL可, FK reservation_series.id）。単発は NULL。
- 詳細なカラム定義・制約は Functional Design で確定。

## ストーリー対応

| Story | 対応コンポーネント |
|---|---|
| US-R01 シリーズ作成 | C-1, C-2, C-3, C-4, C-5, C-6 |
| US-R02 全体拒否(原子性) | C-2 + R-1 |
| US-R03 入力検証 | C-2, C-3 |
| US-R04 シリーズ全体キャンセル | C-1, C-2, C-8 |
| US-R05 個別回キャンセル | 既存 reservations（変更なし） |
| US-R06 series_id 表示 | C-7, C-8 |
| US-R07 シリーズ照会(任意) | C-1, C-2 |
| US-R08 互換性維持 | C-1(パス非衝突), C-7(後方互換), R-1(不変) |

## 設計の完全性・一貫性チェック

- [x] 既存の単発予約 API 契約は不変（ReservationCreate 変更なし、ReservationOut は追加のみ）— C-1
- [x] 半開区間ロジックは availability.service を変更せず再利用 — C-2
- [x] HTTP ステータス方針は既存の common.errors マッピングを流用 — C-3
- [x] 既存テストは不変。新規テストは brown.tests.conftest 規約に合わせる — C-4
- [x] 新規エンドポイントのパスは既存ルートと非衝突（/reservations/recurring）
- [x] 全ユーザーストーリー（US-R01〜R08）にコンポーネントを割当済み
