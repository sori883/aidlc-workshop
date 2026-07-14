# System Architecture

## System Overview

Python + FastAPI + SQLAlchemy(2.0) + SQLite で実装された単一プロセスの REST API。レイヤードアーキテクチャ（Router → Service → Repository → ORM Model）を機能モジュール（rooms / reservations / availability）ごとに縦割りで構成する。ドメイン例外を HTTP ステータスへ変換する共通ハンドラを持つ。

## Architecture Diagram

```mermaid
flowchart TD
    subgraph API["FastAPI アプリ (app.main)"]
        RoomsR["rooms.router"]
        ResR["reservations.router"]
        AvailR["availability.router"]
        Handlers["common.errors 例外ハンドラ"]
    end

    subgraph Service["サービス層"]
        RoomsS["rooms.service"]
        ResS["reservations.service"]
        AvailS["availability.service"]
    end

    subgraph Repo["リポジトリ層"]
        RoomsRepo["rooms.repository"]
        ResRepo["reservations.repository"]
    end

    Models["db.models (Room, Reservation)"]
    DBsess["db.database (engine/session)"]
    DB[("SQLite")]

    RoomsR --> RoomsS --> RoomsRepo --> Models
    ResR --> ResS --> ResRepo --> Models
    ResS --> AvailS
    AvailR --> AvailS --> Models
    RoomsS --> Models
    Models --> DBsess --> DB
```

## Component Descriptions

### app.main
- **Purpose**: アプリ生成とルータ/例外ハンドラ登録、起動時テーブル作成。
- **Responsibilities**: `create_app()`、`/health`、`create_all()` の呼び出し。
- **Dependencies**: 各 router、common.errors、db.database。
- **Type**: Application

### rooms / reservations / availability（各モジュール）
- **Purpose**: それぞれ会議室・予約・空き検索の機能を提供。
- **Responsibilities**: router（HTTP 入出力）→ service（業務ルール）→ repository（永続化）の3層。availability は repository を持たず service が直接 ORM を照会。
- **Dependencies**: db.models、db.database、common.exceptions。reservations.service は availability.service に依存。
- **Type**: Application

### db.models / db.database
- **Purpose**: ORM モデル定義と SQLAlchemy エンジン/セッション管理。
- **Responsibilities**: Room・Reservation の定義、`get_db` 依存性、`create_all`。
- **Type**: Application (Data)

### common.exceptions / common.errors
- **Purpose**: ドメイン例外定義と HTTP マッピング。
- **Responsibilities**: `ValidationError`→400、`NotFoundError`→404、`ConflictError`→409。
- **Type**: Application (Cross-cutting)

## Data Flow

予約作成（BT-03）の主要フロー:

```mermaid
sequenceDiagram
    participant C as Client
    participant R as reservations.router
    participant S as reservations.service
    participant A as availability.service
    participant DB as SQLite

    C->>R: POST /reservations
    R->>S: create_reservation(...)
    S->>S: 時刻順序・予約者名・過去日時を検証
    S->>DB: 会議室存在確認
    S->>A: has_conflict(room_id, start, end)
    A->>DB: active 予約を走査し overlaps 判定
    A-->>S: 重複あり/なし
    alt 重複あり
        S-->>C: 409 Conflict
    else 重複なし
        S->>DB: INSERT reservation (commit)
        S-->>C: 201 Created
    end
```

## Integration Points
- **External APIs**: なし。
- **Databases**: SQLite（`reservations.db`、環境変数 `DATABASE_URL` で差し替え可）。
- **Third-party Services**: なし。

## Infrastructure Components
- **CDK Stacks**: なし。
- **Deployment Model**: `uvicorn app.main:app` によるローカル単一プロセス実行。
- **Networking**: 127.0.0.1:8000（既定、環境変数で変更可）。
