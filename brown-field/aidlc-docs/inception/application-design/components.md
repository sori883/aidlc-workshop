# Components — 定期予約機能

## 新規コンポーネント

### C-1: app.series.router
- **Purpose**: 定期予約シリーズの HTTP エンドポイントを提供。
- **Responsibilities**:
  - `POST /reservations/recurring`（シリーズ作成）
  - `POST /reservations/recurring/{series_id}/cancel`（シリーズ全体キャンセル）
  - `GET /reservations/recurring/{series_id}`（任意: シリーズ照会 US-R07）
- **Interfaces**: RecurringReservationCreate を受け取り、RecurringReservationOut / SeriesOut を返す。ドメイン例外は既存 `common.errors` ハンドラで HTTP 変換。
- **Note**: 個別回キャンセルは既存 `POST /reservations/{id}/cancel` を流用するため本 router には含めない。

### C-2: app.series.service（RecurringReservationService）
- **Purpose**: シリーズのユースケースをオーケストレーションする。
- **Responsibilities**:
  - シリーズ作成: 入力検証 → recurrence で全回生成 → 会議室存在確認 → 全回の重複チェック → 原子的に series + 全回を登録（1回でも重複なら全体拒否 409）。
  - シリーズ全体キャンセル: 未来の active 回のみ cancelled（冪等）。
  - シリーズ照会（任意）。
- **Interfaces**: `AvailabilityService.has_conflict` を再利用。`SeriesRepository` と `ReservationRepository` を利用。

### C-3: app.series.recurrence（純粋関数モジュール）
- **Purpose**: 週次の出現日時生成と終了条件解決を副作用なく行う。
- **Responsibilities**:
  - 起点 `start`/`end` と終了条件（`count` または `until`）から、各回の (start, end) タプル列を生成。
  - 7日刻み。`until` は開始日が until 以下の回まで。回数上限（52）の判定用に生成数を返す。
- **Interfaces**: 純粋関数（`generate_occurrences(...) -> list[tuple[datetime, datetime]]`）。DB 非依存。`overlaps` と同じ設計思想でテスト容易。

### C-4: app.series.schemas
- **Purpose**: シリーズの入出力スキーマ（Pydantic v2）。
- **Responsibilities**: RecurringReservationCreate（room_id, start_time, end_time, booker_name, booker_email?, count?, until?）、RecurringReservationOut（series_id, occurrences[]）、SeriesOut（メタ情報）。

### C-5: app.series.repository（SeriesRepository）
- **Purpose**: `reservation_series` テーブルの永続化アクセス。
- **Responsibilities**: series の追加・取得。

## 変更コンポーネント

### C-6: app.db.models（変更）
- **Purpose**: ORM モデル。
- **Change**:
  - 新規 `ReservationSeries` モデル（id, room_id, booker_name, booker_email, weekday, start_time_of_day/end_time_of_day 相当のメタ, 終了条件, created_at）。
  - `Reservation` に `series_id: str | None`（FK `reservation_series.id`、NULL可）列を追加。単発は NULL。

### C-7: app.reservations.schemas（変更）
- **Purpose**: 予約の入出力スキーマ。
- **Change**: `ReservationOut` に `series_id: str | None` を追加（単発は null）。**リクエストスキーマ ReservationCreate は不変**（C-1 遵守）。

### C-8: app.reservations.repository（軽微変更）
- **Purpose**: 予約の永続化。
- **Change**: `list_by_series(series_id)` / `list_future_active_by_series(series_id, now)` などの検索メソッドを追加（既存メソッドは不変）。

### C-9: app.main（変更）
- **Purpose**: アプリ生成。
- **Change**: `series_router` を登録。

## 再利用（変更なし）コンポーネント

### R-1: app.availability.service
- **Reuse**: `has_conflict(room_id, start, end)` を各回の重複チェックにそのまま利用。半開区間ロジック不変（C-2 遵守）。`find_available_rooms` はシリーズ回も active 予約として自然に考慮される。

### R-2: app.common（exceptions / errors）
- **Reuse**: ValidationError(400) / NotFoundError(404) / ConflictError(409) をそのまま利用。

### R-3: app.db.database
- **Reuse**: `get_db`、`Base`、`create_all`。新テーブルは `create_all` で作成される。
