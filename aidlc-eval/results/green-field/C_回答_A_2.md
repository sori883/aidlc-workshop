調査完了。66件のテストが全てパスすることも確認しました。以下、20問に回答します。

なお前提として、この cond-A リポジトリ（`work/brown-field/cond-A/`）には設計ドキュメント（aidlc-docs）が含まれておらず、根拠はコード・コメント・README・テストに限られます。コメント中に `BR-RS-*` 等の業務ルール番号は参照されていますが、その定義書自体はこのリポジトリには存在しないため、「経緯・理由」が明文化されていない箇所はその旨を明記します。

---

**Q1.** 「1回でも重複するとシリーズ全体を409で拒否する」のは、シリーズと全回を単一トランザクションで登録する**原子性（all-or-nothing）**を業務ルールとして採用しているためです。`app/series/service.py:78-81` に「BR-RS-OV1/OV2: 1回でも重複すればシリーズ全体を拒否（原子性）」、`README.md`（API概要表）にも「1回でも重複すると全体409」と明記されています。テスト `test_conflict_rejects_whole_series_atomically`（`tests/test_recurring_api.py:68-89`）が「シリーズの回は1件も作られない」ことを検証しています。ただし「重複回だけスキップする案を採らなかった具体的な検討経緯・比較理由」を記した文書はこのリポジトリには無く、原子性という結論のみが記録されています。根拠: `app/series/service.py`, `tests/test_recurring_api.py`, `README.md`。

**Q2.** 上限52回は `MAX_OCCURRENCES = 52`（`app/series/service.py:22`）および `generate_occurrences` の `max_count: int = 52`（`app/series/recurrence.py:18`）で定義されています。ただし「なぜ52か」という理由はコード・コメント・READMEのいずれにも記載されていません。週次で約1年分に相当する値ではありますが、リポジトリからその意図の根拠は確認できないため、確定的な理由は**分からない**。根拠: `app/series/service.py`, `app/series/recurrence.py`。

**Q3.** 定期予約の各回は通常の `Reservation` レコードとして展開され（`series_id` で紐付くだけ）、個別回は既存の単発キャンセルAPI `POST /reservations/{reservation_id}/cancel` をそのまま流用できるためです。専用APIは不要という設計で、`tests/test_recurring_api.py:161-173`（`test_individual_occurrence_cancel_via_existing_api`、コメント「既存の個別キャンセル API を流用（US-R05）」）が、シリーズ1回分を既存APIでキャンセルし他の回が active のまま残ることを検証しています。個別回のキャンセルは `POST /reservations/{その回のid}/cancel` で行います。根拠: `tests/test_recurring_api.py`, `app/reservations/router.py`, `app/reservations/service.py`。

**Q4.** `generate_occurrences` を純粋関数として分離した理由は、モジュールのdocstringに明記されています:「副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想。」（`app/series/recurrence.py:1-5`）。DBに依存しないため単体テスト（`tests/test_recurrence.py`）とProperty-Based Test（`tests/test_recurring_pbt.py`）が容易に書けます。既存の重複判定 `overlaps`（`app/availability/service.py:14`）と同じ「ロジックを純粋関数に切り出す」設計方針に揃えたものです。根拠: `app/series/recurrence.py`。

**Q5.** `app/db/database.py:36-51` の `_ensure_series_id_column` が理由をコメントで説明しています:「Base.metadata.create_all は未作成テーブルしか作らず、既存テーブルへの列追加は行わないため、定期予約機能で追加した series_id を既存 DB にも反映する」。つまり `create_all` 方式（マイグレーションツール非使用）の既存構成の中で、既存 `reservations` テーブルへ `series_id` を冪等に足すための最小限の手当てです。実際 `requirements.txt` にAlembic等は含まれていません。ただし「Alembicを敢えて採らなかった」という明示的な意思決定の記録はこのリポジトリには無く、既存の軽量な `create_all` 構成に合わせた結果と読み取れる範囲です。根拠: `app/db/database.py`, `requirements.txt`。

