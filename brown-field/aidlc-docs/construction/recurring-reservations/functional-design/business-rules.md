# Business Rules — recurring-reservations

命名は既存 business-rules（BR-C*/BR-X*/BR-OV/BR-A/BR-R*）に倣い、シリーズ系を **BR-RS*** とする。
既存ルールは再利用し、変更しない。

## 作成: 入力検証（BR-RS-C*）

- **BR-RS-C1（時刻順序）**: 起点 `start_time >= end_time` は 400。（既存 BR-C1 と同一方針）
- **BR-RS-C2（予約者名必須）**: `booker_name` が空/空白のみは 400。（既存 BR-C2 と同一）
- **BR-RS-C3（会議室存在）**: `room_id` が存在しなければ 404。（既存 BR-C3 と同一）
- **BR-RS-C4（終了条件の一方指定）**: `count` と `until` の両方指定は 400。両方未指定も 400。ちょうど一方のみ有効。
- **BR-RS-C5（count 妥当性）**: `count` 指定時、`count >= 1` を要求。1未満は 422（Pydantic 制約）または 400。
- **BR-RS-C6（until 妥当性・inclusive）**: `until` は日付として扱い、各回の**開始日が until 以下**（inclusive）の回まで生成。起点の開始日が until より後なら生成数0 → 400（有効な回がない）。
- **BR-RS-C7（回数上限）**: 生成回数が **52 を超える**場合は 400。
- **BR-RS-C8（過去日時）**: シリーズ**最初の回**の `start_time` が現在（`datetime.now()`）より過去なら 400。（既存 BR-C4 と一貫。start == now は許可）

## 作成: 週次生成（BR-RS-G*）

- **BR-RS-G1（7日刻み）**: n 回目の開始 = 起点開始 + 7*(n-1) 日、終了 = 起点終了 + 7*(n-1) 日。時・分・秒は起点と同一。
- **BR-RS-G2（曜日固定）**: 全回は起点と同じ曜日（7日刻みの自然な帰結）。
- **BR-RS-G3（回数確定）**: count 指定なら回数 = count。until 指定なら開始日 <= until を満たす最大回数。

## 作成: 重複と原子性（BR-RS-OV*）

- **BR-RS-OV1（重複判定の再利用）**: 各回の重複判定は既存 `AvailabilityService.has_conflict`（半開区間 `[start, end)`、隣接OK・重なりNG）をそのまま使用。（既存 BR-OV を変更しない = C-2）
- **BR-RS-OV2（全体拒否/原子性）**: 生成した回のうち**1回でも** active 予約（他シリーズ・単発含む）と重複したら **409** を返し、series と全回を**一切登録しない**（単一トランザクションでロールバック）。
- **BR-RS-OV3（シリーズ内非重複前提）**: 同一シリーズの各回は7日刻みで相互に重ならないため、シリーズ内どうしの重複判定は不要。
- **BR-RS-OV4（判定タイミング）**: 重複チェック → 全回 INSERT を単一トランザクション内で実施（既存 BR-C5 と同方針）。

## 作成: レスポンス（BR-RS-R*）

- **BR-RS-R1**: 成功時 201。`series_id` と生成された全回（`ReservationOut` のリスト、各 `series_id` 設定済み）を返す。
- **BR-RS-R2**: 各回の `status` は active、`series_id` は当該シリーズ。

## シリーズ全体キャンセル（BR-RS-X*）

- **BR-RS-X1（対象）**: `start_time > 現在` の active 回のみ cancelled にする。
- **BR-RS-X2（過去回不変）**: `start_time <= 現在` の回、および既に cancelled の回は変更しない。
- **BR-RS-X3（冪等）**: 対象の未来 active 回が無ければ状態を変えず 200。再実行も 200。
- **BR-RS-X4（未存在）**: `series_id` が存在しなければ 404。
- **BR-RS-X5（レスポンス）**: 200。シリーズのメタ情報と各回の現在状態を返す。

## 個別回キャンセル（BR-RS-I*）

- **BR-RS-I1（既存流用）**: シリーズの各回は通常の Reservation。既存 `POST /reservations/{id}/cancel`（既存 BR-X* 準拠、冪等・404）をそのまま使用。**新規ルール・新規コードなし**。

## 表示（BR-RS-D*）

- **BR-RS-D1（series_id 付与）**: `ReservationOut` に `series_id` を含める。単発予約は `null`。
- **BR-RS-D2（後方互換）**: `ReservationCreate`（リクエスト）は不変。既存の単発予約 API の契約・挙動は変わらない（C-1）。

## シリーズ照会（BR-RS-Q*）

- **BR-RS-Q1**: `GET /reservations/recurring/{series_id}` はメタ情報 + 全回を 200 で返す。
- **BR-RS-Q2**: 未存在は 404。

## HTTP ステータス整合（C-3）

| 事象 | ステータス |
|---|---|
| シリーズ作成成功 | 201 |
| シリーズキャンセル成功 / 照会成功 | 200 |
| 入力検証違反（時刻順序・終了条件・回数上限・過去日時・until 範囲） | 400 |
| Pydantic 制約違反（count 型など） | 422 |
| 会議室 / シリーズが存在しない | 404 |
| いずれかの回が重複 | 409 |
