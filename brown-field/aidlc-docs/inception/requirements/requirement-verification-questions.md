# Requirements Verification Questions — 定期予約機能

定期予約（毎週同じ曜日・時間に繰り返す予約）機能の要件を確定するための質問です。
各質問の `[Answer]:` タグの後に選択肢の記号（A/B/C…）を記入してください。
選択肢が合わない場合は最後の「Other」を選び、説明を記入してください。
記入が終わったら「完了」とお知らせください。

> **回答済み（2026-07-10、対話形式で取得）**
> - Q1: 全体拒否（1回でも重複ならシリーズ全体を 409）
> - Q2: 新テーブル `reservation_series` + `reservations.series_id`（NULL可）列追加
> - Q3: 両方サポート（count または until のどちらか一方。両方指定はエラー）
> - Q4: 上限あり（最大52回、超過は 400）
> - Q5: 新規エンドポイント `POST /reservations/recurring`
> - Q6: シリーズ全体キャンセルは「未来の active 回のみ」
> - Q7: 個別回キャンセルは既存 `POST /reservations/{id}/cancel` を流用
> - Q8: シリーズ全体キャンセルは `POST /reservations/recurring/{series_id}/cancel`（Q5 に整合）
> - Q9: `ReservationOut` に `series_id`（単発は null）を追加
> - Q10: 過去日時は既存ルールに合わせる（最初の回の開始が過去なら 400）
> - Q11 Security 拡張: No（適用しない）
> - Q12 Resiliency 拡張: No（適用しない）
> - Q13 Property-Based Testing: Partial（純粋関数とシリアライズ往復に限定適用）

> 参考: 変更禁止事項（Vision より）
> - 既存の単発予約 API のリクエスト/レスポンス契約
> - ダブルブッキング防止の半開区間ロジック（隣接OK・重なりNG）
> - README 記載の HTTP ステータス方針
> - 既存テストはすべてパスし続けること・既存テストの改変は不可

---

## Question 1: シリーズの一部が重複する場合の扱い（Vision 未確定事項）
定期予約シリーズを作成する際、シリーズ内の一部の回だけが既存予約と重複する場合、どう振る舞うべきですか。

A) 全体拒否 — 1回でも重複があればシリーズ全体を作成せず 409 を返す（原子性を優先）

B) スキップ作成 — 重複する回だけスキップし、残りの回は作成する。レスポンスで作成された回とスキップされた回を返す

C) 呼び出し側が選べる — リクエストのパラメータ（例: `on_conflict = reject | skip`）で A/B を切り替え可能にする

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 2: シリーズのデータ設計（Vision 未確定事項）
定期予約シリーズをどう永続化しますか。

A) 新テーブル `reservation_series` を追加し、各回は既存 `reservations` に `series_id`（NULL可・FK）列を追加して紐付ける（単発予約は series_id=NULL のまま）

B) `reservations` テーブルへの列追加のみで表現（series_id 等を追加、シリーズのメタ情報も予約行に持たせる。新テーブルなし）

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 3: 繰り返しの終了指定方式（In Scope: 終了日 or 回数指定）
週次の繰り返しをどこまで作成するかの指定方法として、どれをサポートしますか。

A) 回数指定のみ（例: `count = 10` で10回分作成）

B) 終了日指定のみ（例: `until = 2026-09-30` までの毎週分を作成）

C) 両方サポート（`count` または `until` のどちらか一方を指定。両方指定はエラー）

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 4: 繰り返し回数の上限
無限・過大なシリーズ作成を防ぐため、1シリーズあたりの最大回数に上限を設けますか。

A) 上限を設ける（推奨。例: 最大52回=約1年。超過時は 400）

B) 上限なし（終了日/回数の指定に委ねる）

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 5: 定期予約作成の API 形
既存の単発予約 API（`POST /reservations`）の契約は変更禁止です。定期予約はどの形で公開しますか。

A) 新規エンドポイント `POST /reservations/recurring` を追加（単発 API は無変更）

B) 新規エンドポイント `POST /reservation-series` を追加（シリーズをリソースとして表現）

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 6: シリーズ全体のキャンセルの範囲（In Scope: シリーズ全体キャンセル）
「シリーズ全体のキャンセル」を実行したとき、どの回をキャンセル対象にしますか。

A) 未来の active な回のみキャンセル（既に過ぎた回・既にキャンセル済みの回は変更しない）

B) 過去・未来を問わずシリーズの全 active 回をキャンセル

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 7: 個別回のキャンセル方法（In Scope: 個別回キャンセル）
シリーズ内の1回だけをキャンセルする操作は、どのように提供しますか。

A) 既存の `POST /reservations/{reservation_id}/cancel` をそのまま使う（各回は通常の予約行なので既存 API で個別キャンセル可能。冪等性も既存仕様を踏襲）

B) シリーズ専用の個別キャンセル API を新設する

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 8: シリーズ全体キャンセルの API 形
シリーズ全体キャンセルのエンドポイント形をどうしますか（Q5 の選択に整合させます）。

A) `POST /reservations/recurring/{series_id}/cancel`（または `/reservation-series/{series_id}/cancel`）

B) 既存キャンセル API にシリーズ指定の拡張を加える

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 9: 予約一覧・詳細でのシリーズ情報表示（In Scope）
既存の単発予約 API のレスポンス契約は変更禁止です。シリーズ情報（series_id 等）を予約の出力にどう含めますか。

A) 既存 `ReservationOut` に `series_id`（単発は null）を追加する。※既存テストがフィールド追加で壊れないことを前提（既存テストは等値比較ではなく個別フィールド検証のため追加は許容）

B) 既存 `ReservationOut` は一切変更せず、シリーズ情報は専用エンドポイント（例: `GET /reservations/recurring/{series_id}`）でのみ返す

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 10: 定期予約の開始日の扱い
定期予約の起点日時に過去が含まれる場合の扱いは、既存の単発予約ルール（過去開始は 400）に合わせますか。

A) 既存ルールに合わせる — シリーズの最初の回の開始が過去なら 400（単発と一貫）

B) 起点は現在以降を必須とし、以降は指定曜日・時間で週次生成（Aと実質同じだが明示）

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 11 (拡張): Security Extensions
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)

B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 12 (拡張): Resiliency Extensions
Should the resiliency baseline be applied to this project?

（有効化すると AWS Well-Architected（信頼性の柱）由来の設計時ベストプラクティスを要件・設計・コードに反映します。本番認証やRTO/RPO保証ではなく、あくまで出発点です。）

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects)

X) Other (please describe after [Answer]: tag below)

[Answer]:

---

## Question 13 (拡張): Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

（定期予約は日付生成・重複判定というロジック中心の機能のため、PBT と相性が良い領域です。）

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips

C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers)

X) Other (please describe after [Answer]: tag below)

[Answer]:

---
