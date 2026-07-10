# 論理コンポーネント構成 (Logical Components) — reservation-service

NFR パターンを反映した論理コンポーネント。追加インフラ部品（キュー/キャッシュ/CB）は無し。

## 論理コンポーネント一覧
| コンポーネント | 種別 | 役割 | 関連パターン |
|---|---|---|---|
| API Routers | 境界 | HTTP エンドポイント、DTO 変換、例外→HTTP マッピング | P1, P5 |
| Pydantic Schemas | 境界 | リクエスト/レスポンスのバリデーション | P4 |
| Services (Room/Reservation/Availability) | アプリケーション | 業務ロジック、トランザクション制御 | P1, P3, P4 |
| Repositories (Room/Reservation) | 永続化 | SQLAlchemy によるデータアクセス | P1 |
| DB Session Provider | 基盤 | Depends によるセッション注入・クローズ | P2 |
| ORM Models + Engine | 基盤 | テーブル定義、SQLite 接続、インデックス | P3 |
| Domain Exceptions | 横断 | NotFound / Conflict / Validation を表現 | P5 |

## 論理構成図（テキスト）

```
        HTTP (Swagger UI / client)
                 |
        +--------v---------+
        |   API Routers    |  rooms / reservations / availability
        |  (+Schemas P4)   |
        +--------+---------+
                 |  DTO
        +--------v---------+
        |    Services      |  業務ロジック / トランザクション(P3)
        +--------+---------+
                 |
        +--------v---------+
        |  Repositories    |  SQLAlchemy クエリ
        +--------+---------+
                 |  session (P2 DI)
        +--------v---------+
        | ORM Models/Engine|  -> SQLite file
        +------------------+

   Domain Exceptions ---(P5)--> Routers で HTTP ステータスへ変換
```

## データストア設計上の要点
- **テーブル**: `rooms`, `reservations`。
- **インデックス**: `reservations(room_id, status)` を付与し、重複チェック（対象会議室の active 予約走査）と空き検索を効率化。
- **リレーション**: `reservations.room_id` → `rooms.id`（外部キー相当。SQLite では外部キー制約は任意で有効化）。

## トランザクション境界
- 予約作成 UC-3 のみ「チェック→挿入」を明示的な単一トランザクションで囲む。
- その他の単純な CRUD は1操作＝1トランザクション（ORM 既定）。
