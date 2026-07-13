調査完了しました。以下、20問に回答します。

なお前提として、私の作業ディレクトリ（`green-field/cond-B`）には定期予約機能は存在せず、実装・設計ドキュメントはすべて同一リポジトリ内の `brown-field/` 配下にあります（コミット `878f9bd`）。以下の回答はその `brown-field/` の実装・ドキュメントを根拠にしています。

---

Q1. 「全体拒否（原子性優先）」は、要件確定時にユーザーへ選択肢A/B/Cを提示して合意した設計判断です。`requirement-verification-questions.md` の Question 1 で「A) 全体拒否」「B) スキップ作成」「C) パラメータで切替」が提示され、ユーザーが A を選択（2026-07-10 対話取得）しました。理由は原子性の優先で、シリーズを単一トランザクションで登録し、1回でも重複すれば series と全回を一切登録せずロールバックする方針です。
根拠: `brown-field/aidlc-docs/inception/requirements/requirement-verification-questions.md`（Question 1 と回答済みQ1）、`brown-field/aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md`（BR-RS-OV2）、`brown-field/app/series/service.py`

Q2. 「過大・無限なシリーズ作成を防ぐための上限」で、52回は「約1年（週次×52週）」を意図した推奨値です。Question 4 で「最大52回=約1年」として提示され承認されました。
根拠: `brown-field/aidlc-docs/inception/requirements/requirement-verification-questions.md`（Question 4）、`brown-field/aidlc-docs/inception/requirements/requirements.md`（FR-1.5）、`brown-field/app/series/service.py`（`MAX_OCCURRENCES = 52`）

Q3. 専用APIを設けなかったのは、シリーズの各回が通常の `Reservation` 行として展開されるため既存APIで個別キャンセルできるからです。Question 7 で「A) 既存 `POST /reservations/{reservation_id}/cancel` をそのまま使う」が選択されました。個別回のキャンセルは、対象回の予約ID を使い既存の `POST /reservations/{reservation_id}/cancel`（冪等・404仕様も既存踏襲）を呼び出して行います。新規コードはありません。
根拠: `brown-field/aidlc-docs/inception/requirements/requirement-verification-questions.md`（Question 7）、`brown-field/aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md`（BR-RS-I1）、`brown-field/app/reservations/service.py`（`cancel_reservation`）

Q4. 副作用なし・DB非依存でユニットテストと Property-Based Testing が容易になるためで、既存の `overlaps`（重複判定の純粋関数）と同じ設計思想を踏襲しています。ファイル冒頭のdocstringに「副作用なし・DB非依存でテスト/PBT が容易。overlaps と同じ設計思想」と明記されています。
根拠: `brown-field/app/series/recurrence.py`（docstring）、`brown-field/app/availability/service.py`（`overlaps`）

Q5. インフラが SQLite ローカル固定の軽量構成であり、Alembic 等の導入は過剰と判断したためです。既存の `create_all()` によるテーブル自動作成方針に整合させる形で、起動時に冪等な `_ensure_series_id_column`（`ALTER TABLE ... ADD COLUMN`）で列を補う方式を採用しています。既存テーブルへは `create_all` が列追加をしないため、この補助が必要でした。Q&Aでも「既存DBへのスキーマ反映=軽量な自動ALTERヘルパ」で合意されています。
根拠: `brown-field/aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md`、`brown-field/app/db/database.py`（`_ensure_series_id_column` / `create_all`）、`brown-field/aidlc-docs/aidlc-docs/audit.md`（該当なし→）`brown-field/aidlc-docs/audit.md`（「軽量な自動ALTERヘルパ」）

Q6. 目的は Property-Based Testing（PBT）フレームワークで、日付生成の純粋関数・スキーマのシリアライズ往復・不変条件を検証するためです（PBT-09準拠で選定）。一部にしか適用されていないのは、要件確定時に「Q13 Property-Based Testing: Partial（純粋関数とシリアライズ往復に限定適用）」とユーザーが選択したためで、DB非依存の `generate_occurrences` と `RecurringReservationCreate` スキーマに限定しています。
根拠: `brown-field/aidlc-docs/inception/requirements/requirement-verification-questions.md`（Q13）、`brown-field/aidlc-docs/construction/recurring-reservations/nfr-requirements/tech-stack-decisions.md`、`brown-field/tests/test_recurring_pbt.py`

