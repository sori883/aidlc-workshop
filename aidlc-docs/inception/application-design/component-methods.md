# コンポーネントのメソッド定義 (Component Methods)

> 注: 詳細な業務ルール（バリデーションの厳密仕様・境界条件など）は Functional Design で確定する。
> ここでは高レベルのシグネチャと入出力を定義する。ID はすべて UUID 文字列 (`str`)。

## RoomService（C1）
| メソッド | 目的 | 入力 | 出力 |
|---|---|---|---|
| `create_room(data)` | 会議室を作成 | RoomCreate(name, capacity, equipment[], location) | Room |
| `get_room(room_id)` | 会議室を取得 | room_id: str | Room（無ければ NotFound） |
| `list_rooms()` | 会議室一覧 | なし | list[Room] |
| `update_room(room_id, data)` | 会議室を更新 | room_id: str, RoomUpdate | Room |
| `delete_room(room_id)` | 会議室を削除 | room_id: str | None（NotFound あり） |

## ReservationService（C2）
| メソッド | 目的 | 入力 | 出力 |
|---|---|---|---|
| `create_reservation(data)` | 予約を作成（重複チェック込み） | ReservationCreate(room_id, start_time, end_time, booker_name, booker_email?) | Reservation（重複時 Conflict） |
| `get_reservation(res_id)` | 予約を取得 | res_id: str | Reservation（無ければ NotFound） |
| `list_reservations(room_id?, from?, to?)` | 予約一覧（絞り込み可） | room_id?: str, from?: datetime, to?: datetime | list[Reservation] |
| `cancel_reservation(res_id)` | 予約をキャンセル | res_id: str | Reservation（status=cancelled） |

## AvailabilityService（C3）
| メソッド | 目的 | 入力 | 出力 |
|---|---|---|---|
| `overlaps(start_a, end_a, start_b, end_b)` | 2区間の重なり判定（半開区間） | 4 × datetime | bool |
| `has_conflict(room_id, start, end)` | 指定会議室・時間帯に active 予約の重複があるか | room_id: str, start, end | bool |
| `find_available_rooms(start, end)` | 空き会議室検索（US-08） | start, end: datetime | list[Room] |

## 入出力スキーマ（DTO 概略）
- **RoomCreate / RoomUpdate**: name: str, capacity: int, equipment: list[str], location: str
- **Room（応答）**: id: str, name, capacity, equipment, location, created_at
- **ReservationCreate**: room_id: str, start_time: datetime, end_time: datetime, booker_name: str, booker_email: str | None
- **Reservation（応答）**: id: str, room_id, start_time, end_time, booker_name, booker_email, status, created_at

## 状態遷移
- Reservation.status: `active` → `cancelled`（cancel_reservation により遷移）。
- 重複判定は status=`active` の予約のみ対象。
