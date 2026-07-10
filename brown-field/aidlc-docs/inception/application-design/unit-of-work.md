# Unit of Work — 定期予約機能

## Unit: recurring-reservations

- **種別**: Module（既存 FastAPI モノリス内の論理モジュール。独立デプロイ不要）
- **目的**: 週次定期予約の作成・シリーズ全体キャンセル・シリーズ照会を提供し、既存の予約照会にシリーズ情報を後方互換で付与する。
- **責務**:
  - 定期予約シリーズの原子的作成（重複時は全体拒否）
  - シリーズ全体キャンセル（未来 active 回のみ、冪等）
  - シリーズ情報の表示（series_id）と任意のシリーズ照会
  - 既存の単発予約 API・既存テスト・半開区間ロジックの不変性維持

### 含むコンポーネント

**新規（app.series モジュール）**
- `app/series/__init__.py`
- `app/series/router.py`
- `app/series/service.py`（RecurringReservationService）
- `app/series/schemas.py`
- `app/series/repository.py`（SeriesRepository）
- `app/series/recurrence.py`（純粋関数）

**変更（既存モジュール、後方互換）**
- `app/db/models.py`（ReservationSeries 追加、Reservation.series_id 列）
- `app/reservations/schemas.py`（ReservationOut に series_id）
- `app/reservations/repository.py`（series_id 検索メソッド追加）
- `app/main.py`（series_router 登録）

**再利用（変更なし）**
- `app/availability/service.py`（has_conflict）
- `app/common/*`（例外/HTTP マッピング）
- `app/db/database.py`（セッション/テーブル作成）

### 含むストーリー
US-R01, US-R02, US-R03, US-R04, US-R05, US-R06, US-R07, US-R08

### コード編成（Brownfield — 既存構造踏襲）
既存の縦割りモジュール構成（rooms / reservations / availability と同様）に沿って `app/series/` を追加。アプリケーションコードはワークスペースルートの `app/` 配下（aidlc-docs 配下には置かない）。テストは `tests/` に追加し、既存の `brown.tests.conftest` インポート規約に合わせる。

### 独立性・見積り
- **独立性**: 既存機能に対して追加的。既存 API 契約・テストへ非破壊。
- **見積り**: 中規模（新モジュール1 + 既存4ファイルの軽微変更 + テスト）。
- **テスト**: 既存テスト全パス（回帰）+ 新規（例示 + PBT Partial）。
