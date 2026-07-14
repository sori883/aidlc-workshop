# サービス層定義 (Services)

サービス層は API層（router）から呼ばれ、リポジトリ層とドメインロジック（Availability）をオーケストレーションする。

## RoomService
- **責務**: 会議室 CRUD のユースケースを実現。
- **オーケストレーション**:
  - バリデーション（名前必須、収容人数 ≥ 0）を実施し、RoomRepository で永続化。
  - `delete_room` 時、その会議室に紐づく予約の扱いを決定（→ Functional Design で確定。デフォルト案: 紐づく予約も含めて削除、または予約があれば拒否）。

## ReservationService
- **責務**: 予約ユースケースの中核。作成時に必ず重複チェックを行う。
- **オーケストレーション（create_reservation）**:
  1. 入力バリデーション（start < end、booker_name 必須）。
  2. RoomRepository で room_id の存在確認（無ければ NotFound）。
  3. **AvailabilityService.has_conflict** で同一会議室・時間帯の active 予約重複を確認。
  4. 重複なし → ReservationRepository で作成。重複あり → Conflict（409）。
- **cancel_reservation**: 予約を取得し status を cancelled に更新（冪等な扱いは Functional Design で確定）。

## AvailabilityService
- **責務**: 重複判定（半開区間）と空き会議室検索の純粋ロジック。
- **オーケストレーション（find_available_rooms）**:
  1. RoomRepository で全会議室を取得。
  2. ReservationRepository で指定時間帯に重なる active 予約を持つ会議室を除外。
  3. 残った会議室一覧を返す。

## サービス間の関係
- ReservationService → AvailabilityService（重複チェック）
- ReservationService → RoomRepository（会議室存在確認）
- AvailabilityService → RoomRepository / ReservationRepository（検索・判定）
- RoomService → RoomRepository

## トランザクション方針（概略）
- 予約作成は「重複チェック→挿入」を1トランザクション内で行い、競合時の二重作成を避ける。
- 追加の保険として DB レベルの制約（部分ユニークインデックス等）は NFR Design / Functional Design で検討。
