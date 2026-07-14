# Unit Test Execution

## Run Unit Tests

### 1. 全テスト実行
```bash
# リポジトリルート（brown-field/）から
pytest
```

### 2. 結果（実測 2026-07-10）
- **合計**: 66 passed, 0 failed
- **既存（回帰）**: 34 passed（test_overlaps 7 / test_rooms_api 9 / test_reservations_api 13 / test_availability_api 5）— **既存テスト未改変で全パス（C-4 充足）**
- **新規**: 32 passed
  - `test_recurrence.py`: 9（純粋関数の境界: count/until/上限/7日間隔/曜日）
  - `test_recurring_api.py`: 18（作成/全体拒否409/検証/シリーズ・個別キャンセル/照会/series_id 表示）
  - `test_recurring_pbt.py`: 5（Hypothesis: 不変・往復・境界）

### 3. カテゴリ別実行
```bash
# 純粋関数
pytest tests/test_recurrence.py
# API
pytest tests/test_recurring_api.py
# PBT（Hypothesis）
pytest tests/test_recurring_pbt.py
# 既存回帰のみ
pytest tests/test_overlaps.py tests/test_rooms_api.py tests/test_reservations_api.py tests/test_availability_api.py
```

### 4. PBT（Hypothesis）の seed 再現性（PBT-08）
- 失敗時は Hypothesis が最小反例と seed を出力。再現は `pytest --hypothesis-seed=<seed>`。
- shrinking は既定で有効（無効化していない）。

### 5. 失敗時
1. 出力の失敗テストを特定
2. コード修正
3. 全パスまで再実行
