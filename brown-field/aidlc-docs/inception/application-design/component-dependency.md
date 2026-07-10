# Component Dependency — 定期予約機能

## 依存マトリクス

| コンポーネント | 依存先 | 種別 |
|---|---|---|
| app.series.router | app.series.service, app.series.schemas, db.database(get_db) | Runtime |
| app.series.service | app.series.recurrence, app.series.repository, reservations.repository, rooms.repository, availability.service, common.exceptions, db.models | Runtime |
| app.series.recurrence | （標準ライブラリ datetime のみ） | Runtime |
| app.series.repository | db.models, SQLAlchemy Session | Runtime |
| app.series.schemas | pydantic | Runtime |
| app.reservations.schemas (変更) | pydantic（series_id 追加のみ） | Runtime |
| app.reservations.repository (変更) | db.models（メソッド追加） | Runtime |
| app.db.models (変更) | db.database(Base)（ReservationSeries 追加、series_id 列） | Runtime |
| app.main (変更) | app.series.router（登録追加） | Runtime |

## 通信パターン

- すべて同一プロセス内の直接メソッド呼び出し（既存アーキテクチャ踏襲）。
- レイヤー: series.router → series.service → {recurrence(pure), repositories, availability.service} → db.models → db.database → SQLite。
- 例外は下位でドメイン例外として送出し、`common.errors` の FastAPI ハンドラで HTTP に変換（既存の仕組みを流用）。

## 依存グラフ

```mermaid
flowchart TD
    main["app.main (変更)"]
    sr["series.router (新)"]
    ss["series.service (新)"]
    rec["series.recurrence (新・純粋)"]
    ssch["series.schemas (新)"]
    srepo["series.repository (新)"]
    resrepo["reservations.repository (変更)"]
    roomrepo["rooms.repository (再利用)"]
    avail["availability.service (再利用/不変)"]
    models["db.models (変更)"]
    database["db.database (再利用)"]
    common["common.exceptions/errors (再利用)"]
    resschemas["reservations.schemas (変更: series_id)"]

    main --> sr
    sr --> ss
    sr --> ssch
    ss --> rec
    ss --> srepo
    ss --> resrepo
    ss --> roomrepo
    ss --> avail
    ss --> common
    ss --> models
    srepo --> models
    resrepo --> models
    models --> database
    avail --> models
    resschemas -.->|出力に series_id 追加| sr
```

## データフロー（新テーブル/列）

```mermaid
flowchart LR
    series["reservation_series<br/>(新テーブル)"]
    res["reservations<br/>(series_id 列追加, NULL可)"]
    rooms["rooms (不変)"]

    rooms -->|1..*| res
    series -->|1..*| res
```

## 影響範囲と後方互換

- **後方互換**: `ReservationCreate`（リクエスト）不変。`ReservationOut` は `series_id` 追加のみ（既存クライアント・既存テストは個別フィールド検証のため非破壊）。
- **DB マイグレーション**: 新テーブル追加は `create_all` で対応。既存 `reservations` への `series_id` 列追加は Infrastructure Design で手順を確定（新規DBは create_all、既存DBは ALTER 手順）。
- **半開区間ロジック**: availability.service を変更しないことで C-2 を保証。
