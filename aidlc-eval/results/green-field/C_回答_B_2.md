必要な情報が揃いました。なお、私の作業ディレクトリは `green-field/cond-B` ですが、質問が言及する定期予約機能（`app/series/recurrence.py`、`from brown.tests.conftest`、hypothesis、52回上限、`series_id` 列追加など）は **`brown-field/cond-B`** の実装に対応します。以下はすべて `brown-field/cond-B/` 配下のファイルを根拠にした回答です。

---

**Q1.** 「全体拒否（1回でも重複ならシリーズ全体を409）」は、要件確定時にユーザーが選択した仕様です。要件検証で「A) 全体拒否」「B) 重複回だけスキップして残りを作成」「C) パラメータで切替」の3案が明示的に提示され、2026-07-10 の対話でユーザーが A を選択しました。理由は原子性（all-or-nothing）を優先する明快さで、単一トランザクション＋既存 `has_conflict` の再利用で実装が単純になるためです。B案（スキップ）は候補として提示されたが採用されませんでした。根拠: `aidlc-docs/inception/requirements/requirement-verification-questions.md`(Question 1 と回答済み欄), `aidlc-docs/inception/requirements/requirements.md`(FR-1.6), `app/series/service.py:78-81`。

**Q2.** 52回 ≈ 約1年（52週）だからです。無限・過大なシリーズ生成を防ぐ上限として、要件検証 Q4 で「A) 上限あり（例: 最大52回=約1年、超過は400）」が選ばれました。根拠: `aidlc-docs/inception/requirements/requirement-verification-questions.md`(Question 4「最大52回=約1年」), `requirements.md`(FR-1.5), `app/series/service.py:22`(`MAX_OCCURRENCES = 52`), `app/series/recurrence.py:18`。

**Q3.** シリーズの各回は通常の `Reservation` 行（`series_id` を持つだけ）であり、既存の `POST /reservations/{reservation_id}/cancel` がそのまま個別回のキャンセルに使えるため、専用APIを新設しない設計にしました（要件検証 Q7 で A を選択、「新規ルール・新規コードなし」）。個別回のキャンセルは、対象回の予約ID を使って既存の単発キャンセルAPI `POST /reservations/{reservation_id}/cancel` を呼びます。根拠: `aidlc-docs/inception/requirements/requirement-verification-questions.md`(Question 7), `requirements.md`(FR-3.1/3.2), `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md`(BR-RS-I1)。

**Q4.** テスト容易性（保守性）のためです。週次の日付生成を副作用なし・DB非依存の純粋関数に切り出すことで、単体テストと Property-Based Testing（Hypothesis）が容易になり、既存の重複判定 `overlaps` と同じ設計思想を踏襲しています。根拠: `app/series/recurrence.py:1-5`(docstring「副作用なし・DB非依存でテスト/PBTが容易。overlaps と同じ設計思想」), `requirements.md`(NFR-3), `aidlc-docs/construction/recurring-reservations/nfr-requirements/nfr-requirements.md`(NFR-RS-4)。

**Q5.** 既存プロジェクトが Alembic 等のマイグレーションツールを一切導入しておらず、起動時の `Base.metadata.create_all()` でスキーマを作る方式だったためです。その方針に整合させ、依存追加を最小化する目的で、既存の `create_all()` を拡張した冪等な自動ALTERヘルパ（`_ensure_series_id_column`：列が無ければ `ALTER TABLE reservations ADD COLUMN series_id` を実行）を採用しました。SQLite ローカル実行の小規模ワークショップアプリという前提もあります。根拠: `aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md`(「決定: 軽量な自動ALTERヘルパ（冪等）」), `aidlc-docs/construction/recurring-reservations/nfr-requirements/tech-stack-decisions.md`(マイグレーション方針), `app/db/database.py:36-62`。

**Q6.** 目的は Property-Based Testing（PBT）フレームワークとしての導入で、日付生成・重複判定・シリアライズ往復に適用します。一部のテストにしか適用されていないのは、ユーザーが拡張オプトインで「Partial」を選んだためです（Q13 回答 B）。Partial では PBT-02（Round-trip）/PBT-03（Invariant）/PBT-07（Generator）/PBT-08（Shrinking）/PBT-09（Framework）のみ強制で、対象は純粋関数（`generate_occurrences`）とスキーマの往復に限定され、DB依存やステートフルなAPI層には適用しない方針だからです。根拠: `requirements.md`(Extension Configuration「Partial」), `requirement-verification-questions.md`(Question 13 の B), `aidlc-docs/.../nfr-requirements/nfr-requirements.md`(NFR-RS-6), `tests/test_recurring_pbt.py:1-6`, `requirements.txt`(hypothesis)。

