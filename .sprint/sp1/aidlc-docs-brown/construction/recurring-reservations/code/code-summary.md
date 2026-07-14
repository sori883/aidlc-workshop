# Code Summary — recurring-reservations

## 生成/変更ファイル一覧

### 新規（アプリ）
- `app/series/__init__.py` — パッケージ初期化
- `app/series/recurrence.py` — 週次生成の純粋関数 `generate_occurrences`
- `app/series/schemas.py` — `RecurringReservationCreate` / `RecurringReservationOut` / `SeriesOut`
- `app/series/repository.py` — `SeriesRepository`
- `app/series/service.py` — `RecurringReservationService`（create/cancel/get）
- `app/series/router.py` — `/reservations/recurring` エンドポイント群

### 変更（アプリ）
- `app/db/models.py` — `RecurrenceEndType` enum、`ReservationSeries` モデル追加、`Reservation.series_id` 列追加
- `app/db/database.py` — `create_all` に冪等な `_ensure_series_id_column`（既存DBへの列追加）
- `app/reservations/schemas.py` — `ReservationOut.series_id`（`str | None`, 既定 None）追加
- `app/reservations/repository.py` — `list_by_series` / `list_future_active_by_series` 追加
- `app/main.py` — `series_router` 登録（reservations より前）
- `requirements.txt` — `hypothesis` 追加

### 新規（テスト）
- `tests/test_recurrence.py` — 純粋関数の境界（count/until/上限/7日間隔/曜日）
- `tests/test_recurring_api.py` — API（作成/409全体拒否/検証/シリーズキャンセル/個別回キャンセル/照会/series_id表示）
- `tests/test_recurring_pbt.py` — PBT（Hypothesis）：往復・不変・生成器

### 変更（ドキュメント）
- `README.md` — 定期予約エンドポイントを API 概要へ追記

## ストーリー実装状況
| Story | 状態 | 実装箇所 |
|---|---|---|
| US-R01 シリーズ作成 | ✅ | recurrence/service/router/schemas/models |
| US-R02 全体拒否（原子性） | ✅ | service.create_series（has_conflict 再利用、単一 commit） |
| US-R03 入力検証 | ✅ | service + recurrence + Pydantic |
| US-R04 シリーズ全体キャンセル | ✅ | service.cancel_series（未来 active 回のみ） |
| US-R05 個別回キャンセル | ✅ | 既存 `/reservations/{id}/cancel` 流用（新規コードなし） |
| US-R06 series_id 表示 | ✅ | ReservationOut.series_id |
| US-R07 シリーズ照会 | ✅ | GET /reservations/recurring/{series_id} |
| US-R08 互換性維持 | ✅ | ReservationCreate 不変・availability 不変・既存テスト不改変 |

## 制約遵守
- C-1: `ReservationCreate` 不変、既存 API 契約不変。`ReservationOut` は Optional フィールド追加のみ。
- C-2: `app/availability/service.py`・`overlaps` 一切変更なし。
- C-3: HTTP ステータス（201/200/400/404/409/422）を既存 `common.errors` 経由で踏襲。
- C-4: 既存テスト未改変。新規テストは `brown.tests.conftest` 規約に準拠（test_recurring_api.py）。

## 検証は Build and Test フェーズで実施
- 既存テスト回帰 + 新規例示 + PBT の実行。
