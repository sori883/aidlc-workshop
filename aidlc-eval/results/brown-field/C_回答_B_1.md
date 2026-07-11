調査が完了しました。以下、20問すべてに回答します。

---

**Q1.** 「重複した回だけスキップ」ではなく「シリーズ全体を409拒否」にした理由は、**要件確定時にユーザーが明示的に「全体拒否（原子性優先）」を選択したから**です。`aidlc-docs/inception/requirements/requirement-verification-questions.md` の Question 1 で、A）全体拒否、B）スキップ作成、C）呼び出し側が選択、の3択が提示され、回答は「A) 全体拒否 — 1回でも重複があればシリーズ全体を作成せず 409」でした（同ファイル冒頭の回答済みサマリ Q1、および `requirements.md` FR-1.7相当）。実装は `app/series/service.py:78-81` で、全回のいずれかが `has_conflict` なら `ConflictError` を送出し、`series` と全回を単一トランザクションで登録する設計（同 78行コメント「原子性」）になっています。

**Q2.** 上限52回は**「約1年（52週）」に相当するため**です。`requirement-verification-questions.md` Question 4 の選択肢A「上限を設ける（推奨。例: 最大52回=約1年。超過時は 400）」が採用され、`requirements.md:34` FR-1.5、`business-rules.md` BR-RS-C7 に反映されています。週次繰り返しで52回＝1年分を上限とし、無限・過大なシリーズ生成を防ぐ意図です（`app/series/service.py:22` `MAX_OCCURRENCES = 52`）。

**Q3.** 専用APIが無いのは、**各回が通常の予約行（`series_id` を持つ `reservations` レコード）として展開されており、既存の単発キャンセルAPIをそのまま流用できるから**です。`requirement-verification-questions.md` Question 7 で選択肢A「既存の `POST /reservations/{reservation_id}/cancel` をそのまま使う」が選ばれ（`requirements.md:48-50` FR-3、`application-design-plan.md:19`「個別回キャンセルは既存 API 流用のため新規コンポーネント不要」）。個別回のキャンセルは、対象回の予約IDを使って `POST /reservations/{reservation_id}/cancel` を呼びます（実装 `app/reservations/router.py:51-56`）。

**Q4.** 週次生成ロジックを純粋関数として分離した理由は、**副作用（DB・トランザクション）を切り離して単体テスト／Property-Based Testingを容易にするため**であり、既存の `overlaps` 関数と同じ「Functional Core / Imperative Shell」設計思想に揃えたためです。`app/series/recurrence.py:1-5` のモジュールドキュメント、`nfr-design-patterns.md` P-3「純粋関数の分離」（根拠「既存 `overlaps` と同じ思想。単体テスト/PBT を容易化」）、`nfr-requirements.md` NFR-RS-6 に記載があります。

**Q5.** Alembic等を使わずSQL直書きヘルパにした理由は、**既存プロジェクトがマイグレーションツールを導入しておらず、追加依存を最小化しつつ、起動時 `create_all()` を拡張して冪等にスキーマ反映する方針を採ったから**です。`aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md:15-41` に「決定: 軽量な自動 ALTER ヘルパ（冪等）」とあり、`Base.metadata.create_all` は既存テーブルへの列追加を行わないため、`series_id` 列を `ALTER TABLE ... ADD COLUMN` で補う設計です（実装 `app/db/database.py:36-62`）。SQLite限定・FK厳密付与はアプリ層（ORMリレーション）で担保、と割り切っています。

**Q6.** hypothesis の目的は**Property-Based Testing（PBT）フレームワークとして日付生成・重複判定・シリアライズ往復の不変条件を検証するため**です（`tech-stack-decisions.md:17` PBT-09、`requirements.txt:7`）。一部にしか適用していないのは、**要件確定時にPBTを「Partial」モードで採用したから**です。`requirement-verification-questions.md` Question 13 で B）Partial「純粋関数とシリアライズ往復に限定適用」が選ばれ（`requirements.md:77`、`nfr-requirements.md` NFR-RS-6）。純粋関数 `generate_occurrences` とPydanticスキーマがDB非依存でPBTと相性が良い一方、DB絡みのフローは例示ベーステストでカバーする方針です（`tests/test_recurring_pbt.py:1-6`）。

**Q7.** 共存**できます**。重複判定は半開区間 `[start, end)` で行われ、`overlaps` は `start_a < end_b and start_b < end_a` を返します（`app/availability/service.py:14-19`）。10:00終了（end=10:00）と10:00開始（start=10:00）では `10:00 < 10:00` が偽となり重ならない扱い（隣接OK）です。READMEの「隣接はOK、重なりは409」（`README.md:9`）とも一致します。

**Q8.** **含まれます**。`until` は「開始日 <= until（inclusive）」で判定され、`app/series/recurrence.py:48` は `if occ_start.date() > until: break` です。開始日がちょうど 2030-01-15 の回は `> until` が偽なので生成対象に含まれます（`recurrence.py:22-23` のドキュメント、`schemas.py:21-23`「この日以前の開始回まで、inclusive」）。

**Q9.** count と until を**両方指定すると400（ValidationError）**、**両方省略しても400**です。`app/series/service.py:50-53` の `if (count is None) == (until is None):` でどちらか一方のみを要求し、`generate_occurrences` 側でも同じ判定で `ValueError` を送出します（`recurrence.py:28-29`）。要件 FR-1.4（`requirements.md:31`）、BR-RS-C4 に対応します。

