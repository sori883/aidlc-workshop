# アプリケーション設計 統合ドキュメント (Application Design — Consolidated)

社内会議室予約システムの高レベル設計を統合したドキュメント。詳細は各個別ファイルを参照。

## 1. 設計方針（確定事項）
| 項目 | 決定 | 根拠 |
|---|---|---|
| レイヤ構成 | router → service → repository → DB | Q-D1=A |
| DBアクセス | SQLAlchemy (ORM) | Q-D2=A |
| ID型 | UUID 文字列 | Q-D3=B |
| プロセス構成 | 単一 FastAPI アプリ、ローカル完結 | 要件 NFR-01 |

## 2. コンポーネント構成（→ components.md）
- **Room**: 会議室マスタ CRUD
- **Reservation**: 予約の作成・一覧・取得・キャンセル
- **Availability**: 重複判定（半開区間）と空き会議室検索
- **Persistence**: SQLAlchemy セッション・ORMモデル基盤

## 3. メソッド（→ component-methods.md）
- RoomService: create/get/list/update/delete
- ReservationService: create（重複チェック込み）/get/list/cancel
- AvailabilityService: overlaps / has_conflict / find_available_rooms

## 4. サービス層（→ services.md）
- ReservationService が中核。作成時に RoomRepository（存在確認）と AvailabilityService（重複チェック）をオーケストレーション。
- 予約作成は「重複チェック→挿入」を1トランザクションで実施。

## 5. 依存関係（→ component-dependency.md）
- Service → Repository → DB の一方向。循環依存なし。
- すべて同一プロセス内呼び出し。外部通信なし。

## 6. ストーリーとの対応
| ストーリー | 担当コンポーネント/メソッド |
|---|---|
| US-01 会議室登録 | RoomService.create_room |
| US-02 会議室一覧・詳細 | RoomService.list_rooms / get_room |
| US-03 会議室更新・削除 | RoomService.update_room / delete_room |
| US-04 予約作成 | ReservationService.create_reservation |
| US-05 重複拒否 | AvailabilityService.has_conflict / overlaps |
| US-06 予約一覧・詳細 | ReservationService.list_reservations / get_reservation |
| US-07 予約キャンセル | ReservationService.cancel_reservation |
| US-08 空き検索 | AvailabilityService.find_available_rooms |

## 7. 後続工程に委ねる論点（Open Points）
- 会議室削除時の紐づく予約の扱い（削除連鎖 or 拒否）→ Functional Design
- キャンセルの冪等性（再キャンセルの扱い）→ Functional Design
- 重複防止の DB レベル制約の要否 → NFR Design / Functional Design

## 8. 設計の完全性・一貫性チェック
- [x] 全8ストーリーがコンポーネント/メソッドに対応付け済み
- [x] レイヤ責務が明確（router/service/repository/persistence）
- [x] 循環依存なし
- [x] 中核ロジック（重複防止）の担当が明確（AvailabilityService）