**Q6.** hypothesis は Property-Based Testing（PBT）のために追加されています（`requirements.txt:7`、`tests/test_recurring_pbt.py`）。一部にしか適用されていない理由は、PBT対象が純粋関数 `generate_occurrences` とPydanticスキーマに限られているためで、テストのdocstringに「純粋関数・スキーマが対象のため DB 非依存」「PBT Partial モードで強制対象の PBT-02（Round-trip）/ PBT-03（Invariant）… に対応」と記されています（`tests/test_recurring_pbt.py:1-6`）。DBやAPI層は副作用を持ちPBT向きでないため、DB非依存な純粋部分にのみ適用する方針です。根拠: `requirements.txt`, `tests/test_recurring_pbt.py`。

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行い、`overlaps` は `start_a < end_b and start_b < end_a` を返すため、`end == start`（隣接）は重ならない扱いになります（`app/availability/service.py:14-19`、コメント「隣接（end_a == start_b など）は重ならない扱い」）。したがって「10:00終了」と「10:00開始」は境界が接するだけで重複せず、両方予約できます。根拠: `app/availability/service.py`, `README.md`（「隣接はOK、重なりは409」）。

**Q8.** 含まれます（inclusive）。`until` は日付として扱われ、`if occ_start.date() > until: break` という条件のため、開始日が `until` と等しい回（2030-01-15開始）は生成対象に含まれます（`app/series/recurrence.py:42-53`）。テスト `test_until_inclusive_boundary`（`tests/test_recurrence.py:34-38`）が境界日を含むことを確認しています。根拠: `app/series/recurrence.py`, `tests/test_recurrence.py`。

**Q9.** 両方指定すると 400 になります。`(count is None) == (until is None)` が真になり `ValidationError`（→400）が投げられます（`app/series/service.py:50-53`）。両方省略した場合も同じ条件で真となり 400 です。テスト `test_both_count_and_until_400` / `test_neither_count_nor_until_400`（`tests/test_recurring_api.py:92-105`）で確認されています。根拠: `app/series/service.py`, `tests/test_recurring_api.py`。

**Q10.** 作成できます。定期予約では最初の回について `if occurrences[0][0] < datetime.now(): raise ...` と「未満」判定のため、`start == now` は許可されます（`app/series/service.py:71-73`、コメント「start == now は許可」）。単発予約も `if start_time < datetime.now()` で同様に許可されます（`app/reservations/service.py:40-42`）。根拠: `app/series/service.py`, `app/reservations/service.py`。

**Q11.** `cancel_series` は `list_future_active_by_series`（`start_time > now` かつ `status == active`）のみを cancelled にします（`app/series/service.py:130-141`, `app/reservations/repository.py:60-72`）。
(a) 過去に開始済みの回（`start_time <= now`）: 対象外なので変更されず active のまま残ります。
(b) 既にキャンセル済みの回: `status == active` の絞り込みで対象外のため、そのまま cancelled のままです。
(c) もう一度実行: 未来のactive回が無ければ何も更新せず 200 を返す冪等動作です（テスト `test_cancel_series_idempotent`、`tests/test_recurring_api.py:147-154`）。根拠: `app/series/service.py`, `app/reservations/repository.py`, `tests/test_recurring_api.py`。

**Q12.** リクエスト契約（`ReservationCreate`）は変更なしです。レスポンス契約 `ReservationOut` には `series_id: str | None = None` フィールドが追加されました（単発予約では `None`）（`app/reservations/schemas.py:28-29`）。テスト `test_single_reservation_has_null_series_id`（`tests/test_recurring_api.py:200-213`）が単発予約で `series_id` が `null` になることを確認しています。根拠: `app/reservations/schemas.py`, `tests/test_recurring_api.py`。

**Q13.** DBレベルの制約では実現されていません。ダブルブッキング防止は `AvailabilityService.has_conflict` が対象会議室のactive予約をクエリしPython側の `overlaps` ループで判定する方式で（`app/availability/service.py:28-46`）、DBに UniqueConstraint 等は無く、`reservations(room_id, status)` は性能用の通常インデックスのみです（`app/db/models.py:111-112`）。したがってチェックと挿入の間に分離があり、同時到来した並行リクエストは二重予約が起こりえます（SQLite利用・`check_same_thread` も無効化）。根拠: `app/availability/service.py`, `app/db/models.py`, `app/db/database.py`。

