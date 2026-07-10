# NFR Design Patterns — recurring-reservations

## P-1: 原子的トランザクション（Unit of Work / Transaction Script）
- **対応 NFR**: NFR-RS-1（原子性）。
- **設計**: `RecurringReservationService.create_series` 内で、全回の重複チェック後に series + 全 Reservation を追加し、**単一 `db.commit()`** で確定。いずれかの回が重複した時点で ConflictError を送出し commit しない → セッションは未フラッシュ/ロールバックされ、DB に何も残らない。
- **根拠**: 既存 `ReservationService.create_reservation` の「チェック→add→commit」パターンを踏襲し一貫性を保つ。
- **注意**: `flush` は行うが `commit` は最後の1回のみ。例外時は FastAPI 依存性 `get_db` の `finally: db.close()` によりトランザクションは確定されない。

## P-2: 後方互換の追加専用拡張（Tolerant Reader / Additive Change）
- **対応 NFR**: NFR-RS-2（後方互換）。
- **設計**: `ReservationOut` に `series_id: str | None` を**追加のみ**。`ReservationCreate` は不変。既存の単発作成フローは `series_id` を設定しない（DB 既定 NULL）。
- **根拠**: 既存クライアント・既存テスト（個別フィールド検証）を壊さない。C-1/C-4 を満たす。

## P-3: 純粋関数の分離（Functional Core / Imperative Shell）
- **対応 NFR**: NFR-RS-4（保守性・テスト容易性）。
- **設計**: 週次生成・終了条件解決を `recurrence.py` の純粋関数に集約（Functional Core）。副作用（DB・トランザクション）は service（Imperative Shell）に隔離。
- **根拠**: 既存 `overlaps` と同じ思想。単体テスト/PBT を容易化。

## P-4: 例外→HTTP マッピングの再利用（Centralized Error Handling）
- **対応 NFR**: NFR-RS-3（信頼性）、C-3。
- **設計**: 新規 API も `ValidationError`/`NotFoundError`/`ConflictError` を送出し、既存 `common.errors` ハンドラで 400/404/409 に変換。Pydantic 制約違反は 422（FastAPI 標準）。
- **根拠**: HTTP ステータス方針の一貫性、service 層の HTTP 非依存維持。

## P-5: 重複判定ロジックの再利用（不変の共有カーネル）
- **対応 NFR**: NFR-RS-3、C-2。
- **設計**: `AvailabilityService.has_conflict` / `overlaps` を変更せずに各回へ適用。
- **根拠**: 半開区間ロジック（隣接OK・重なりNG）を単発・定期で同一に保つ。

## P-6: Property-Based Testing パターン（PBT Partial）
- **対応 NFR**: NFR-RS-6。
- **設計**:
  - **Round-trip（PBT-02）**: Recurring/Series スキーマの `model_validate` ↔ `model_dump` 往復が同値。
  - **Invariant（PBT-03）**: `generate_occurrences` の不変（生成数=count、7日間隔、until 境界）、シリーズ内 series_id 一貫、重複時0件（原子性）。
  - **Generators（PBT-07）**: 会議室ID・起点日時・count(1..52)・until のドメイン生成器を再利用可能に定義。
  - **Shrinking/seed（PBT-08）**: Hypothesis 既定の shrinking 有効、失敗時 seed をログ、CI で seed 記録。
  - **Framework（PBT-09）**: Hypothesis。

## 適用外パターン（明示）
| パターン | 判定 | 理由 |
|---|---|---|
| リトライ/サーキットブレーカ | N/A | 外部依存なし、単一プロセス |
| キャッシュ | N/A | 小規模・読み取り負荷低 |
| キュー/非同期 | N/A | 同期処理で十分 |
| 水平スケール/シャーディング | N/A | ローカル SQLite、スケール要件なし |
| 認証/認可/暗号化 | N/A | Security 拡張無効、スコープ外 |
