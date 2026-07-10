# Requirements: 定期予約機能

## Intent Analysis

- **User Request**: 既存の会議室予約システムに「定期予約（毎週同じ曜日・時間に繰り返す予約）」機能を追加する。詳細は `docs/writing-inputs/brownfield-vision.md`。
- **Request Type**: New Feature（既存システムへの機能追加 / Enhancement）
- **Scope Estimate**: Multiple Components（reservations モジュール中心 + db.models + 新モジュール/テーブル。availability の重複判定ロジックを再利用）
- **Complexity Estimate**: Moderate（日付生成・シリーズ管理・原子的な重複チェックが絡むが、既存の半開区間ロジックを流用できる）

## Existing System Context（リバースエンジニアリングより）

- Python 3.13 + FastAPI + SQLAlchemy 2.0 + SQLite のレイヤード構成（Router → Service → Repository → ORM）。
- 重複防止は半開区間 `[start, end)` の `overlaps` 純粋関数 + `AvailabilityService.has_conflict`。
- ドメイン例外→HTTP（400/404/409）を common で一元マッピング。
- 予約は `status`（active / cancelled）を持ち、キャンセルは冪等。
- **制約**: 既存テストは `from brown.tests.conftest import ...` 規約でインポートしており、新規テストも同規約に合わせる。

## Constraints（変更禁止 — Vision より）

- **C-1**: 既存の単発予約 API（`POST /reservations` 等）のリクエスト/レスポンス契約を変更しない。
- **C-2**: ダブルブッキング防止の半開区間ロジック（隣接OK・重なりNG）を変更しない。再利用する。
- **C-3**: README 記載の HTTP ステータス方針を踏襲する（作成201 / 取得200 / 削除204 / 検証違反400 / Pydantic制約422 / 未存在404 / 重複409）。
- **C-4**: 既存テストはすべてパスし続ける。既存テストの改変は不可。

## Functional Requirements

### FR-1: 定期予約シリーズの作成
- **FR-1.1**: 新規エンドポイント `POST /reservations/recurring` を追加する（既存の単発 API は無変更 — C-1）。
- **FR-1.2**: リクエストは、会議室・起点となる開始/終了時刻（曜日と時間帯を規定）・予約者情報・繰り返し終了条件（`count` または `until`）を受け取る。
- **FR-1.3**: 起点の曜日・時間帯を毎週繰り返して各回を生成する。各回は起点から 7 日刻みで、同じ時刻・同じ会議室。
- **FR-1.4 (終了条件)**: `count`（回数）または `until`（終了日）の**どちらか一方**を指定する。両方指定・両方未指定はいずれも 400。
  - `count`: 起点を1回目として合計 count 回を生成。
  - `until`: 起点から、開始日が `until` 以下となる回まで生成。
- **FR-1.5 (回数上限)**: 1シリーズの最大回数は **52回**。生成回数が上限を超える場合は 400。
- **FR-1.6 (重複時の扱い — 全体拒否 / 原子性)**: 生成した回のうち **1回でも**既存 active 予約（他シリーズ含む）と重複する場合、**シリーズ全体を作成せず 409** を返す。DB へは1件も登録しない（原子的）。
- **FR-1.7**: 重複判定は既存の半開区間ロジック（`overlaps` / `has_conflict`）を再利用する（C-2）。シリーズ内の各回どうしは 7 日刻みのため相互に重複しない前提。
- **FR-1.8 (過去日時)**: シリーズ最初の回の開始時刻が現在より過去の場合は 400（既存の単発予約ルールと一貫 — C-3）。
- **FR-1.9 (入力検証)**: 各回について既存と同じ検証を適用（start < end、予約者名必須、会議室存在確認）。違反時は 400 / 404。
- **FR-1.10 (成功レスポンス)**: 201 で、作成された `series_id` と生成された全回の予約（`ReservationOut` のリスト）を返す。

