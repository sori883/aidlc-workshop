必要な情報が揃いました。回答します。

---

**Q1.** 「1回でも重複するとシリーズ全体を409で拒否」する挙動は、リポジトリ上は「原子性（atomicity）を保証する仕様上の割り切り」として実装されています。`app/series/service.py:78-81` に `# BR-RS-OV1/OV2: 1回でも重複すればシリーズ全体を拒否（原子性）。` とあり、全回を単一トランザクションで登録する設計（`app/series/service.py:83` 以降、最後に `self.db.commit()`）と一体になっています。README（41行目）にも「1回でも重複すると全体 409」と明記。ただし「スキップ方式にしなかった具体的な経緯・議論」自体はリポジトリに記録がなく、そこまでは分かりません（設計方針として原子性を選んだ、という以上の根拠は見当たりません）。根拠: `app/series/service.py:78-120`, `README.md:41`

**Q2.** リポジトリ上、52という値は上限定数 `MAX_OCCURRENCES = 52`（`app/series/service.py:22`、`app/series/recurrence.py:19` の `max_count: int = 52`）として定義され、業務ルール BR-RS-C7 に対応する旨のコメントがあります（`app/series/service.py:66-70`）。しかし「なぜ52なのか」という理由そのものはコードにもREADMEにも明記されていません。週次で52回＝およそ1年分に相当しますが、それが根拠だと断定できる記述はリポジトリ内に無く、明確な理由は分かりません。根拠: `app/series/service.py:22,66-70`, `app/series/recurrence.py:19`

**Q3.** 個別回は通常の `Reservation` レコードとして展開されており（`app/series/service.py:106-118`）、既存の単発予約キャンセルAPI `POST /reservations/{reservation_id}/cancel` をそのまま流用できるため、専用APIを設けていません。テスト `test_individual_occurrence_cancel_via_existing_api`（`tests/test_recurring_api.py:161-173`、コメント「既存の個別キャンセル API を流用（US-R05）」）が、対象回のIDに対し既存APIでキャンセルし他の回がactiveのままであることを確認しています。個別回のキャンセルはこの既存エンドポイントで行います。根拠: `tests/test_recurring_api.py:161-173`, `app/reservations/router.py:51-56`

**Q4.** 副作用が無くDB非依存で、単体テスト・Property-Based Testingが容易になるためです。`app/series/recurrence.py:1-5` のモジュールdocstringに「副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想。」と明記されており、実際に `test_recurrence.py` と `test_recurring_pbt.py` がDBなしでこの関数を直接検証しています。根拠: `app/series/recurrence.py:1-5`, `tests/test_recurring_pbt.py:32-62`

**Q5.** `Base.metadata.create_all` は未作成テーブルしか作らず既存テーブルへの列追加を行わないため、既存DBに `series_id` 列を補うヘルパ `_ensure_series_id_column`（`ALTER TABLE reservations ADD COLUMN ...` を冪等実行）を用意しています。`app/db/database.py:36-51` のdocstring/コメントにその旨が説明されています。なお「Alembic等を採用しなかった理由」自体は明記されておらず、そもそもこのプロジェクトにマイグレーションツールは導入されていません（`requirements.txt` にAlembicは無い）。軽量に列追加だけを済ませる意図と読み取れますが、不採用の明示的経緯は分かりません。根拠: `app/db/database.py:36-62`, `requirements.txt`

**Q6.** 目的は定期予約のProperty-Based Testingの実施です（`requirements.txt` に `hypothesis`、`tests/test_recurring_pbt.py` が Hypothesis を使用）。一部にしか適用されていないのは、PBT対象が純粋関数 `generate_occurrences` とスキーマ（シリアライズ往復）に限られDB非依存だからです。`tests/test_recurring_pbt.py:1-6` に「純粋関数・スキーマが対象のため DB 非依存。」と明記されています。根拠: `requirements.txt`, `tests/test_recurring_pbt.py:1-14`

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行い、`overlaps` は `start_a < end_b and start_b < end_a` を返します（`app/availability/service.py:14-19`）。10:00終了 `[9:00,10:00)` と10:00開始 `[10:00,11:00)` は `10:00 < 11:00`（真）かつ `10:00 < 10:00`（偽）で重ならない扱いになり、隣接はOKです。READMEにも「隣接はOK、重なりは 409」とあります。根拠: `app/availability/service.py:14-19`, `README.md:9`

**Q8.** 含まれます（untilはinclusive）。`app/series/recurrence.py:48` の判定は `if occ_start.date() > until: break` で、開始日が until と等しい回は打ち切られず追加されます。つまり2030-01-15に開始する回（起点からの週次でその日に一致する回が存在する場合）は生成対象に含まれます。根拠: `app/series/recurrence.py:41-53`

**Q9.** 両方指定すると400（ValidationError）になります。`app/series/service.py:49-53` の `if (count is None) == (until is None):` で両方指定/両方未指定の両ケースを弾きます。両方省略も同じ条件で400です。テスト `test_both_count_and_until_400` / `test_neither_count_nor_until_400`（`tests/test_recurring_api.py:92-105`）で確認されています。根拠: `app/series/service.py:49-53`, `tests/test_recurring_api.py:92-105`

**Q10.** 作成できます。判定は `if start_time < datetime.now()`（`app/reservations/service.py:41`）で、厳密に過去（`<`）のみ拒否し、start == now は許可されます（コメント「start == now は許可」）。定期予約側も同様に `occurrences[0][0] < datetime.now()`（`app/series/service.py:72`）です。根拠: `app/reservations/service.py:40-42`, `app/series/service.py:71-73`