**Q7.** はい、共存できます。重複判定は半開区間 `[start, end)` で行い、`overlaps` は `start_a < end_b and start_b < end_a` です。A（10:00終了）と B（10:00開始）では `start_b(10:00) < end_a(10:00)` が偽になるため重ならない扱い（隣接OK）となり、両方 active で登録できます。根拠: `app/availability/service.py:14-19`, `requirements.md`(C-2「隣接OK・重なりNG」)。

**Q8.** はい、含まれます。`until` は inclusive で、各回の「開始日 <= until」まで生成します（`occ_start.date() > until` になった時点で打ち切り）。開始日がちょうど 2030-01-15 の回は `> until` ではないため生成対象に含まれます。根拠: `app/series/recurrence.py:42-53`, `business-rules.md`(BR-RS-C6「開始日が until 以下（inclusive）」)。

**Q9.** `count` と `until` を両方指定すると 400（ValidationError「count または until のどちらか一方を指定してください」）。両方省略しても同じく 400 です。「ちょうど一方のみ」を要求しており、`(count is None) == (until is None)` が真（＝両方指定 or 両方未指定）で拒否されます。根拠: `app/series/service.py:49-53`, `app/series/recurrence.py:28-29`, `business-rules.md`(BR-RS-C4)。

**Q10.** 仕様上は許可です。過去判定は「最初の回の開始 < `datetime.now()`」で、`start == now` は `<` に該当しないため拒否されません（BR-RS-C8「start == now は許可」）。ただし実装は生成後に改めて `datetime.now()` を取得して比較するため（`app/series/service.py:72`）、リクエスト時点で「ちょうど現在時刻」だと処理時間ぶん now が進み `start < now` となって 400 になる可能性があります。設計意図としては「現在以降（>= now）は可、厳密な過去のみ 400」です。根拠: `app/series/service.py:71-73`, `business-rules.md`(BR-RS-C8), `requirement-verification-questions.md`(Question 10)。

**Q11.** (a) 過去に開始済みの回（`start_time <= 現在`）は変更されません（`list_future_active_by_series` が `start_time > now` のみ抽出）。(b) 既にキャンセル済みの回も変更されません（`status == active` のみ抽出）。(c) もう一度実行しても冪等で、対象となる未来の active 回が無ければ状態を変えず 200 を返します。根拠: `app/series/service.py:130-141`, `app/reservations/repository.py:60-72`, `business-rules.md`(BR-RS-X1/X2/X3)。

**Q12.** リクエスト契約に変更はありません（`ReservationCreate` は不変）。レスポンスは `ReservationOut` に `series_id`（`str | None`、既定 `None`、単発予約は `null`）が追加されました。これは Optional フィールドの追記のみで後方互換（既存テストは個別フィールド検証のため壊れない）ですが、レスポンスの形は厳密には拡張されています。根拠: `app/reservations/schemas.py:9-14`(リクエスト不変)と`:17-29`(series_id追加), `requirements.md`(FR-4.1, C-1), `business-rules.md`(BR-RS-D1/D2)。

**Q13.** いいえ、DBレベルの制約（ユニーク制約や排他制約）では実現されていません。`reservations` にあるのは非ユニークの複合インデックス `ix_reservations_room_id_status` のみで、ダブルブッキング防止はアプリ層で「`has_conflict` で問い合わせ→重複なければ INSERT」というロジックで行っています。ロックやトランザクション分離での防御がないため、並行リクエストが同時に来ると両方が重複チェックを通過して二重予約が起こりえます（並行性制御はスコープ外）。根拠: `app/db/models.py:111-112`(インデックスのみ、ユニーク制約なし), `app/availability/service.py:28-46`, `app/series/service.py:78-120`, `nfr-requirements.md`(非対象：スケーラビリティ等)。

