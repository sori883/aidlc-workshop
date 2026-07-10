# Integration Test Instructions

## Purpose
定期予約（app.series）と既存モジュール（reservations / availability / rooms / db）が
連携して正しく動作することを検証する。単一プロセス・単一DBのため、FastAPI TestClient を
用いた API 結合テストで代替する（別サービス起動は不要）。

## Test Scenarios（実施済み・自動E2Eで確認）

### Scenario 1: series → availability 統合（重複防止の一貫性）
- **説明**: シリーズ各回の重複判定に既存 `AvailabilityService.has_conflict` が使われる。
- **手順**: 既存単発予約と重なる回を含むシリーズ作成。
- **期待**: 全体拒否 409、DB に1件も追加されない（原子性）。
- **確認**: `test_recurring_api.py::test_conflict_rejects_whole_series_atomically`、E2E スモークで 409 を確認。

### Scenario 2: series → reservations 個別キャンセル統合
- **説明**: シリーズの各回は通常の Reservation。既存 `POST /reservations/{id}/cancel` で個別キャンセル可能。
- **期待**: 対象回のみ cancelled、他は active。
- **確認**: `test_recurring_api.py::test_individual_occurrence_cancel_via_existing_api`。

### Scenario 3: series → reservations 一覧表示統合（series_id）
- **説明**: `GET /reservations` のレスポンスに series_id が含まれる。単発は null。
- **確認**: `test_series_id_shown_in_listing` / `test_single_reservation_has_null_series_id`。

### Scenario 4: db マイグレーション統合（既存DB）
- **説明**: 既存 `reservations.db` に対し `create_all()` が `reservation_series` 作成 + `series_id` 列追加（冪等）。
- **手順**: 既存DBのコピーに `create_all()` を2回実行。
- **期待**: 列/テーブルが追加され、再実行してもエラーなし。既存データ保持。
- **確認**: マイグレーション検証スクリプト（Build and Test 実行時に確認済み）。

## Run
```bash
# 結合シナリオは API テストに内包。全実行:
pytest
```

## Cleanup
- テストは一時 SQLite を使用し自動破棄。追加のクリーンアップ不要。
