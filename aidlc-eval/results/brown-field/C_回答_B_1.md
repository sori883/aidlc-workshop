調査完了しました。66件全てのテストがパスすることも確認できました。以下、20問に回答します。

---

**Q1.** 「1回でも重複するとシリーズ全体を409で拒否」する原子性方針は、要件確定時にユーザーが明示的に選択した結果です。`aidlc-docs/inception/requirements/requirement-verification-questions.md` のQuestion 1で「A) 全体拒否（原子性を優先）／B) 重複回だけスキップ／C) パラメータで切替」の3択が提示され、ユーザーは A を選択しました（同ファイル9行目・`aidlc-docs/audit.md` 45行目「Q1=全体拒否」）。この決定が `BR-RS-OV2`（`business-rules.md` 26行目「1回でも…409を返し、series と全回を一切登録しない」）となり、`app/series/service.py:78-81` に実装されています。つまり「スキップ作成にしなかった理由」は技術的制約ではなく、原子性（シリーズ全回が揃わないなら作らない）を優先するというユーザーの意思決定です。

**Q2.** 52回=約1年（週次×52週）だからです。`requirement-verification-questions.md:77`「最大52回=約1年。超過時は 400」、`requirements.md:34` FR-1.5、`business-rules.md:14`（BR-RS-C7）に根拠があります。無限・過大なシリーズ生成を防ぐ上限として、週次予約の現実的な範囲である「約1年」を採用したものです（実装は `app/series/service.py:22` `MAX_OCCURRENCES = 52`）。

**Q3.** 専用APIを作らない方針もユーザーが選択したためです（`requirement-verification-questions.md` Question 7で「A) 既存APIを流用／B) 専用API新設」のうち A を選択、15行目・`audit.md:45`「Q7=既存キャンセルAPI流用」）。シリーズの各回は通常の `Reservation` 行として展開され `series_id` で紐付くだけなので、個別回のキャンセルは既存の `POST /reservations/{reservation_id}/cancel` をそのまま使います（`business-rules.md:45` BR-RS-I1「新規ルール・新規コードなし」、`aidlc-docs/construction/recurring-reservations/functional-design/business-logic-model.md:95-97`）。

**Q4.** 副作用がなくDB非依存で、単体テストとProperty-Based Testingが容易だからです。`app/series/recurrence.py:1-5` のdocstringに「副作用なし・DB非依存でテスト/PBTが容易。overlaps と同じ設計思想」と明記されており、既存の重複判定 `overlaps`（`app/availability/service.py:14`）と同じ「純粋関数として切り出す」設計思想を踏襲したものです（`aidlc-docs/inception/plans/application-design-plan.md:11`）。

**Q5.** このプロジェクトにはもともとマイグレーションツール（Alembic等）が導入されておらず、テーブル作成は起動時の `Base.metadata.create_all` に依存しているためです。`create_all` は未作成テーブルは作るが既存テーブルへの列追加は行わないので、既存DBに `series_id` を反映する手段が別途必要でした。ユーザーは「軽量な自動ALTERヘルパ」を選択し（`audit.md:232`、`infrastructure-design.md:17` 決定・`recurring-reservations-infrastructure-design-plan.md:6`）、新規DB・既存DBの両方でシームレスに動く冪等ヘルパ `_ensure_series_id_column`（`app/db/database.py:36-51`）が実装されました。既存スタックを最大限継承し新規依存追加を最小限にする方針（`tech-stack-decisions.md:30-32`）とも整合します。

**Q6.** hypothesis はProperty-Based Testing（PBT）フレームワークとして追加されました（`requirements.txt:7`、`tech-stack-decisions.md:17`「Python標準的、優れたshrinking、pytest統合」）。一部にしか適用されていない理由は、ユーザーがPBT拡張を「Partial（純粋関数とシリアライズ往復に限定適用）」に設定したためです（`requirement-verification-questions.md` Question 13で B を選択・21行目、`audit.md:45`「Q13=Partial」）。実際 `tests/test_recurring_pbt.py` は純粋関数 `generate_occurrences` の不変条件とスキーマの往復（round-trip）のみが対象で、DB依存部分には適用されていません。

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行われ（`app/availability/service.py:14-19` `overlaps`）、`start_a < end_b and start_b < end_a` で判定します。「10:00終了の予約」＝終了境界が10:00、「10:00開始の予約」＝開始境界が10:00の場合、`start_b(10:00) < end_a(10:00)` が False となり重ならない扱いになります。docstringにも「隣接（end_a == start_b）は重ならない扱い」とあり（同15-18行）、`business-rules.md:25`（隣接OK・重なりNG）に対応します。

**Q8.** 含まれます。`until` は「開始日 <= until（inclusive）」で判定され、`app/series/recurrence.py:48` の `if occ_start.date() > until: break` は「until より後」でのみ打ち切ります。2030-01-15開始の回は `occ_start.date() == until` で `>` にはならないため生成対象に残ります（`recurrence.py:23`・`business-rules.md:13` BR-RS-C6「inclusive」）。

**Q9.** 両方指定すると400エラーになります。`app/series/service.py:50-53`（BR-RS-C4）で `(count is None) == (until is None)` が真（両方指定＝両方not None）のとき `ValidationError` を送出します。両方省略した場合も同じ条件が真（両方None）となり同じく400です。「ちょうど一方のみ」有効という仕様です（`recurrence.py:28-29` でも二重にガード、`business-rules.md:11`）。

**Q10.** 作成できます。`app/series/service.py:72` は `if occurrences[0][0] < datetime.now():` で「現在より前（過去）」のみを拒否し、ちょうど同時刻は `<` を満たさないため許可されます。コメントにも「start == now は許可」とあり（同71行・`business-rules.md:15` BR-RS-C8）。ただし `datetime.now()` はチェック時点で都度評価されるため、厳密に同一時刻を狙うのは現実には困難です。

