# Code Generation 計画 — Unit-1: reservation-service

**この計画が Code Generation の唯一の正典 (single source of truth) である。**

## ユニット・コンテキスト
- **ユニット**: Unit-1 会議室予約サービス（モノリス、単一 FastAPI アプリ）
- **実装ストーリー**: US-01 〜 US-08（全8本）
- **ユニット依存**: なし（単一ユニット）
- **所有エンティティ**: Room, Reservation
- **技術**: Python 3.11+ / FastAPI / SQLAlchemy 2.x / Pydantic v2 / SQLite / pytest + httpx

## コード配置（ワークスペースルート直下）
アプリコードは `app/`、テストは `tests/` に配置（ドキュメントは aidlc-docs/ のみ）。

```
app/
  __init__.py
  main.py                # FastAPI 生成・router登録・起動時テーブル作成
  core/
    __init__.py
    config.py            # DATABASE_URL/HOST/PORT
  db/
    __init__.py
    database.py          # engine/SessionLocal/Base/get_db
    models.py            # Room, Reservation (ORM)
  common/
    __init__.py
    exceptions.py        # NotFoundError, ConflictError, ValidationError系
    errors.py            # 例外→HTTPException ハンドラ登録
  rooms/
    __init__.py
    schemas.py           # RoomCreate/RoomUpdate/RoomOut
    repository.py        # RoomRepository
    service.py           # RoomService
    router.py            # /rooms
  reservations/
    __init__.py
    schemas.py           # ReservationCreate/ReservationOut
    repository.py        # ReservationRepository
    service.py           # ReservationService
    router.py            # /reservations
  availability/
    __init__.py
    service.py           # overlaps/has_conflict/find_available_rooms
    schemas.py           # AvailabilityQuery/結果
    router.py            # /availability
tests/
  __init__.py
  conftest.py            # テスト用DB(インメモリ/一時)・TestClient
  test_overlaps.py       # overlaps 純粋関数（境界条件）
  test_rooms_api.py      # 会議室 CRUD API
  test_reservations_api.py  # 予約作成/一覧/取得/キャンセル + 重複防止
  test_availability_api.py  # 空き検索
requirements.txt
README.md
.gitignore
```

## 実行ステップ（番号付き・チェックボックス）

- [x] **Step 1: プロジェクト構造セットアップ**（greenfield）: ディレクトリ・`__init__.py`・`.gitignore`・`requirements.txt` 作成
- [x] **Step 2: 永続化基盤生成**: `app/core/config.py`, `app/db/database.py`（engine/session/Base/get_db）, `app/db/models.py`（Room/Reservation, インデックス reservations(room_id,status)）
- [x] **Step 3: 共通例外/エラーハンドラ生成**: `app/common/exceptions.py`, `app/common/errors.py`（例外→400/404/409）
- [x] **Step 4: ビジネスロジック生成 — Availability**: `app/availability/service.py`（overlaps/has_conflict/find_available_rooms）… US-05, US-08
- [x] **Step 5: リポジトリ層生成**: `app/rooms/repository.py`, `app/reservations/repository.py`
- [x] **Step 6: サービス層生成**: `app/rooms/service.py`（CRUD + 削除時active予約チェック）, `app/reservations/service.py`（作成時トランザクションで重複防止/キャンセル冪等）… US-01〜US-07
- [x] **Step 7: スキーマ(DTO)生成**: `app/rooms/schemas.py`, `app/reservations/schemas.py`, `app/availability/schemas.py`
- [x] **Step 8: API層(router)生成**: `app/rooms/router.py`, `app/reservations/router.py`, `app/availability/router.py`
- [x] **Step 9: アプリ組み立て**: `app/main.py`（FastAPI・router登録・起動時 create_all・例外ハンドラ登録）
- [x] **Step 10: ユニットテスト生成 — overlaps**: `tests/test_overlaps.py`（隣接OK/一致・内包・部分NG/別室…境界網羅）… US-05
- [x] **Step 11: APIテスト生成**: `tests/conftest.py`, `tests/test_rooms_api.py`, `tests/test_reservations_api.py`（重複=409, 過去日時=400, キャンセル冪等 等）, `tests/test_availability_api.py`… US-01〜US-08
- [x] **Step 12: ドキュメント生成**: `README.md`（起動手順・API概要）, `aidlc-docs/construction/reservation-service/code/` にコードサマリ(md)
- [x] **Step 13: デプロイ成果物**: `requirements.txt` 確定（Step1 と整合）、起動コマンドを README に明記
- [x] **Step 14: 全ストーリー実装の確認**（US-01〜US-08 の [x] 化）

## ストーリー・トレーサビリティ
| Step | ストーリー |
|---|---|
| Step 4, 10 | US-05（重複判定） |
| Step 4, 8, 11 | US-08（空き検索） |
| Step 6, 8, 11 | US-01, US-02, US-03（会議室 CRUD） |
| Step 6, 8, 11 | US-04（予約作成）, US-06（予約一覧/取得）, US-07（キャンセル） |

## 生成方針
- 業務ルールは `aidlc-docs/construction/reservation-service/functional-design/business-rules.md` を厳守。
- HTTPステータスは business-rules.md のポリシー表に従う（201/200/204/400/404/409）。
- テストは重複防止の境界条件（BR-OV）を最優先で網羅。
- テストの実行は次の Build and Test 工程で行う（本工程では生成のみ）。
