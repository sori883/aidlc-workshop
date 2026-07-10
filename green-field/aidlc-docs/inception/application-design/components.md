# コンポーネント定義 (Components)

## 設計方針（確定事項）
- **レイヤ構成**: API層 (router) → サービス層 (service) → リポジトリ層 (repository) → DB（SQLite）— Q-D1=A
- **DBアクセス**: SQLAlchemy (ORM) — Q-D2=A
- **ID型**: UUID 文字列（`str`, UUID4 を文字列で保持）— Q-D3=B

---

## C1. Room コンポーネント
- **目的**: 会議室マスタの管理（CRUD）。
- **責務**:
  - 会議室の作成・取得・一覧・更新・削除。
  - 会議室属性（名前・収容人数・設備・場所）のバリデーション。
- **インターフェース**: RoomService（サービス層）が公開。RoomRepository がデータアクセスを担う。
- **保持データ**: Room（id, name, capacity, equipment, location, created_at）。

## C2. Reservation コンポーネント
- **目的**: 予約のライフサイクル管理。
- **責務**:
  - 予約の作成・取得・一覧・キャンセル。
  - 予約属性（会議室・開始/終了時刻・予約者・状態）のバリデーション。
  - キャンセル時の状態遷移（active → cancelled）。
- **インターフェース**: ReservationService が公開。ReservationRepository がデータアクセスを担う。
- **保持データ**: Reservation（id, room_id, start_time, end_time, booker_name, booker_email, status, created_at）。

## C3. Availability コンポーネント
- **目的**: 重複判定と空き会議室検索という横断ロジックを提供。
- **責務**:
  - 2つの時間帯の重なり判定（半開区間ルール）。
  - 指定会議室・時間帯に対する既存 active 予約との重複チェック（予約作成時に使用）。
  - 指定時間帯に空いている会議室一覧の算出（US-08）。
- **インターフェース**: AvailabilityService として提供。Reservation/Room のリポジトリを参照する純粋ロジック中心のコンポーネント。
- **保持データ**: なし（ステートレス。判定ロジックのみ）。

## C4. Persistence（共通基盤）
- **目的**: DB接続・セッション・スキーマ定義の共通基盤。
- **責務**:
  - SQLAlchemy エンジン/セッションの提供。
  - ORM モデル（Room, Reservation）の定義とテーブル作成。
- **インターフェース**: DBセッション依存性（FastAPI の Depends で注入）。

## コンポーネント一覧表
| ID | コンポーネント | レイヤ | 主な公開単位 |
|---|---|---|---|
| C1 | Room | domain/service/repository | RoomService |
| C2 | Reservation | domain/service/repository | ReservationService |
| C3 | Availability | service（横断ロジック） | AvailabilityService |
| C4 | Persistence | infrastructure | DBセッション・ORMモデル |
