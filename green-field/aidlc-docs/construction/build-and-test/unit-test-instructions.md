# Unit Test Execution

## Run Unit Tests

### 1. Execute All Unit Tests
```bash
source .venv/bin/activate
pytest -q
```

個別実行の例:
```bash
pytest tests/test_overlaps.py -q          # 重複判定の境界条件（純粋関数）
pytest tests/test_reservations_api.py -q  # 予約・重複防止
```

### 2. Review Test Results
- **期待**: 34 tests pass, 0 failures（検証済み）。
- **テスト内訳**:
  - `test_overlaps.py`: 7件（隣接/一致/内包/部分/前後）
  - `test_rooms_api.py`: 9件（CRUD・バリデーション・404）
  - `test_reservations_api.py`: 13件（作成・重複409・過去日時400・別室OK・キャンセル冪等・再予約 等）
  - `test_availability_api.py`: 5件（空き検索・隣接空き・キャンセルで空き・時刻順序400・空リスト）
- **カバレッジ方針**: 中核の重複防止ロジック（BR-OV）と主要APIパスを網羅。数値カバレッジ計測は任意（`pytest-cov` 追加で取得可能）。
- **許容警告**: `StarletteDeprecationWarning`（動作影響なし）。

### 3. Fix Failing Tests
テストが失敗した場合:
1. 失敗したテスト名と assert 内容を確認。
2. 対応する `app/` 側の実装（service / router）を修正。
3. `pytest -q` を再実行し、全件パスまで繰り返す。