Q7. 共存できます。重複判定は半開区間 `[start, end)` で行われ、`overlaps` は `start_a < end_b and start_b < end_a` で判定します。10:00終了の予約 `[..,10:00)` と 10:00開始の予約 `[10:00,..)` では `start_b(10:00) < end_a(10:00)` が偽になり重ならない扱い（隣接OK）となるためです。
根拠: `brown-field/app/availability/service.py`（`overlaps`）、`README.md`（隣接OK・重なりNG）

Q8. 含まれます。`until` は inclusive で、生成ループは `occ_start.date() > until` で打ち切るため、開始日がちょうど 2030-01-15 の回は `> until` が偽となり生成対象に残ります。
根拠: `brown-field/app/series/recurrence.py`（`if occ_start.date() > until: break`）、`brown-field/aidlc-docs/.../business-rules.md`（BR-RS-C6）

Q9. 両方指定すると 400（`count または until のどちらか一方を指定してください。`）になります。両方省略しても同じく 400 です。`(count is None) == (until is None)` が真（両方指定＝両方None のどちらも）になる場合に `ValidationError` を投げる実装です。
根拠: `brown-field/app/series/service.py`（`create_series` の BR-RS-C4 チェック）、`brown-field/app/series/recurrence.py`（同ガード）

Q10. 作成できます。過去日時チェックは `occurrences[0][0] < datetime.now()`（厳密な `<`）で、開始時刻が現在とちょうど同じ場合は「過去」に該当せず許可されます（単発の BR-C4 と一貫）。
根拠: `brown-field/app/series/service.py`（BR-RS-C8）、`brown-field/aidlc-docs/.../business-rules.md`（BR-RS-C8「start == now は許可」）

Q11. (a) 過去に開始済みの回（`start_time <= 現在`）は変更されません。キャンセル対象は `list_future_active_by_series` が返す「開始時刻が現在より後の active 回のみ」です。(b) 既にキャンセル済みの回も対象外で変更されません（active のみ抽出）。(c) もう一度実行しても、対象となる未来の active 回が残っていなければ状態を変えず 200 を返す冪等動作です。
根拠: `brown-field/app/series/service.py`（`cancel_series`）、`brown-field/app/reservations/repository.py`（`list_future_active_by_series`）、`brown-field/aidlc-docs/.../business-rules.md`（BR-RS-X1〜X3）

Q12. 変更はありません。リクエストの `ReservationCreate` は不変で、レスポンスの `ReservationOut` に `series_id`（`str | None`、既定 `None`、単発予約は null）という任意フィールドを追加しただけの後方互換変更です（制約C-1、BR-RS-D2）。既存テストも未改変です。
根拠: `brown-field/app/reservations/schemas.py`、`brown-field/aidlc-docs/.../code/code-summary.md`（制約C-1）、`brown-field/aidlc-docs/.../business-rules.md`（BR-RS-D2）

Q13. いいえ、DBレベルの制約（ユニーク制約や排他制約）では実現されていません。`AvailabilityService.has_conflict` が対象会議室の active 予約をアプリ層で走査して判定する方式です。したがって、チェックと挿入の間にコミットされる並行リクエストがあれば二重予約は起こりえます（TOCTOU）。単一 `commit` でロールバックはできますが、DB制約による排他はありません。
根拠: `brown-field/app/availability/service.py`（`has_conflict`）、`brown-field/app/db/models.py`（インデックスのみで unique 制約なし）、`brown-field/app/series/service.py`

