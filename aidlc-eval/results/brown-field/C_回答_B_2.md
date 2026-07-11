調査が完了しました。全20問に回答します。

---

**Q1. 「重複した回だけスキップ」にしなかった理由・経緯**
これは実装上の都合ではなく、要件確定時にユーザーが明示的に選択した仕様です。要件確認質問 Question 1 で「A) 全体拒否（原子性を優先）」「B) スキップ作成」「C) 呼び出し側が選択」の3択が提示され、ユーザーは **A（全体拒否）** を選びました。理由は「部分的に歯抜けのシリーズが登録されず、ダブルブッキングも起きない」ことを優先したためです。この決定に沿って FR-1.6／US-R02／BR-RS-OV2 として文書化され、`service.py` で1回でも重複したら `ConflictError`（409）を投げて何も登録しない実装になっています。
根拠: `aidlc-docs/inception/requirements/requirement-verification-questions.md`（Q1）、`aidlc-docs/audit.md:45`（Q1=全体拒否）、`aidlc-docs/inception/requirements/requirements.md`（FR-1.6）、`aidlc-docs/inception/user-stories/stories.md`（US-R02）、`app/series/service.py:78-81`

**Q2. シリーズ上限が52回である理由**
「52回 = 約1年（週次×52週）」という業務的な目安であり、無限・過大なシリーズ作成を防ぐためです。要件確認質問 Question 4 の推奨選択肢に「例: 最大52回=約1年。超過時は 400」と記載され、これが採用されています。
根拠: `aidlc-docs/inception/requirements/requirement-verification-questions.md:77`、`aidlc-docs/inception/requirements/requirements.md:34`（FR-1.5）

**Q3. 個別回キャンセル専用APIが無い理由／個別回のキャンセル方法**
シリーズの各回は通常の `Reservation` 行として展開され `series_id` で紐付くだけなので、既存の単発キャンセルAPIをそのまま使えるからです。要件確認質問 Question 7 で「A) 既存 `POST /reservations/{reservation_id}/cancel` を流用（新規ルール・新規コードなし）」が選択されました（BR-RS-I1）。個別回のキャンセルは、対象回の `reservation_id`（シリーズ照会 `GET /reservations/recurring/{series_id}` の `occurrences` から取得可能）に対して `POST /reservations/{reservation_id}/cancel` を呼び出して行います。
根拠: `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:44-45`、`aidlc-docs/inception/requirements/requirement-verification-questions.md:113-116`、`app/reservations/service.py:76-83`

**Q4. 週次生成ロジックが純粋関数として分離されている理由**
副作用なし・DB非依存にすることでテストとProperty-Based Testingが容易になるためです。ファイル冒頭のdocstringに「副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想」と明記されており、既存の重複判定 `overlaps` と同じ設計思想を踏襲しています。NFR設計でも「P-3: 純粋関数分離」パターンとして位置づけられています。
根拠: `app/series/recurrence.py:1-5`、`aidlc-docs/construction/recurring-reservations/nfr-design/nfr-design-patterns.md`（P-3）

**Q5. マイグレーションツールではなくSQL直書きヘルパで列追加している理由**
「既存のローカル実行モデル（uvicorn + SQLite）を踏襲し、新規追加は最小限」という方針のためです。インフラ設計で、追加インフラ・IaC・マイグレーションツールを導入せず、既存の `create_all()` を拡張した「軽量な自動ALTERヘルパ（冪等）」を採用すると決定されています。SQLite固定・小規模・依存最小の前提です。
根拠: `aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md:15-41`、`aidlc-docs/construction/recurring-reservations/nfr-requirements/tech-stack-decisions.md:4,30-32`、`app/db/database.py:36-62`

