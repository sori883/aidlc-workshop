調査完了しました。cond-A リポジトリ内のファイル（コード・コメント・README・テスト）を根拠に回答します。なお、設計意図を記した `aidlc-docs`（business-rules.md 等）は**このリポジトリ（cond-A）には含まれていない**ため、コード/コメント/README に根拠がない「なぜ」については推測せず「分からない」と明記します。

---

**Q1.** 挙動そのものは意図的です。`app/series/service.py:78-81` のコメントに「BR-RS-OV1/OV2: 1回でも重複すればシリーズ全体を拒否（原子性）」とあり、`app/series/service.py:83` でも series と全回を単一トランザクションで登録する「all-or-nothing」設計だと明記されています（README.md:41 も「1回でも重複すると全体 409」）。つまり「シリーズは全回そろって成立する原子的単位」という設計判断が根拠です。ただし「重複回だけスキップする案を採らなかった具体的な検討経緯」自体は、このリポジトリ内（cond-A）には記述が見当たらないため、原子性という設計方針以上の理由・経緯は**分からない**です。

**Q2.** 上限52は `app/series/service.py:22`（`MAX_OCCURRENCES = 52`）と `app/series/recurrence.py:18`（`max_count: int = 52`）に定義されています。しかし「なぜ52なのか」という理由・根拠を説明した記述はリポジトリ内に見当たりません（週次で約1年分＝52週に相当しますが、そう明記した根拠はありません）。したがって理由は**分からない**です。

**Q3.** シリーズ内の個別回をキャンセルする専用APIは、`app/series/router.py` にシリーズ単位の `/reservations/recurring/{series_id}/cancel` しか無く、存在しません。個別回は既存の単発キャンセルAPI **`POST /reservations/{reservation_id}/cancel`** で行えます。各回は独立した `Reservation`（固有 id と `series_id` を持つ、`app/db/models.py:85-103`）として展開されており、`ReservationService.cancel_reservation` は id で対象を取得し series を問わずキャンセルできる（`app/reservations/service.py:76-83`）ためです。専用APIを設けなかった明示的理由はドキュメント化されていませんが、既存の単発キャンセルで代替可能なことがその方法の根拠です。（根拠: `app/series/router.py`, `app/reservations/router.py:51-56`, `app/reservations/service.py:76-83`）

**Q4.** `app/series/recurrence.py:1-5` の docstring に理由が明記されています。「副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想」。つまり純粋関数にすることで単体テストや Property-Based Testing が容易になり、既存の `overlaps`（`app/availability/service.py:14`）と同じ設計方針に揃えるため、が根拠です。

**Q5.** メカニズム面の理由は `app/db/database.py:36-52` のコメントに記載があります。「`Base.metadata.create_all` は未作成テーブルしか作らず、既存テーブルへの列追加は行わない」ため、`_ensure_series_id_column` が `ALTER TABLE ... ADD COLUMN series_id` を冪等に実行する、という説明です。ただし「なぜ Alembic 等のマイグレーションツールを使わなかったのか」という選択理由そのものは記述されていません（requirements.txt にも alembic は無く軽量な方針がうかがえますが、明示的な理由の記載はありません）。よって道具選定の理由は**分からない**です。

**Q6.** hypothesis の目的は Property-Based Testing の実施で、`tests/test_recurring_pbt.py` で `generate_occurrences`（純粋関数）と `RecurringReservationCreate`（スキーマ）に対する不変条件・往復（round-trip）テストに使われています（requirements.txt:7、`tests/test_recurring_pbt.py:1-14`）。一部にしか適用されていない理由も同ファイルの docstring に「純粋関数・スキーマが対象のため DB 非依存」とあり、PBT を適用しやすい純粋関数/スキーマに限って適用しているためです（`tests/test_recurring_pbt.py:1-8`）。

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行われ、`overlaps` は `start_a < end_b and start_b < end_a`（`app/availability/service.py:14-19`）です。10:00終了予約（end=10:00）と10:00開始予約（start=10:00）は `start_b < end_a` が `10:00 < 10:00 = False` となり重ならない扱いになります。README.md:9 も「隣接はOK」と明記しています。

**Q8.** 含まれます。`app/series/recurrence.py:47-50` で `if occ_start.date() > until: break`、それ以外は生成対象に追加、というロジックのため、開始日が until と等しい回（2030-01-15開始）は inclusive で含まれます。docstring（`recurrence.py:23`）にも「開始日 <= until の回まで（inclusive）」とあります。

**Q9.** 両方指定するとエラーです。`app/series/service.py:50-53`（BR-RS-C4）で `(count is None) == (until is None)` が真ならば `ValidationError` を送出し、`app/common/errors.py:11-13` により **400** になります。両方省略した場合も同じ条件式が真になるため同様に **400** です（両方指定＝両方 not None、両方省略＝両方 None のどちらも `== ` が真）。

**Q10.** 作成できます。単発予約は `app/reservations/service.py:41` が `if start_time < datetime.now()` の時のみ拒否し、コメントに「start == now は許可」とあります。定期予約も `app/series/service.py:72` が `occurrences[0][0] < datetime.now()` の時のみ拒否（「start == now は許可」）です。したがって現在時刻とちょうど同じ start_time は可能です。

