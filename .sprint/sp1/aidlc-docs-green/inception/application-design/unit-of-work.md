# ユニット定義 (Unit of Work)

## 分解方針
- **決定**: 単一ユニット（モノリス）— Q-U1=A
- **理由**: ローカル完結・2〜3時間の制約・単一 SQLite。マイクロサービス分割は範囲を超えるため採用しない。
- **ユニット種別**: Service（1つの独立デプロイ可能なアプリ）。内部を論理 Module に分割する。

## Unit-1: 会議室予約サービス (Meeting Room Reservation Service)
- **責務**: 会議室 CRUD・予約 CRUD・重複防止・空き検索を提供する REST API 一式。
- **内部モジュール**:
  - `rooms` モジュール — Room コンポーネント（router/service/repository）
  - `reservations` モジュール — Reservation コンポーネント（router/service/repository）
  - `availability` モジュール — Availability コンポーネント（重複判定・空き検索ロジック）
  - `core` / `db` モジュール — 設定・DBセッション・ORMモデル基盤（Persistence）
- **含むストーリー**: US-01 〜 US-08（全ストーリー）
- **デプロイ**: 単一 uvicorn プロセス、単一 SQLite ファイル。

## コード構成戦略（Greenfield）
アプリコードはワークスペースルート直下の `app/` に配置する（ドキュメントは aidlc-docs/ のみ）。想定構成:

```
app/
  main.py                 # FastAPI エントリポイント、router 登録
  core/
    config.py             # 設定（DBパス等）
  db/
    database.py           # SQLAlchemy engine / session / Base
    models.py             # ORM モデル (Room, Reservation)
  rooms/
    router.py             # /rooms エンドポイント
    service.py            # RoomService
    repository.py         # RoomRepository
    schemas.py            # Pydantic DTO
  reservations/
    router.py             # /reservations エンドポイント
    service.py            # ReservationService
    repository.py         # ReservationRepository
    schemas.py            # Pydantic DTO
  availability/
    service.py            # AvailabilityService (overlaps/has_conflict/find_available_rooms)
    router.py             # /availability エンドポイント（空き検索）
tests/
  ...                     # pytest（重複防止の境界テスト中心）
requirements.txt
README.md
```
（最終的なファイル構成は Code Generation で確定する）

## ユニット数サマリ
- **総ユニット数**: 1
- **並行開発**: 不要（単一ユニット）