**Q6. hypothesis の目的／PBTが一部にしか適用されない理由**
目的はProperty-Based Testing（PBT）フレームワークとしての導入で、優れたshrinking・pytest統合・Python標準的であることが選定理由です。一部にしか適用されないのは、要件確認質問 Question 13 でユーザーが「B) Partial — 純粋関数とシリアライズ往復に限定適用」を選んだためです。実際、PBTは純粋関数 `generate_occurrences` とスキーマの往復 `RecurringReservationCreate` にのみ適用されています（DB・API層には非適用）。
根拠: `aidlc-docs/construction/recurring-reservations/nfr-requirements/tech-stack-decisions.md:17`、`aidlc-docs/inception/requirements/requirement-verification-questions.md:193-202`、`aidlc-docs/audit.md:45`（Q13 PBT=Partial）、`tests/test_recurring_pbt.py`

**Q7. 「10:00終了の予約」と「10:00開始の予約」は共存できるか**
共存できます。重複判定は半開区間 `[start, end)` で行われ、`overlaps` は `start_a < end_b and start_b < end_a` で判定します。終了=10:00、開始=10:00の場合 `10:00 < 10:00` が偽になり重ならない扱い（隣接OK）になるためです。
根拠: `app/availability/service.py:14-19`、`README.md:9`

**Q8. until=2030-01-15 のとき、2030-01-15開始の回は含まれるか**
含まれます（inclusive）。生成ループは `occ_start.date() > until` で打ち切るため、開始日が until と等しい回は生成対象に残ります。
根拠: `app/series/recurrence.py:41-53`、`app/series/schemas.py:21-23`

**Q9. count と until を両方指定／両方省略した場合**
どちらも 400（ValidationError）になります。サービス層で `(count is None) == (until is None)` が真（両方指定または両方省略）なら「count または until のどちらか一方を指定してください」というエラーを投げます（BR-RS-C4）。純粋関数側でも同条件で `ValueError` を投げる二重防御になっています。
根拠: `app/series/service.py:50-53`、`app/series/recurrence.py:28-29`

**Q10. start_time が現在時刻とちょうど同じ予約は作成できるか**
作成できます。判定は `occurrences[0][0] < datetime.now()` で「過去（より前）」のみ拒否し、`start == now` は許可される設計です（BR-RS-C8、単発予約の BR-C4 と一貫）。
根拠: `app/series/service.py:71-73`、`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:15`

**Q11. シリーズ全体キャンセル実行時の挙動**
(a) 過去に開始済みの回（`start_time <= now`）は変更されません。対象は `start_time > now` の active 回のみです。(b) 既にキャンセル済みの回も変更されません（active のみが対象）。(c) 同じキャンセルを再実行しても、対象となる未来のactive回が無ければ状態を変えず 200 を返します（冪等）。
根拠: `app/series/service.py:130-141`、`app/reservations/repository.py:60-72`、`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:37-41`（BR-RS-X1〜X3）

**Q12. 既存の単発予約APIの契約変更の有無**
リクエスト契約（`ReservationCreate`）は変更されていません。レスポンス（`ReservationOut`）には後方互換の追加として `series_id`（単発は `null`、デフォルト `None`）が1フィールド増えただけです。これはユーザーが Question 9 で「A) `ReservationOut` に `series_id` を追加」を選んだ結果で、BR-RS-D2で「既存の単発予約APIの契約・挙動は変わらない」と担保されています。
根拠: `app/reservations/schemas.py:9-29`、`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:49-50`

**Q13. ダブルブッキング防止はDB制約か／並行時に二重予約は起こりうるか**
DBレベルの制約ではありません。`reservations` にあるのは非ユニークな `Index("ix_reservations_room_id_status", ...)` のみで、ユニーク制約や排他ロックはありません。防止はアプリ層の `has_conflict`（active予約を走査してPython側で重なり判定）で行われます。したがって「重複チェック→INSERT」の間にロックが無いため、並行リクエストが同時に来た場合は二重予約が起こりえます（check-then-insertの競合）。
根拠: `app/db/models.py:111-112`、`app/availability/service.py:28-46`、`app/series/service.py:79-120`

