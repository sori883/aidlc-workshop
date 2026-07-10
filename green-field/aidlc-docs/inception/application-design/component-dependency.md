# コンポーネント依存関係 (Component Dependencies)

## 依存マトリクス
| 依存元 \ 依存先 | RoomRepo | ReservationRepo | AvailabilityService | DB(SQLite) |
|---|---|---|---|---|
| RoomService | ✓ | | | (via repo) |
| ReservationService | ✓ | ✓ | ✓ | (via repo) |
| AvailabilityService | ✓ | ✓ | | (via repo) |
| RoomRepository | | | | ✓ |
| ReservationRepository | | | | ✓ |

## 通信パターン
- すべて **同一プロセス内の関数呼び出し**（ローカル単一 FastAPI アプリ）。
- 外部サービス・ネットワーク通信なし。
- DB アクセスは SQLAlchemy セッションを FastAPI の依存性注入 (Depends) で各リクエストに供給。

## レイヤとデータフロー（テキスト図）

```
[HTTP Client / Swagger UI]
        |
        v
+-----------------------------+
|  API Layer (FastAPI router) |   rooms_router, reservations_router
+-----------------------------+
        |
        v
+-----------------------------+
|  Service Layer              |   RoomService, ReservationService, AvailabilityService
+-----------------------------+
        |
        v
+-----------------------------+
|  Repository Layer           |   RoomRepository, ReservationRepository
+-----------------------------+
        |
        v
+-----------------------------+
|  Persistence (SQLAlchemy)   |   ORM models -> SQLite file
+-----------------------------+
```

## 予約作成フロー（重複防止）テキスト図

```
POST /reservations
   |
   v
ReservationService.create_reservation
   |-- validate(start < end, booker_name)
   |-- RoomRepository.get(room_id) --> 無ければ 404
   |-- AvailabilityService.has_conflict(room_id, start, end)
   |        |-- ReservationRepository.find_active_overlapping(...)
   |        `-- overlaps() 半開区間判定
   |-- conflict? --> Yes: 409 Conflict
   |            --> No : ReservationRepository.create(...) --> 201 Created
   v
Reservation
```

## 循環依存チェック
- Service → Repository → DB の一方向。循環依存なし。
- AvailabilityService は Repository のみに依存し、他 Service には依存しない（ReservationService から一方向に利用される）。
