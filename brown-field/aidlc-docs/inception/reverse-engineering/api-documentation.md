# API Documentation

## REST APIs

### 会議室登録
- **Method**: POST
- **Path**: `/rooms`
- **Purpose**: 会議室を登録する。
- **Request**: `{ name, capacity(>=0), equipment[], location }`
- **Response**: 201 `RoomOut`。name 空は 400、capacity 負数は 422。

### 会議室一覧 / 詳細
- **Method**: GET
- **Path**: `/rooms`, `/rooms/{room_id}`
- **Response**: 200 `RoomOut` / `list[RoomOut]`。詳細で未存在は 404。

### 会議室更新
- **Method**: PUT
- **Path**: `/rooms/{room_id}`
- **Request**: `{ name, capacity, equipment[], location }`
- **Response**: 200 `RoomOut`。未存在 404、name 空 400、capacity 負数 422。

### 会議室削除
- **Method**: DELETE
- **Path**: `/rooms/{room_id}`
- **Response**: 204。未存在 404。active な予約があると 409。

### 予約作成
- **Method**: POST
- **Path**: `/reservations`
- **Purpose**: 会議室・時間帯・予約者を指定して予約する。
- **Request**: `{ room_id, start_time, end_time, booker_name, booker_email? }`
- **Response**: 201 `ReservationOut`。時刻順序違反/予約者名空/過去日時は 400、会議室未存在 404、重複は 409。

### 予約一覧
- **Method**: GET
- **Path**: `/reservations?room_id=&from_time=&to_time=`
- **Purpose**: 予約を絞り込み取得。期間は半開区間の重なりで判定。
- **Response**: 200 `list[ReservationOut]`。

### 予約詳細
- **Method**: GET
- **Path**: `/reservations/{reservation_id}`
- **Response**: 200 `ReservationOut`。未存在 404。

### 予約キャンセル
- **Method**: POST
- **Path**: `/reservations/{reservation_id}/cancel`
- **Purpose**: 予約を取り消す（冪等）。
- **Response**: 200 `ReservationOut`（status=cancelled）。未存在 404。既に cancelled でも 200。

### 空き会議室検索
- **Method**: GET
- **Path**: `/availability?start_time=&end_time=`
- **Purpose**: 指定時間帯に active 予約が重ならない会議室を返す。
- **Response**: 200 `AvailableRoomsOut { start_time, end_time, available_rooms[] }`。時刻順序違反は 400。

### ヘルスチェック
- **Method**: GET
- **Path**: `/health`
- **Response**: 200 `{ "status": "ok" }`。

## Internal APIs

### AvailabilityService
- **Methods**:
  - `overlaps(start_a, end_a, start_b, end_b) -> bool`（モジュール関数）: 半開区間の重なり判定。
  - `has_conflict(room_id, start, end, exclude_reservation_id=None) -> bool`: 対象会議室の active 予約との重複有無。
  - `find_available_rooms(start, end) -> list[Room]`: 空き会議室一覧。

### ReservationService
- **Methods**: `create_reservation`, `get_reservation`, `list_reservations`, `cancel_reservation`。

### RoomService
- **Methods**: `create_room`, `get_room`, `list_rooms`, `update_room`, `delete_room`。

## Data Models

### Room
- **Fields**: id(str/UUID), name, capacity(int), equipment(list[str]、JSON文字列で保存), location, created_at。
- **Relationships**: reservations（1対多、cascade all, delete-orphan）。
- **Validation**: name 必須、capacity >= 0。

### Reservation
- **Fields**: id(str/UUID), room_id(FK), start_time, end_time, booker_name, booker_email(任意), status(active/cancelled), created_at。
- **Relationships**: room（多対1）。
- **Validation**: start_time < end_time、booker_name 必須、start_time は現在以降、時間帯重複なし。
- **Index**: `ix_reservations_room_id_status` (room_id, status)。