**Q14.** リポジトリ直下の `conftest.py` が、`brown` という名前をこのプロジェクトディレクトリへのパッケージエイリアスとして `sys.modules` に登録しているためです（`conftest.py:21-24`、`_brown.__path__ = [_here]`）。これにより `brown.tests.conftest` が実体の `tests/conftest.py` に解決されます。この規約に合わせた理由もconftestに明記されており、「既存テストのソースは一切変更せず、この規約（`from brown.tests.conftest import ...`）を成立させるための追加設定」とあります（`conftest.py:1-7`）。既存テストの `import` 形式を書き換えずに動かすためです。根拠: `conftest.py`。

**Q15.** 起動時に `create_all()` が呼ばれ（`app/main.py:42`）、まず `_ensure_series_id_column` が既存 `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` で追加し、続く `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します（`app/db/database.py:36-62`）。2回目の起動では、列存在チェック（`if "series_id" not in columns`）とテーブル存在チェックにより何も変更されません（冪等）。根拠: `app/db/database.py`, `app/main.py`。

**Q16.** 手順: リポジトリディレクトリ（`work/brown-field/cond-A`）で仮想環境を作成・有効化し依存をインストール、`pytest` を実行します（`README.md`「テスト」節、`python -m venv .venv` → `source .venv/bin/activate` → `pip install -r requirements.txt` → `pytest`）。実際に `python -m pytest -q` を実行した結果 **66件パス**（`66 passed`）でした。根拠: `README.md`, 実行結果（`tests/` 配下 test_*.py）。

**Q17.** サービス層で検出します。`generate_occurrences` は無制限生成を防ぐため最大 `max_count + 1`（=53）件で打ち切って返し（`app/series/recurrence.py:24-52`）、`RecurringReservationService.create_series` が `if len(occurrences) > MAX_OCCURRENCES:` で上限超過を判定して `ValidationError`（→400）を投げます（`app/series/service.py:66-70`）。スキーマ側 `count` は `ge=1` のみで上限バリデーションは持たないため（`app/series/schemas.py:18-20`）、上限超過はサービス層で検出される設計です。テスト `test_over_max_count_400`（count=53→400）、`test_over_max_count_is_bounded`（count=100→53件で打ち切り）で確認できます。根拠: `app/series/recurrence.py`, `app/series/service.py`, `tests/`。

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。時刻は一貫してナイーブ `datetime`（ローカル）で扱われ（`app/db/models.py:4` コメント「時刻はナイーブ datetime（ローカル）」）、`grep` でも `timezone/tzinfo/astimezone` 等は一切ヒットしません。READMEも「タイムゾーン」を設計上のスコープ外として明記しています（`README.md`「設計上の割り切り」）。したがってタイムゾーン変換は存在しません。根拠: `app/db/models.py`, `README.md`, コード全体検索結果。

**Q19.** 隔週・月次の定期予約を作成する手段はありません。生成ロジックは週次固定（`WEEK = timedelta(days=7)`、7日刻み固定、`app/series/recurrence.py:10`）で、リクエストスキーマ `RecurringReservationCreate` にも間隔・頻度を指定するパラメータは存在しません（`app/series/schemas.py:11-23`）。READMEでも「隔週・月次などの複雑な繰り返し」はスコープ外と明記されています（`README.md`「設計上の割り切り」）。よって指定できるパラメータは無く、作成できません。根拠: `app/series/recurrence.py`, `app/series/schemas.py`, `README.md`。

**Q20.** 設定箇所は存在しません。このシステムには認証機構自体が実装されておらず（`token`/`auth`/`jwt` 等はコード全体で一切ヒットしません）、設定 `Settings` も `DATABASE_URL`/`HOST`/`PORT` のみです（`app/core/config.py`）。READMEも「認証・権限」をスコープ外と明記しています（`README.md`「設計上の割り切り」）。したがって認証トークンの有効期限を設定する場所は無く、該当機能は存在しません。根拠: `app/core/config.py`, `README.md`, コード全体検索結果。
