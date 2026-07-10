# Component Inventory

## Application Packages
- `app` - FastAPI アプリのルート。
- `app.rooms` - 会議室 CRUD（router/service/schemas/repository）。
- `app.reservations` - 予約管理（router/service/schemas/repository）。
- `app.availability` - 空き検索・重複判定（router/service/schemas）。
- `app.db` - ORM モデルと DB セッション（models/database）。
- `app.common` - ドメイン例外と HTTP マッピング（exceptions/errors）。
- `app.core` - アプリ設定（config）。

## Infrastructure Packages
- なし（IaC・デプロイ設定なし）。

## Shared Packages
- `app.common` - 横断的関心事（例外・エラーハンドリング）。
- `app.core` - 設定。

## Test Packages
- `tests` - Unit + API テスト（pytest + FastAPI TestClient）。

## Total Count
- **Total Packages**: 7（app 直下のサブパッケージ + tests）
- **Application**: 6（rooms, reservations, availability, db, common, core）
- **Infrastructure**: 0
- **Shared**: common, core（Application に内包してカウント）
- **Test**: 1（tests）