### FR-2: シリーズ全体のキャンセル
- **FR-2.1**: 新規エンドポイント `POST /reservations/recurring/{series_id}/cancel` を追加する。
- **FR-2.2 (対象範囲)**: **未来の active な回のみ**をキャンセルする。既に開始時刻を過ぎた回、既に cancelled の回は変更しない。
- **FR-2.3 (冪等性)**: 既存キャンセルの方針に倣い冪等。再実行しても未来 active 回がなければ状態を変えず 200 を返す。
- **FR-2.4**: 存在しない `series_id` は 404。
- **FR-2.5 (レスポンス)**: 200 で、キャンセル後のシリーズ情報および各回の状態を返す。

### FR-3: 個別回のキャンセル
- **FR-3.1**: シリーズ内の1回だけのキャンセルは、**既存の `POST /reservations/{reservation_id}/cancel` を流用**する（新規 API を作らない）。
- **FR-3.2**: 各回は通常の予約行（`series_id` を持つ）であり、既存キャンセル API がそのまま機能する。冪等性・404 挙動も既存仕様を踏襲（C-1 に抵触しない）。

### FR-4: シリーズ情報の表示
- **FR-4.1**: `ReservationOut` に `series_id`（`str | None`、単発予約は `null`）を**追加**する。
  - 既存テストはレスポンスの完全一致ではなく個別フィールドを検証しているため、フィールド追加は既存テストを壊さない（C-4 を満たす）。既存リクエスト契約は不変（C-1 を満たす）。
- **FR-4.2**: 予約一覧・詳細（`GET /reservations`, `GET /reservations/{id}`）のレスポンスに `series_id` が含まれ、シリーズ所属が判別可能。
- **FR-4.3 (任意)**: シリーズ単位の照会が必要な場合、`GET /reservations/recurring/{series_id}` でシリーズのメタ情報と全回を返す（設計段階で要否を確定）。

### FR-5: データモデル
- **FR-5.1**: 新テーブル `reservation_series` を追加する。少なくとも `id`、繰り返しルール（曜日・時間帯・終了条件のメタ）、予約者情報、作成日時を保持。
- **FR-5.2**: `reservations` テーブルに `series_id`（`String(36)`、NULL可、`reservation_series.id` への FK）列を追加する。単発予約は `series_id = NULL`。
- **FR-5.3**: マイグレーションは既存の `create_all()` によるテーブル作成方針に整合させる（設計段階で既存DBへの列追加手順を確定）。

## Non-Functional Requirements

- **NFR-1 (互換性)**: 既存の単発予約フロー・API 契約・既存テストに一切の後方非互換を持ち込まない（C-1〜C-4）。
- **NFR-2 (一貫性/原子性)**: シリーズ作成は原子的（全成功または全ロールバック）。重複チェックと全回 INSERT を単一トランザクション内で実施。
- **NFR-3 (テスト容易性)**: 日付生成・終了条件解決を純粋関数として切り出し、単体テスト可能にする。既存の `overlaps` の設計思想を踏襲。
- **NFR-4 (HTTP ステータス整合)**: 新規 API も C-3 のステータス方針に従う（201/200/400/404/409/422）。
- **NFR-5 (スコープ外)**: 隔週・月次などの複雑な繰り返し、認証・権限、キャンセルポリシー、営業時間制約、タイムゾーン対応は対象外（Vision）。

## Extension Configuration（オプトイン結果）

| Extension | Enabled | 備考 |
|---|---|---|
| Security Baseline | No | 適用しない |
| Resiliency Baseline | No | 適用しない |
| Property-Based Testing | Yes (Partial) | PBT-02/03/07/08/09 のみ強制。日付生成・重複判定・シリアライズ往復に適用。フレームワークは Hypothesis を想定（NFR/コード生成で確定）。 |

## Key Requirements Summary

- `POST /reservations/recurring` を新設。週次繰り返しを `count` または `until`（最大52回）で生成。
- **重複が1回でもあればシリーズ全体を 409 で拒否**（原子的、既存の半開区間ロジックを再利用）。
- シリーズ全体キャンセル（未来 active 回のみ）を `POST /reservations/recurring/{series_id}/cancel` で提供。個別回は既存キャンセル API を流用。
- `ReservationOut` に `series_id`（単発 null）を追加。既存 API 契約・既存テストは不変。
- 新テーブル `reservation_series` + `reservations.series_id` 列で永続化。
- 拡張: Security/Resiliency は無効、PBT は Partial。
