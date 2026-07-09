# コード生成サマリ — reservation-service

## 生成したアプリケーションコード（ワークスペースルート `app/`）
| ファイル | 役割 | 関連ストーリー |
|---|---|---|
| `app/main.py` | FastAPI 生成、router 登録、起動時テーブル作成、例外ハンドラ登録 | 全体 |
| `app/core/config.py` | 設定（DATABASE_URL/HOST/PORT） | — |
| `app/db/database.py` | engine / SessionLocal / Base / get_db / create_all | — |
| `app/db/models.py` | ORM モデル Room, Reservation（UUID, index） | — |
| `app/common/exceptions.py` | ドメイン例外（NotFound/Conflict/Validation） | — |
| `app/common/errors.py` | 例外→HTTP（400/404/409）ハンドラ | — |
| `app/availability/service.py` | overlaps / has_conflict / find_available_rooms | US-05, US-08 |
| `app/availability/schemas.py` | 空き検索の応答スキーマ | US-08 |
| `app/availability/router.py` | GET /availability | US-08 |
| `app/rooms/repository.py` | RoomRepository | US-01〜03 |
| `app/rooms/service.py` | RoomService（削除時 active 予約チェック） | US-01, US-02, US-03 |
| `app/rooms/schemas.py` | RoomCreate/RoomUpdate/RoomOut | US-01〜03 |
| `app/rooms/router.py` | /rooms エンドポイント | US-01, US-02, US-03 |
| `app/reservations/repository.py` | ReservationRepository | US-04, US-06, US-07 |
| `app/reservations/service.py` | ReservationService（トランザクション重複防止/キャンセル冪等） | US-04, US-05, US-06, US-07 |
| `app/reservations/schemas.py` | ReservationCreate/ReservationOut | US-04, US-06 |
| `app/reservations/router.py` | /reservations エンドポイント | US-04, US-06, US-07 |

## 生成したテストコード（`tests/`）
| ファイル | 内容 |
|---|---|
| `tests/conftest.py` | 一時 SQLite・TestClient・get_db 差し替え・会議室作成ヘルパー |
| `tests/test_overlaps.py` | overlaps 境界条件（隣接/一致/内包/部分/前後） US-05 |
| `tests/test_rooms_api.py` | 会議室 CRUD・バリデーション・404 |
| `tests/test_reservations_api.py` | 予約作成・重複409・過去日時400・隣接OK・別室OK・キャンセル冪等・再予約 |
| `tests/test_availability_api.py` | 空き検索・隣接空き・キャンセルで空き・時刻順序400・空リスト |

## その他成果物
- `requirements.txt`（fastapi/uvicorn/sqlalchemy/pydantic/pytest/httpx）
- `README.md`（起動手順・API 一覧・ステータス方針）
- `.gitignore`（Python/SQLite 追加）

## 業務ルールの実装対応
- 重複判定は半開区間（`s1 < e2 and s2 < e1`）。隣接は非重複。→ `app/availability/service.py`
- 予約作成は「検証→会議室存在→過去日時→重複チェック→挿入→commit」の順（単一トランザクション）。
- 会議室削除は active 予約が1件でもあれば 409。
- キャンセルは冪等（cancelled への再要求も 200）。

## 備考
- テストの実行は次工程 Build and Test で行う。
- capacity 負数は Pydantic（ge=0）で 422、空 name などの業務検証は 400。