**Q14.** リポジトリルート（プロジェクト直下）に置かれた `conftest.py` が、`brown` という名前の擬似モジュールを作り `__path__` を当該プロジェクトディレクトリに向けて `sys.modules["brown"]` に登録するため、`from brown.tests.conftest import create_room` が `tests/conftest.py` に解決されます。あわせてプロジェクトルートを `sys.path` に追加して `app` を import 可能にしています。この規約に合わせた理由は、既存テスト（`test_availability_api.py`・`test_rooms_api.py`・`test_reservations_api.py`）が元々この `brown.tests.conftest` 形式を使っており、既存テストを一切改変しない（C-4）という制約のもと、新規テストも同じ規約に揃えたためです。根拠: `conftest.py:1-24`(ルート), `tests/conftest.py:55-67`(`create_room`), `requirements.md`(既存システムContext・C-4)。

**Q15.** 起動時に `create_all()` が走り、(1) `_ensure_series_id_column` が既存 `reservations` テーブルに `series_id` 列が無いことを検出して `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を実行、(2) `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します。既存の予約データは保持され、`series_id` は NULL になります。2回目の起動では、`series_id` 列は既に存在するので列追加はスキップ、`reservation_series` も既存なので `create_all` はスキップします（冪等）。根拠: `app/db/database.py:36-62`, `infrastructure-design.md`(「冪等」「複数回起動しても安全」), `app/main.py:42`。

**Q16.** プロジェクトディレクトリ（`brown-field/cond-B`＝ルート `conftest.py` がある場所）で、`python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` で依存を入れ、`pytest` を実行します。ルート `conftest.py` が `brown` エイリアスと `app` の import パスを解決するため、この場所から実行する必要があります。全部で **66件** パスします（既存回帰34 + 新規例示27〔recurrence 9 + recurring_api 18〕+ PBT 5）。根拠: `aidlc-docs/construction/build-and-test/build-instructions.md`, `unit-test-instructions.md`, `build-and-test-summary.md`(66/66), 実ファイルのテスト関数数 5+7+9+18+5+13+9=66。（注: build-instructions は旧レイアウト時の記述で「`brown-field/` から実行」とありますが、現行では `brown` を登録する `conftest.py` はプロジェクト直下（cond-B）にあります。）

**Q17.** Pydantic 層では `count` は `ge=1` のみで上限チェックがない（`count=100` は通過）ため、まず `generate_occurrences` が最大 `max_count + 1`（＝53件）まで生成して打ち切り、次に `RecurringReservationService.create_series` が `len(occurrences) > MAX_OCCURRENCES(52)` を判定して `ValidationError`（→400）を返します。つまりサービス層で件数超過を検出します。根拠: `app/series/schemas.py:18-20`, `app/series/recurrence.py:36-40`, `app/series/service.py:66-70`。

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。日時はナイーブ `datetime`（ローカル）として保存・比較され、タイムゾーン対応は明示的にスコープ外です。根拠: `app/db/models.py:1-8`(「時刻はナイーブ datetime（ローカル）」), `requirements.md`(NFR-5「タイムゾーン対応は対象外」), `nfr-requirements.md`(非対象：タイムゾーン)。

**Q19.** できません。実装は週次（7日刻み）固定で、隔週・月次を指定するパラメータは存在しません。`RecurringReservationCreate` が受け取るのは `room_id`・`start_time`・`end_time`・`booker_name`・`booker_email`・`count`／`until` のみで、間隔（interval/frequency）指定はなく、隔週・月次は明示的にスコープ外です。根拠: `app/series/schemas.py:11-23`, `app/series/recurrence.py:10`(`WEEK = timedelta(days=7)`固定), `requirements.md`(NFR-5「隔週・月次などの複雑な繰り返し…は対象外」)。

**Q20.** 分かりません（該当設定は存在しません）。このアプリには認証・認可の実装が一切なく（Security 拡張は「No」でオプトアウト、`app/` 配下に token/auth/jwt 等のコードなし）、認証トークンもその有効期限設定も存在しないためです。根拠: `requirements.md`(NFR-5「認証・権限…は対象外」/Extension Configuration「Security Baseline: No」), `app/core/config.py`(DB/host/port のみ、認証設定なし), `app/` 全体に認証関連コードが見当たらないこと。
