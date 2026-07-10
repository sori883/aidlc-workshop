# NFR 設計パターン (NFR Design Patterns) — reservation-service

ローカル・低同時実行・単一 SQLite という制約に見合った、軽量なパターンのみを採用する。

## 採用パターン

### P1. レイヤードアーキテクチャ (Layered Architecture)
- **対応NFR**: NFR-M1（保守性）
- **適用**: router（HTTP/DTO）→ service（業務ロジック）→ repository（永続化）→ SQLite。
- **効果**: 責務分離によりテスト容易性と可読性を確保。業務ルールを service に集約。

### P2. 依存性注入 (Dependency Injection) によるDBセッション管理
- **対応NFR**: NFR-M1, NFR-R1
- **適用**: FastAPI の `Depends` でリクエストスコープの SQLAlchemy セッションを注入。リクエスト終了時にクローズ。
- **効果**: セッションのライフサイクルを一元管理。テストでセッションを差し替え可能。

### P3. トランザクション整合性による重複防止 (Check-Then-Insert in a Transaction)
- **対応NFR**: NFR-R1（データ整合性・中核）
- **適用**: 予約作成時、同一トランザクション内で「active予約の重複チェック → 挿入 → コミット」を実施。
- **補助**: 重複判定を高速化するため、`reservations(room_id, status)` にインデックスを付与し、対象会議室の active 予約のみを走査。
- **効果**: 低同時実行下で二重予約を防止。SQLite の書き込み直列化とも整合。

### P4. 入力バリデーション (Validation at the Edge)
- **対応NFR**: NFR-R2, NFR-S2
- **適用**: Pydantic スキーマで型・必須を検証（router 層）。業務的制約（start<end、過去日時、capacity≥0 等）は service 層で検証。
- **効果**: 不正入力を早期に 400 で弾く。SQL は ORM 経由でパラメータ化され SQLi を回避。

### P5. 例外→HTTPステータスの一貫マッピング (Error Mapping)
- **対応NFR**: NFR-R2
- **適用**: ドメイン例外を定義し、FastAPI の例外ハンドラ or HTTPException で対応:
  - ValidationError系 → 400
  - NotFound（room/reservation） → 404
  - Conflict（重複予約 / active予約ありの会議室削除） → 409
- **効果**: エラー応答の一貫性。クライアントが機械的に判別可能。

## 明示的に不採用（N/A）とするパターン
| パターン | 理由 |
|---|---|
| リトライ / サーキットブレーカー | 外部依存なし・ローカル完結のため不要 |
| キャッシュ層 | データ量小・SQLite ローカルで即応 |
| メッセージキュー / 非同期ワーカー | 同期処理で十分。ジョブなし |
| 水平スケール / ロードバランサ | 単一プロセス前提 |
| 認証・認可ミドルウェア | 要件によりスコープ外 |

## 対応表（NFR → パターン）
| NFR | 対応パターン |
|---|---|
| NFR-R1 データ整合性 | P3（+P2） |
| NFR-R2 エラーハンドリング | P4, P5 |
| NFR-S2 入力対策 | P4 |
| NFR-M1 保守性 | P1, P2 |
