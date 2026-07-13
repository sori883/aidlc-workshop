調査完了です。cond-A の作業ツリーには README.md 以外の設計ドキュメント（`aidlc-docs`, `business-rules.md` 等）は含まれていません。コード内コメントは `business-rules.md` の BR-ID を参照していますが、その実ファイルはこのリポジトリ（cond-A）内には存在しません。この点を踏まえ、コード・コメント・README・テストの実挙動を根拠に回答します。根拠のない「理由・経緯」は推測で埋めず「分からない」と明記します。

---

**Q1.** 「1回でも重複するとシリーズ全体を409」という挙動そのものは実装・仕様として明確です。`app/series/service.py:78-81` に「BR-RS-OV1/OV2: 1回でも重複すればシリーズ全体を拒否（原子性）」とあり、生成した全回を事前にループで重複チェックし、1件でもコンフリクトすれば `ConflictError`（409）を投げます。README.md:41 にも「1回でも重複すると全体 409」と明記され、`tests/test_recurring_api.py:68`（`test_conflict_rejects_whole_series_atomically`）で「シリーズの回は1件も作られない」原子性が検証されています。ただし「重複回だけスキップして残りを作成する仕様にしなかった具体的な理由・経緯」を説明した記述は、この cond-A リポジトリ内には見当たりません（コメントは設計原則として「原子性」を掲げるのみ）。したがって、採用理由が「原子性を優先したこと」までは根拠がありますが、代替案（スキップ）を退けた詳細な経緯は分からない。

**Q2.** 上限値が52であること自体は `app/series/service.py:22`（`MAX_OCCURRENCES = 52`）および `app/series/recurrence.py:18`（`max_count: int = 52`）に根拠があります。しかし「なぜ52なのか」を説明する記述は cond-A 内にありません。週次で52回はおおむね1年分（1年＝約52週）に対応しますが、これはコード・READMEに明記された理由ではなく推測になるため、確たる理由は分からない。

**Q3.** 個別回は展開時に通常の `Reservation` 行として独立した `id` を持って作成されるため（`app/series/service.py:106-118`）、専用APIを設けず既存の単発キャンセルAPIを流用する設計です。個別回のキャンセルは既存の `POST /reservations/{reservation_id}/cancel` を使います。`tests/test_recurring_api.py:161-173`（`test_individual_occurrence_cancel_via_existing_api`、コメント「既存の個別キャンセル API を流用（US-R05）」）で、対象回のみ cancelled になり他の回は active のまま、が検証されています。

**Q4.** `app/series/recurrence.py:1-5` のモジュール docstring に理由が明記されています：「副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想。」つまり、日付生成ロジックを純粋関数にすることで単体テストおよびProperty-Based Testを容易にするため、そして既存の `overlaps`（`app/availability/service.py:14`）と同じ設計方針に揃えるためです。

**Q5.** 実装は `app/db/database.py:36-51`（`_ensure_series_id_column`）で、`inspect` により `reservations` に `series_id` 列が無ければ `ALTER TABLE ... ADD COLUMN` を実行する冪等ヘルパになっています。docstring は「`Base.metadata.create_all` は未作成テーブルしか作らず既存テーブルへの列追加は行わないため」と、この関数が必要な理由は説明しています。一方「Alembic等のマイグレーションツールを使わずSQL直書きにした理由」は cond-A 内に明記されていません。事実として `requirements.txt` に Alembic は無く、ローカルSQLite前提の小規模アプリ（README.md:3-4）である点は根拠になりますが、ツール選定を退けた明示的な経緯は分からない。

**Q6.** `hypothesis` は Property-Based Testing のための依存で、`tests/test_recurring_pbt.py` が唯一の利用箇所です（`generate_occurrences` の不変条件検証やスキーマのラウンドトリップ）。一部にしか適用されていない理由は同ファイルの docstring（`tests/test_recurring_pbt.py:1-6`）に根拠があり、「PBT Partial モードで強制対象」であること、および「純粋関数・スキーマが対象のため DB 非依存」であることが述べられています。つまりDB非依存で不変条件が明確な純粋関数・スキーマにのみPBTを適用する方針です。なお「PBT Partial モード」の定義そのもの（なぜPartialか）を説明した文書は cond-A 内には無い。

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行われ、`app/availability/service.py:14-19`（`overlaps`）は `start_a < end_b and start_b < end_a` で、隣接（`end == start`）は重ならない扱いです。README.md:9 にも「半開区間で判定。隣接はOK」とあります。したがって「10:00終了」と「10:00開始」は接するだけで重ならず、両方作成できます。

**Q8.** 含まれます（until は inclusive）。`app/series/recurrence.py:48` は `if occ_start.date() > until: break` で、開始日が until と等しい回は打ち切られず生成対象に残ります。スキーマ（`app/series/schemas.py:21-23`）にも「この日以前の開始回まで、inclusive」とあります。ただしこれは「週次の刻みが実際に 2030-01-15 に着地する場合」に限られます（起点の曜日から7日刻みでその日に一致する回が存在すれば、という前提）。存在すれば inclusive で含まれます。

**Q9.** 両方指定すると400（`ValidationError`）です。`app/series/service.py:50-53` で `(count is None) == (until is None)` を検出して弾き、`app/series/recurrence.py:28-29` でも `ValueError` になります。両方省略しても同じく400です（同じ条件式が両ケースを捕捉）。`tests/test_recurring_api.py:92`（`test_both_count_and_until_400`）と `:101`（`test_neither_count_nor_until_400`）で検証されています。

