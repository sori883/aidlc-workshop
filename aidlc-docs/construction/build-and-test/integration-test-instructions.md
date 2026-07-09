# Integration Test Instructions

## Purpose
本システムは**単一ユニット（モノリス）**のため、ユニット間の分散連携はない。
ここでの「統合テスト」は、モジュール（router → service → repository → SQLite）を通した
**エンドツーエンドのAPIフロー**を検証することを指す。既存のAPIテスト（`tests/test_*_api.py`）が
実DB（一時SQLite）を用いた統合テストを兼ねている。

## Test Scenarios

### Scenario 1: 会議室登録 → 予約作成 → 重複拒否（中核フロー）
- **説明**: 会議室を作成し、予約を1件入れ、同じ時間帯の重複予約が 409 で拒否されることを確認。
- **セットアップ**: 一時SQLite（conftest が自動生成）。
- **手順**:
  1. `POST /rooms` で会議室作成（201）。
  2. `POST /reservations`（10:00-11:00, 201）。
  3. `POST /reservations`（10:30-10:45, 内包 → 409）。
- **期待結果**: 3が 409。既存予約は不変。
- **クリーンアップ**: 一時DBファイルはテスト終了時に自動削除。
- **対応テスト**: `tests/test_reservations_api.py::test_overlapping_reservation_conflict_409`

### Scenario 2: 予約 → キャンセル → 空き復活 → 再予約
- **説明**: キャンセルにより時間帯が解放され、空き検索と再予約が成功することを確認。
- **手順**:
  1. 予約作成（201）。
  2. `POST /reservations/{id}/cancel`（200, status=cancelled）。
  3. `GET /availability` で当該会議室が空きに含まれる。
  4. 同時間帯を再予約（201）。
- **期待結果**: 3で会議室が空き、4が成功。
- **対応テスト**: `test_cancelled_slot_can_be_rebooked`, `test_cancelled_reservation_frees_room`

### Scenario 3: 会議室削除の制約
- **説明**: active 予約がある会議室は削除できない（409）。予約が無ければ削除できる（204）。
- **対応テスト**: `tests/test_rooms_api.py::test_delete_room`（正常）＋ サービス仕様（BR-R6）

## Setup / Run
```bash
source .venv/bin/activate
# APIテスト（統合フローを含む）を実行:
pytest tests/test_rooms_api.py tests/test_reservations_api.py tests/test_availability_api.py -q
```

### 手動での確認（起動して curl / Swagger UI）
```bash
uvicorn app.main:app --port 8000
# http://127.0.0.1:8000/docs から一連のフローを実行
```

## Cleanup
- 自動テスト: 一時DBは自動削除。
- 手動確認: ルートに生成された `reservations.db` を削除すればデータ初期化。