**Q14. `brown` パッケージが無いのにテストが動く理由／この規約に合わせた理由**
ルートの `conftest.py` が、`brown` という名前のモジュールエイリアスを本ディレクトリに割り当てて `sys.modules` に登録しているためです。これにより `brown.tests.conftest` が `tests/conftest.py` に解決されます。規約に合わせた理由は、既存テストが `from brown.tests.conftest import ...` という規約でヘルパを取得しており、「既存テストのソースは一切変更せず、この規約を成立させるための追加設定」として conftest 側で吸収したためです。
根拠: `conftest.py:1-24`、`tests/conftest.py:55-67`

**Q15. 旧スキーマの reservations.db がある環境で新バージョンを起動すると／2回起動すると**
起動時に `create_all()` が実行され、まず `reservation_series` テーブルが新規作成され、`_ensure_series_id_column` が `reservations` に `series_id` 列が無いことを検出して `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を実行します。2回目の起動では、列がすでに存在するため何もしません（冪等）。既存データは保持されます。
根拠: `app/db/database.py:36-62`、`aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md:37-41`

**Q16. テスト実行手順／パスするはずの件数**
リポジトリルートで `pytest`（本環境では `.venv/bin/python -m pytest`）を実行します。ルート `conftest.py` が `app` の import と `brown` エイリアスを設定するため追加設定は不要です。実際に実行したところ **66件パス**しました（`66 passed`）。
根拠: `README.md:60-64`、実行結果 `66 passed`、各テストファイル（test_availability_api 5, test_overlaps 7, test_recurrence 9, test_recurring_api 18, test_recurring_pbt 5, test_reservations_api 13, test_rooms_api 9 = 66）

**Q17. count=100 を指定した場合の上限超過検出**
スキーマ `RecurringReservationCreate` の `count` は `ge=1` のみで上限がないため、100 は Pydantic を通過します。検出はサービス層で行われます。純粋関数 `generate_occurrences` は上限超過時も呼び出し側が件数で検出できるよう、最大 `max_count+1`（=53件）まで生成して打ち切ります。その後サービス層の BR-RS-C7 チェック `len(occurrences) > MAX_OCCURRENCES`（53 > 52）が真になり、400（ValidationError「繰り返し回数が上限（52回）を超えています」）を返します。
根拠: `app/series/schemas.py:18-20`、`app/series/recurrence.py:36-40`、`app/series/service.py:67-70`

**Q18. タイムゾーン変換を行うレイヤ**
どのレイヤでもタイムゾーン変換は行っていません。時刻はナイーブ（naive）な `datetime`（ローカル）として扱われ、タイムゾーンはスコープ外と明記されています。
根拠: `app/db/models.py:11-13`（「時刻はナイーブ datetime（ローカル）」）、`README.md:83`（タイムゾーンはスコープ外）

**Q19. 隔週・月次の定期予約を作成するためのパラメータ**
指定できません。本機能は週次（7日固定刻み）のみで、隔週・月次を指定するパラメータは存在しません。`generate_occurrences` は `WEEK = timedelta(days=7)` 固定で、隔週・月次はスコープ外と明記されています。
根拠: `app/series/recurrence.py:10,37,47`、`app/series/schemas.py:11-23`（該当パラメータなし）、`README.md:83`

**Q20. APIの認証トークンの有効期限の設定場所**
認証機能自体が存在しないため、トークンの有効期限設定もありません。Security拡張は無効（Question 11=No）で、認証・権限はスコープ外です。コードベース全体を検索しても token/auth/jwt 等の実装はありません。
根拠: `app/` 配下に認証関連コードなし（grep で該当0件）、`README.md:83`（認証・権限はスコープ外）、`aidlc-docs/inception/requirements/requirement-verification-questions.md:165-174`（Q11 Security=No）
