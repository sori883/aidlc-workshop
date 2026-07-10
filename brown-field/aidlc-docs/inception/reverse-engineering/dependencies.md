# Dependencies

## Internal Dependencies

```mermaid
flowchart TD
    main["app.main"]
    rooms_r["rooms.router"]
    rooms_s["rooms.service"]
    rooms_repo["rooms.repository"]
    res_r["reservations.router"]
    res_s["reservations.service"]
    res_repo["reservations.repository"]
    avail_r["availability.router"]
    avail_s["availability.service"]
    models["db.models"]
    database["db.database"]
    common["common.exceptions / errors"]
    core["core.config"]

    main --> rooms_r
    main --> res_r
    main --> avail_r
    main --> common
    main --> database

    rooms_r --> rooms_s --> rooms_repo --> models
    res_r --> res_s --> res_repo --> models
    res_s --> avail_s
    res_s --> rooms_repo
    avail_r --> avail_s --> models

    rooms_s --> common
    res_s --> common
    database --> core
    models --> database
```

### reservations.service depends on availability.service
- **Type**: Runtime
- **Reason**: 予約作成時に `has_conflict` で重複チェックを行うため。

### reservations.service depends on rooms.repository
- **Type**: Runtime
- **Reason**: 予約作成前に対象会議室の存在確認を行うため。

### 各 service depends on common.exceptions
- **Type**: Runtime
- **Reason**: 業務エラーをドメイン例外として送出するため。

### db.database depends on core.config
- **Type**: Runtime
- **Reason**: `DATABASE_URL` 設定からエンジンを生成するため。

## External Dependencies

### fastapi
- **Version**: 未固定（最新）
- **Purpose**: REST API フレームワーク。
- **License**: MIT。

### uvicorn[standard]
- **Version**: 未固定
- **Purpose**: ASGI サーバ。
- **License**: BSD。

### sqlalchemy
- **Version**: >=2.0
- **Purpose**: ORM。
- **License**: MIT。

### pydantic
- **Version**: >=2.0
- **Purpose**: バリデーション/シリアライズ。
- **License**: MIT。

### pytest / httpx
- **Version**: 未固定
- **Purpose**: テスト。
- **License**: MIT / BSD。