**Q11.** `app/series/service.py:130-141` `cancel_series` の挙動は次の通りです。(a) 過去に開始済みの回：対象外で変更されません（`list_future_active_by_series` が `start_time > now` の回のみ返すため、`repository.py:60-72`）。(b) 既にキャンセル済みの回：`status == active` の回のみ抽出するため変更されません。(c) もう一度実行：対象となる未来のactive回が残っていなければ何も変更せず、そのまま200を返します（冪等）。これらは `business-rules.md:37-39`（BR-RS-X1/X2/X3）に対応します。

**Q12.** リクエスト契約に変更はありません。`ReservationCreate`（`app/reservations/schemas.py:9-14`）は不変です（`business-rules.md:50` BR-RS-D2「後方互換」）。レスポンス契約は、`ReservationOut` に `series_id`（単発は `None`、デフォルト値付き）が**追加**されました（`app/reservations/schemas.py:29`、`business-rules.md:48-49` BR-RS-D1）。これはユーザーがQuestion 9で「A) `ReservationOut` に `series_id` を追加」を選択した結果で、既存テストは等値比較でなく個別フィールド検証のため追加は許容される、という前提です（`requirement-verification-questions.md:142`）。

**Q13.** いいえ、DBレベルの制約では実現されていません。重複防止はアプリケーション層で、対象会議室のactive予約を走査して `overlaps` で判定する方式です（`app/availability/service.py:28-46`）。`app/db/models.py:112` にあるのは検索効率化のための**非ユニーク**インデックス `ix_reservations_room_id_status` のみで、排他制約はありません。したがって並行リクエストが同時に来た場合、「チェック→INSERT」の間にロックがないため二重予約は起こりえます（check-then-actのレースコンディション）。

**Q14.** ルートの `conftest.py`（`/Users/const/.../cond-B/conftest.py`）が、`brown` という名前のモジュールエイリアスを動的に登録し、その `__path__` をプロジェクトルートに向けているためです（`conftest.py:21-25`）。これにより `brown.tests.conftest` は `tests/conftest.py` に解決され、`create_room` がimportできます（各テストの `from brown.tests.conftest import create_room`、`tests/test_recurring_api.py:4` 等）。この規約に合わせた理由は、「既存テストのソースを一切変更しない」という制約下で既存の `brown.*` import 規約を成立させるためです（`conftest.py:1-8` のdocstring「既存テストのソースは一切変更せず、この規約を成立させるための追加設定」）。

**Q15.** 起動時に `create_all()`（`app/db/database.py:54-62`）が走ります。既存の `reservations.db`（旧スキーマ）がある場合、`reservations` テーブルは既に存在するので `_ensure_series_id_column` が列を検査し、`series_id` 列が無ければ `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を1度だけ実行します（同36-51行）。加えて `Base.metadata.create_all` が未作成の新テーブル `reservation_series` を追加します。2回目の起動では、`series_id` 列が既に存在するのでALTERはスキップされ（冪等）、`create_all` も既存テーブルには何もしないため、DBに追加の変更は起きません（`infrastructure-design.md:17-21`）。

**Q16.** 手順：(1) 依存をインストール（`pip install -r requirements.txt`、`requirements.txt` に fastapi/pytest/httpx/hypothesis 等）。(2) プロジェクトルート（`cond-B/`）で `pytest`（または `python -m pytest`）を実行。ルートの `conftest.py` が `app` パッケージのパスと `brown` エイリアスを設定します。全部で**66件**パスします（実際に `python -m pytest` を実行し `66 passed` を確認済み。内訳は `tests/` の7+5+18+9+9+13+5=66関数）。

**Q17.** 2段階です。まず `count=100` はPydanticのField制約 `ge=1`（`app/series/schemas.py:18-20`）を満たすため入力バリデーションは通過します（上限側の制約はスキーマに無い）。次にサービス層で `generate_occurrences` が `max_count=52` の指定で呼ばれ、53件目を生成した時点で打ち切り（`app/series/recurrence.py:39-40`、上限+1件まで生成）、`RecurringReservationService.create_series` が `len(occurrences) > MAX_OCCURRENCES`（53>52）を検出して `ValidationError`→400を返します（`app/series/service.py:67-70`、BR-RS-C7）。つまり検出はサービス層の件数チェックで行われます。

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。モデルはナイーブ（tzinfoなし・ローカル）datetimeを前提とし（`app/db/models.py:1-8` のdocstring「時刻はナイーブ datetime（ローカル）」）、コード内にtimezone/astimezone/utc等の変換処理はありません。タイムゾーン対応は要件上スコープ外です（`requirements.md:69` NFR-5「タイムゾーン対応は対象外」）。

**Q19.** 作成できません。この機能は**週次のみ**をサポートしており、隔週・月次を指定するパラメータは存在しません。リクエストスキーマ `RecurringReservationCreate`（`app/series/schemas.py:11-23`）には間隔を指定するフィールドが無く、生成ロジックは7日固定刻みです（`app/series/recurrence.py:10` `WEEK = timedelta(days=7)`）。隔週・月次は明示的にスコープ外です（`requirements.md:69` NFR-5「隔週・月次などの複雑な繰り返し…は対象外」）。

**Q20.** 分かりません。このリポジトリには認証機構自体が存在せず、認証トークンやその有効期限を設定する箇所は見当たりません（`app/` 全体をgrepしても auth/token/jwt/bearer 等に該当なし）。認証・権限は要件上スコープ外と明記されています（`requirements.md:69` NFR-5「認証・権限…は対象外」）。したがって「トークン有効期限の設定場所」はリポジトリ上に存在しません。