**Q11.** `app/series/service.py:130-141` の `cancel_series` は `list_future_active_by_series`（`start_time > now` かつ `status == active`、`app/reservations/repository.py:60-72`）のみを cancelled にします。
- (a) 過去に開始済みの回（`start_time <= now`）: 対象外なので **active のまま変わりません**。
- (b) 既にキャンセル済みの回: `status == active` 条件で除外されるため **変わりません**。
- (c) もう一度実行: 未来の active 回はもう存在しないため `future_active` が空になり、何も更新せず series を返す **冪等**動作です（README.md:42 も「冪等」）。

**Q12.** リクエスト契約は変更なし、レスポンス契約は加算的に変更されました。`ReservationOut` に `series_id: str | None = None` が追加されています（`app/reservations/schemas.py:29`）。git 履歴でも定期予約追加コミット（878f9bd）でこの1行が追加され、`ReservationCreate`（リクエスト）は不変であることを確認しました。よって単発予約のレスポンスに任意フィールド `series_id`（単発は None）が増えた後方互換の変更です。

**Q13.** DBレベルの制約では実現されていません。`app/db/models.py:112` にあるのは非ユニークな `Index("ix_reservations_room_id_status", ...)` のみで、UNIQUE/排他制約はありません。防止はアプリケーション層の「検索→重複判定」（`AvailabilityService.has_conflict` が active 予約を走査、`app/availability/service.py:28-46`）で行われます。この方式は check-then-insert であり、並行リクエストが同時に来た場合はどちらも「重複なし」と判定してから挿入し得るため、**二重予約は起こりえます**（TOCTOU 競合）。単一トランザクション内でチェックしていますが（`service.py:43`）、セッションをまたぐ同時実行を排他する仕組みはありません。

**Q14.** ルートの `conftest.py:21-25` が、`brown` という名前の `ModuleType` を生成し `__path__` を本ディレクトリに向けて `sys.modules["brown"]` に登録しているためです。これにより `brown.tests.conftest` が実体の `tests/conftest.py` に解決され、`create_room` 等が import できます。規約に合わせた理由も同ファイルの docstring（`conftest.py:1-8`）に「既存テストのソースは一切変更せず、この規約を成立させるための追加設定」と明記されており、既存テストを書き換えずに `from brown.tests.conftest import ...` を成立させるためです。

**Q15.** 旧スキーマの `reservations.db` がある環境で起動すると、`create_all`（`app/db/database.py:54-62`）が動き、まず `_ensure_series_id_column` が `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE ... ADD COLUMN series_id VARCHAR(36)` を実行して列を追加し、次に `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します。2回目の起動では、`series_id` 列は既に存在するので追加をスキップ（`database.py:47` の冪等判定）、テーブルも既存なので `create_all` は何もしません。つまり冪等で、2回起動しても追加の変更は起きません。

**Q16.** 手順（README.md:12-24, 60-64 準拠）: ①`python -m venv .venv` で仮想環境作成 → `source .venv/bin/activate` で有効化、②`pip install -r requirements.txt`、③リポジトリルートで `pytest`（または `python -m pytest`）を実行。実際に実行したところ **66 件パス**しました（`66 passed`）。

**Q17.** まず Pydantic スキーマ `count: int | None = Field(None, ge=1, ...)`（`app/series/schemas.py:18-20`）には上限が無いため count=100 はバリデーションを通過します。次に `generate_occurrences` が呼ばれ、`app/series/recurrence.py:36-40` で件数が `max_count`(=52) を超えると `len(occurrences) > max_count` で `break` し、最大 `max_count + 1`（=53）件で打ち切ります。最後に `RecurringReservationService.create_series` の `app/series/service.py:67-70`（BR-RS-C7）で `len(occurrences) > MAX_OCCURRENCES` を検出し `ValidationError` → **400** を返します。つまり上限超過はサービス層の件数チェックで検出されます。

**Q18.** どのレイヤでもタイムゾーン変換は行っていません。`app/db/models.py:3-4` のモジュール docstring に「時刻はナイーブ datetime（ローカル）」とあり、`DateTime`（tz なし）で保持しています。README.md:83 でもタイムゾーンは「今回のスコープ外」と明記されています。したがって変換レイヤは存在しません。

**Q19.** 指定できるパラメータはありません。`RecurringReservationCreate`（`app/series/schemas.py:11-23`）が受け付けるのは `count`／`until` のみで、生成ロジックは7日刻み固定（`app/series/recurrence.py:10` `WEEK = timedelta(days=7)`）の**週次のみ**です。README.md:83 でも「隔週・月次などの複雑な繰り返し」はスコープ外とされており、隔週・月次を作る手段はありません。

**Q20.** 認証機能自体が存在しないため、トークンの有効期限を設定する箇所はありません。`app/core/config.py` には `database_url`／`host`／`port` しか無く、README.md:83 でも「認証・権限」はスコープ外と明記されています。したがって設定箇所は無い（該当なし）です。