Q14. リポジトリルート（`brown-field/conftest.py`）が pytest 起動時に `brown` という名前を本ディレクトリへのパッケージエイリアスとして `sys.modules` に登録し、`brown.tests.conftest` を `tests/conftest.py` に解決させているため動きます。この規約に合わせた理由は、「既存テストのソースを一切変更しない（制約C-4）」ためで、既存テストが使っていた `from brown.tests.conftest import ...` を成立させる追加設定のみを入れたからです。
根拠: `brown-field/conftest.py`、`brown-field/tests/test_recurring_api.py`（`from brown.tests.conftest import create_room`）、`brown-field/aidlc-docs/.../code/code-summary.md`（制約C-4）

Q15. 起動時の `create_all()` が、既存 `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を実行し、さらに未作成の `reservation_series` テーブルを新規作成します。既存の予約データは保持されます。2回目の起動では、列の存在チェック（`inspect`）とテーブル未作成チェックにより何もせず（冪等）、二重追加は起きません。audit にも既存DBコピーでの検証OKと記録があります。
根拠: `brown-field/app/db/database.py`（`_ensure_series_id_column` / `create_all`）、`brown-field/aidlc-docs/.../infrastructure-design/infrastructure-design.md`、`brown-field/aidlc-docs/audit.md`

Q16. 手順: `brown-field/` ディレクトリで、`python -m venv .venv && source .venv/bin/activate`、`pip install -r requirements.txt`（`hypothesis` を含む）、そのディレクトリで `pytest` を実行します（ルートの `conftest.py` が `app` パッケージ解決と `brown` エイリアスを設定するため、ルートからの実行が前提）。パス件数は 66 件（既存回帰34 + 新規例示27 + PBT 5）です（test関数数の合計 5+7+13+9+9+18+5=66 とも一致）。
根拠: `brown-field/requirements.txt`、`brown-field/conftest.py`、`brown-field/aidlc-docs/audit.md`（「66 passed（既存回帰34 + 新規例示27 + PBT 5）」）、`brown-field/tests/`

Q17. まず Pydantic で `count: int | None = Field(None, ge=1)` を通過します（100は有効）。次に `generate_occurrences` が呼ばれ、`max_count=52` を超えると最大 `max_count + 1`（=53件）まで生成して打ち切ります（無制限生成を防ぐため）。その後 `RecurringReservationService.create_series` が `len(occurrences) > MAX_OCCURRENCES`（BR-RS-C7）で 400（`ValidationError`）を返して上限超過を検出します。つまり最終的な超過検出はサービス層です。
根拠: `brown-field/app/series/recurrence.py`、`brown-field/app/series/service.py`（BR-RS-C7）、`brown-field/app/series/schemas.py`

Q18. タイムゾーン変換はどのレイヤでも行われていません。日時はナイーブ `datetime`（ローカル）として扱い、タイムゾーン対応はスコープ外（NFR-5）と定義されています。
根拠: `brown-field/app/db/models.py`（「時刻はナイーブ datetime（ローカル）」）、`brown-field/aidlc-docs/inception/requirements/requirements.md`（NFR-5 スコープ外）

Q19. 隔週・月次を作成する方法はありません。本機能は週次（7日刻み）固定で、隔週・月次などの複雑な繰り返しはスコープ外（NFR-5）です。リクエストで指定できる繰り返しパラメータは終了条件の `count` または `until` のみで、間隔を指定するパラメータは存在しません。
根拠: `brown-field/app/series/recurrence.py`（`WEEK = timedelta(days=7)` 固定）、`brown-field/app/series/schemas.py`（`RecurringReservationCreate`）、`brown-field/aidlc-docs/inception/requirements/requirements.md`（NFR-5）

Q20. 分かりません（該当なし）。このシステムには認証機構が実装されておらず、認証トークンやその有効期限を設定する箇所は存在しません。認証・権限はスコープ外（NFR-5、Q11 Security=No）と明記されています。
根拠: `brown-field/aidlc-docs/inception/requirements/requirements.md`（NFR-5「認証・権限…は対象外」）、`brown-field/aidlc-docs/inception/requirements/requirement-verification-questions.md`（Q11 Security: No）、`brown-field/app/`（認証関連コードなし）