**Q10.** **作成できます**。`app/series/service.py:71-73` は `if occurrences[0][0] < datetime.now()` で「過去なら拒否」＝start == now は許可という設計です（コメント「start == now は許可」）。単発予約側も同様（`app/reservations/service.py:40-42`）。要件 Question 10 の「start == now は許可」に対応。ただし判定は `datetime.now()` を都度取得するため、厳密に同一瞬間かはタイミング次第です。

**Q11.** シリーズ全体キャンセル（`app/series/service.py:130-141`）は `list_future_active_by_series` が返す「開始時刻が now より後かつ active」の回のみ cancelled にします。したがって **(a)過去に開始済みの回はキャンセルされず（そのまま）**、**(b)既にキャンセル済みの回も対象外（変更なし）** です（要件 Question 6 のA「未来の active な回のみ」、BR-RS-X1/X2/X3）。**(c)もう一度実行しても**、未来の active 回が無ければ何も変更せずシリーズを返す**冪等**動作です（`repository.py:60-72`、`README.md:42`）。

**Q12.** **リクエスト契約は変更なし。レスポンス契約は後方互換の追加のみ**です。`ReservationOut` に `series_id`（`str | None`、単発は `null`）が**追加**されました（`app/reservations/schemas.py:28-29`、FR-4.1 `requirements.md:53`）。`ReservationCreate`（リクエスト）は不変（`schemas.py:9-14`）。既存テストは等値比較でなく個別フィールド検証のためフィールド追加は既存テストを壊さない、という前提で許容されています（`requirements.md:54`、`execution-plan.md:14`）。

**Q13.** **DBレベルの制約では実現されていません**。重複防止はアプリ層で `AvailabilityService.has_conflict` が対象会議室の active 予約を走査して判定する方式で（`app/availability/service.py:28-46`）、UNIQUE制約や排他ロックはありません（`models.py:111-112` のインデックスは検索効率化のためのもの）。そのため**並行リクエストでは二重予約が起こりえます**。`nfr-design/logical-components.md:37` に「同時実行: SQLite の既定分離レベルに依存。小規模・低同時実行前提のため追加のロック機構は導入しない（スコープ外、NFR-RS-5）」と明記されています。

**Q14.** テストが動くのは、**ルートの `conftest.py` が `brown` という名前を本プロジェクトディレクトリへのパッケージエイリアスとして `sys.modules` に登録しているから**です（`conftest.py:19-24`）。これにより `brown.tests.conftest` が `tests/conftest.py` に解決されます。この規約に合わせた理由は、`conftest.py:6-8` によれば「**既存テストのソースを一切変更しない**」という制約（変更禁止事項＝既存テストの改変不可、`requirement-verification-questions.md:27`）を満たすため、既存テストの `from brown.tests.conftest import ...` という記述を成立させる追加設定として用意されたものです。

**Q15.** 旧スキーマの `reservations.db` がある環境で起動すると、`create_all()` が呼ばれ（`app/main.py:42`）、`_ensure_series_id_column` が `reservations` テーブルに `series_id` 列が無いことを検出して `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を実行し、さらに `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します（`app/db/database.py:36-62`）。**2回起動しても**、列存在チェック（`if "series_id" not in columns`）とテーブル作成の冪等性により**何も追加変更されません**（冪等）。`infrastructure-design.md:37-41` に同旨。

**Q16.** 手順は、README（`README.md:12-24,60-64`）の通り仮想環境を有効化し依存をインストールした上で、プロジェクトルートで `pytest`（または `python -m pytest`）を実行します。ルート `conftest.py` が `app` と `brown` の import 解決を行うため、ルートからの実行が前提です。実測で**66件パス**します（`66 passed`）。

**Q17.** 上限超過は**サービス層で件数によって検出**されます。`generate_occurrences` は無制限生成を防ぐため最大 `max_count + 1`（=53）件まで生成して打ち切り（`app/series/recurrence.py:25-26,39-40,51-52`）、`RecurringReservationService.create_series` が `if len(occurrences) > MAX_OCCURRENCES:` で **400（ValidationError）** を返します（`app/series/service.py:66-70`）。したがって count=100 は生成段階で53件に打ち切られ、件数チェックで上限超過として拒否されます（BR-RS-C7）。Pydantic では `count` は `ge=1` のみで上限は課していません（`schemas.py:18-20`）。

**Q18.** タイムゾーン変換は**どのレイヤでも行われていません**。時刻はナイーブ `datetime`（ローカル）として保存・比較する設計で（`app/db/models.py:3-4` コメント「時刻はナイーブ datetime（ローカル）」）、タイムゾーンはスコープ外と明記されています（`README.md:83`、`nfr-requirements.md:38`）。`availability/service.py` にもTZ変換処理はありません。

**Q19.** **指定できません（分かりません＝機能として存在しない）**。本システムは週次（7日固定間隔）のみをサポートし、隔週・月次はスコープ外です。`app/series/recurrence.py:10` の `WEEK = timedelta(days=7)` が固定で、リクエストに間隔指定パラメータはありません（`schemas.py:11-23`）。`README.md:83` に「隔週・月次などの複雑な繰り返し」はスコープ外と明記されています。

**Q20.** **分かりません（設定箇所は存在しません）**。認証・トークンの仕組み自体がこのシステムに実装されていません。認証・権限はスコープ外と明記され（`README.md:83`、`nfr-design-patterns.md:45`「認証/認可/暗号化 N/A」）、`app/core/config.py` にも `database_url`・`host`・`port` のみで認証トークンや有効期限の設定はありません。