**Q10.** 作成できます。単発は `app/reservations/service.py:41`（`if start_time < datetime.now()`、コメント「start == now は許可」）で、過去のみ拒否し「ちょうど現在時刻」は許可します。定期予約も `app/series/service.py:72`（`if occurrences[0][0] < datetime.now()`）と同じく厳密不等号なので、start == now は許可されます。

**Q11.** キャンセル対象は `app/series/repository.py:60-72`（`list_future_active_by_series`）で `start_time > now` かつ `status == active` の回に限定されます。
(a) 過去に開始済み（`start <= now`）の回はキャンセルされず active のまま残ります。
(b) 既にキャンセル済みの回は `status == active` フィルタから外れるため触られず、cancelled のままです。
(c) もう一度実行しても未来の active 回が残っていないため何も変更されず、200 で冪等に成功します（`app/series/service.py:130-141`、コメント「未来の active 回のみ cancelled（冪等）」、`tests/test_recurring_api.py:147` の `test_cancel_series_idempotent`）。

**Q12.** リクエスト契約（`ReservationCreate`, `app/reservations/schemas.py:9-14`）は変更ありません。一方レスポンス契約は変わっており、`ReservationOut` に nullable な `series_id` フィールドが追加されています（`app/reservations/schemas.py:28-29`、単発予約は `None`）。`tests/test_recurring_api.py:200`（`test_single_reservation_has_null_series_id`）で単発は `series_id: null` を返すことが検証されています。つまり後方互換な追加変更（フィールド増）がレスポンスに入っています。

**Q13.** DBレベルの制約では実現されていません。`app/db/models.py:112` にあるのはパフォーマンス用の複合Index（`ix_reservations_room_id_status`）のみで、ユニーク制約や排他制約はありません。防止は完全にアプリ層で、`app/availability/service.py:28-46`（`has_conflict`）が active 予約を読み出してPythonで重なり判定し、その後に挿入する「チェック→挿入」方式です（`app/series/service.py:79-81`、`app/reservations/service.py:44-45`）。トランザクション分離やロックによる保護は無いため、並行リクエストが同時に来た場合は両者が重複なしと判定して二重予約が起こりえます。

**Q14.** ルートの `conftest.py:21-24` が、`brown` という名前のモジュールを動的に生成し `__path__` を本プロジェクトディレクトリに向けて `sys.modules["brown"]` に登録しているため、`brown.tests.conftest` が `tests/conftest.py` に解決され動作します。この規約に合わせた理由も同ファイルの docstring（`conftest.py:1-8`）に明記されており、「テストは既存規約 `from brown.tests.conftest import create_room` でヘルパを取得する」ため、「既存テストのソースは一切変更せず、この規約を成立させるための追加設定」を入れた、というものです。

**Q15.** 旧スキーマの `reservations.db` がある環境で起動すると、`create_all`（`app/db/database.py:54-62`）がまず `_ensure_series_id_column` を呼び、既存 `reservations` テーブルに `series_id VARCHAR(36)` 列を `ALTER TABLE` で追加します。加えて未作成の `reservation_series` テーブルは `Base.metadata.create_all` で新規作成されます。2回起動しても、`series_id` 列の存在を `inspect` で確認してから追加する冪等実装（`app/db/database.py:44-51`）であり、`create_all` も既存テーブルを再作成しないため、何も壊れず変更も起きません。

**Q16.** cond-A ルートで `pytest` を実行します（README.md:60-64）。仮想環境は同梱の `.venv` を使えばよく、例えば `./.venv/bin/python -m pytest`（またはREADME手順どおり `source .venv/bin/activate` 後に `pytest`）です。実際に実行した結果は **66件パス**（`66 passed`、1 warning）でした。

**Q17.** Pydanticスキーマ側では `count` に `ge=1` のみで上限が無い（`app/series/schemas.py:18-20`）ため、`count=100` は422では弾かれずサービス層に到達します。`app/series/recurrence.py:36-40` が `max_count`(=52) を超えても無制限生成を防ぐため最大 `max_count + 1`（=53件）まで生成して打ち切り、サービス層 `app/series/service.py:66-70` の `if len(occurrences) > MAX_OCCURRENCES:` で件数超過を検出して `ValidationError`（400）にします。つまり「生成件数が上限+1で頭打ち → サービス層で件数判定 → 400」という流れで検出します（`tests/test_recurrence.py:52`、`tests/test_recurring_api.py:108`）。

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。`app/db/models.py:1-8` のコメントに「時刻はナイーブ datetime（ローカル）」とあり、全体を通してタイムゾーン非対応のナイーブ `datetime` を扱っています。README.md:83 でもタイムゾーンは「今回のスコープ外」と明記されています。

**Q19.** 隔週・月次を指定する手段はありません。定期予約は週次固定で、リクエストスキーマ（`app/series/schemas.py:11-23`）には頻度・間隔を指定するパラメータが存在せず、`count` か `until` のどちらか一方しか受け付けません。生成ロジックも7日固定刻みです（`app/series/recurrence.py:10` の `WEEK = timedelta(days=7)`）。README.md:83 に「隔週・月次などの複雑な繰り返し」はスコープ外と明記されています。

**Q20.** 認証機能自体が存在しないため、トークン有効期限の設定箇所もありません。README.md:83 で「認証・権限」はスコープ外と明記され、`app/core/config.py`（設定は `database_url`/`host`/`port` のみ）にもトークン関連の設定はありません。したがって設定箇所は無い（＝該当なし）。