**Q11.** `cancel_series` は `list_future_active_by_series`（`start_time > now` かつ status=active）だけを cancelled にします（`app/series/service.py:130-141`, `app/reservations/repository.py:60-72`）。
(a) 過去に開始済みの回（`start_time <= now`）は対象外で active のまま残ります。
(b) 既にキャンセル済みの回は status=active フィルタから外れるため対象外で、cancelled のまま変化しません。
(c) 再実行しても未来のactive回はもう無いため `future_active` が空になり、状態を変えずに200を返します（冪等）。テスト `test_cancel_series_idempotent`（`tests/test_recurring_api.py:147-154`）で確認。根拠: `app/series/service.py:130-141`, `app/reservations/repository.py:60-72`

**Q12.** レスポンス契約に追加変更があります。`ReservationOut` に `series_id: str | None = None` フィールドが追加されました（`app/reservations/schemas.py:28-29`）。単発予約ではNULLになります（テスト `test_single_reservation_has_null_series_id`、`tests/test_recurring_api.py:200-213`）。リクエスト契約 `ReservationCreate`（`app/reservations/schemas.py:9-14`）は変更されていません。よって「レスポンスにseries_idが増えた（後方互換的な追加）」が唯一の変更です。根拠: `app/reservations/schemas.py:9-29`, `tests/test_recurring_api.py:200-213`

**Q13.** データベースレベルの制約では実現されていません。重複防止はアプリ層の `has_conflict` が対象会議室のactive予約を走査して判定する方式で（`app/availability/service.py:28-46`）、DBにユニーク制約や排他ロックはありません（`app/db/models.py` にあるのはインデックス `ix_reservations_room_id_status` のみ）。したがって「重複チェック→挿入」の間にTOCTOUの隙があり、並行リクエストが同時に来た場合は二重予約が起こりえます。根拠: `app/availability/service.py:28-46`, `app/db/models.py:111-112`, `app/reservations/service.py:43-57`

**Q14.** ルートの `conftest.py`（`conftest.py:21-24`）が、`brown` という名前の空モジュールを作り `__path__` を本プロジェクトディレクトリに向けたパッケージエイリアスとして `sys.modules` に登録するため、`brown.tests.conftest` が `tests/conftest.py` に解決されます。これによりテストが動きます。この規約に合わせた理由は同ファイルのdocstring（`conftest.py:1-8`）に「既存テストのソースは一切変更せず、この規約を成立させるための追加設定」とある通り、既存テストのimport規約を書き換えずに成立させるためです。根拠: `conftest.py:1-24`

**Q15.** 旧スキーマの `reservations.db` がある環境で起動すると、`create_all()`（`app/main.py:42`）が呼ばれ、まず `_ensure_series_id_column` が既存 `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE` で追加し、続く `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します（`app/db/database.py:54-62`）。2回目の起動では列は既に存在しテーブルも作成済みのため、`_ensure_series_id_column` も `create_all` も冪等に何もせず、DBは変化しません。根拠: `app/db/database.py:36-62`, `app/main.py:41-43`

**Q16.** 手順: (1) 仮想環境を有効化 `source .venv/bin/activate`（未作成なら `python -m venv .venv`）、(2) `pip install -r requirements.txt`、(3) リポジトリルートで `pytest` を実行（README 60-64行）。ルートの `conftest.py` が `app` と `brown` のimport解決を行うため、ルートから実行する必要があります。実際に実行すると **66 passed** となります（`test_availability_api`5 + `test_overlaps`7 + `test_recurrence`9 + `test_recurring_api`18 + `test_recurring_pbt`5 + `test_reservations_api`13 + `test_rooms_api`9 = 66）。根拠: `README.md:60-66`, 実行結果 `66 passed`

**Q17.** Pydanticスキーマ側では検出されません。`count` は `Field(None, ge=1, ...)`（`app/series/schemas.py:18-20`）で下限のみ、上限がないため count=100 は422になりません。`generate_occurrences` は上限超過でも件数判定できるよう最大 `max_count+1`（=53件）まで生成して打ち切り（`app/series/recurrence.py:36-40`）、その後 `RecurringReservationService.create_series` の `if len(occurrences) > MAX_OCCURRENCES:` で検出して400（ValidationError）を返します（`app/series/service.py:66-70`、BR-RS-C7）。つまりサービス層で件数比較により検出します。テスト `test_over_max_count_400`（`tests/test_recurring_api.py:108-112`）参照。根拠: `app/series/service.py:66-70`, `app/series/recurrence.py:36-40`, `app/series/schemas.py:18-20`

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。モデルはナイーブ（ローカル）datetimeで保存し（`app/db/models.py:1-8` の「時刻はナイーブ datetime（ローカル）」）、READMEの「設計上の割り切り（今回のスコープ外）」にタイムゾーンが挙げられています（`README.md:82-83`）。よってTZ変換レイヤは存在しません。根拠: `app/db/models.py:1-8`, `README.md:82-83`

**Q19.** できません。このシステムは週次（7日刻み固定）のみをサポートし、`RecurringReservationCreate`（`app/series/schemas.py:11-23`）には間隔を指定するパラメータがなく、`generate_occurrences` は `WEEK = timedelta(days=7)` 固定です（`app/series/recurrence.py:10,37`）。READMEでも「隔週・月次などの複雑な繰り返し」はスコープ外と明記（`README.md:82-83`）。隔週・月次を指定する手段はありません。根拠: `app/series/schemas.py:11-23`, `app/series/recurrence.py:10,37`, `README.md:82-83`

**Q20.** 分かりません。このリポジトリには認証機能自体が実装されておらず（認証トークンやその有効期限設定はコード上に存在しません）、READMEの「設計上の割り切り」でも「認証・権限」がスコープ外と明記されています（`README.md:82-83`）。したがって認証トークンの有効期限を設定する箇所は存在しません。根拠: `README.md:82-83`, `app/core/config.py`（認証関連設定なし）
