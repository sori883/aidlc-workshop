調査完了しました。以下、20問すべてに回答します。

---

**Q1.** 「全体拒否（原子性優先）」が明示的に選択された経緯があります。元の Vision では「409で全体拒否か、スキップ作成かは要件分析で決定」と未確定事項（Open Question）として残されており（`docs/writing-inputs/brownfield-vision.md:18-19,34`）、要件確認質問 Question 1 で 3案（A:全体拒否 / B:スキップ作成 / C:リクエストで切替可能）が提示されました（`aidlc-docs/inception/requirements/requirement-verification-questions.md:31-42`）。2026-07-10の対話でユーザーが **A案（全体拒否）** を選択し、「原子性を優先」という理由が採用されました（同ファイル:9行目、`aidlc-docs/inception/requirements/requirements.md:35` FR-1.6、`business-rules.md:26` BR-RS-OV2）。つまり技術的必然ではなく、要件確認でユーザーが原子性を優先すると決めたためです。実装は `app/series/service.py:78-81` で1回でも重複したら `ConflictError`（409）を投げDBに一切登録しません。

**Q2.** 52回 ≈ 約1年（週次×52週）だからです。要件確認 Question 4 の推奨選択肢に「最大52回=約1年」と明記され（`requirement-verification-questions.md:77`）、ユーザーが上限ありを選択（同:12行目）。目的は「無限・過大なシリーズ作成の防止」です（同:74-77、`requirements.md:34` FR-1.5、`business-rules.md:14` BR-RS-C7）。定数は `app/series/service.py:22`（`MAX_OCCURRENCES = 52`）と `app/series/recurrence.py:18`（`max_count=52`）に定義されています。

**Q3.** シリーズ内の各回は通常の予約行（`series_id` を持つ `Reservation`）であり、既存の `POST /reservations/{reservation_id}/cancel` がそのまま機能するため、専用APIは不要と判断されたからです。要件確認 Question 7 で A案（既存APIを流用）が選択されました（`requirement-verification-questions.md:15,113-116`、`requirements.md:48-50` FR-3、`business-rules.md:44-45` BR-RS-I1「新規ルール・新規コードなし」）。個別回のキャンセルは、その回の `reservation_id` を使って既存の `POST /reservations/{reservation_id}/cancel`（`app/reservations/router.py:51-56`）を呼びます。

**Q4.** テスト容易性（PBT を含む単体テスト）のためです。既存の重複判定 `overlaps`（`app/availability/service.py:14-19`）と同じ「副作用なし・DB非依存の純粋関数」という設計思想を踏襲しており、日付生成ロジックをDBやトランザクションから切り離すことで単体テスト・Property-Based Testing を容易にする狙いです（`app/series/recurrence.py:1-5` のdocstring、`requirements.md:67` NFR-3、`nfr-requirements.md:22-24` NFR-RS-4）。実際 `tests/test_recurring_pbt.py` と `tests/test_recurrence.py` がこの純粋関数を直接検証しています。

**Q5.** 既存プロジェクトがマイグレーションツールを一切導入しておらず、起動時の `create_all()`（`Base.metadata.create_all`）だけでスキーマを用意する方式だったため、それを踏襲して依存追加を最小化したからです。`app/db/database.py:36-62` の `_ensure_series_id_column` が、既存 `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE ... ADD COLUMN` を冪等に実行します。インフラ設計でも「決定: 軽量な自動ALTERヘルパ（冪等）」「既存のローカル実行モデル（uvicorn + SQLite）を踏襲」と明記されています（`aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md:4,15-40`、`tech-stack-decisions.md:30-32`）。Alembic を明示的に比較検討・却下した記述は見つかりませんが、方針は「既存スタックの最大限継承・新規追加は最小限」です。

**Q6.** 目的は Property-Based Testing（PBT）フレームワークとしての利用で、`tests/test_recurring_pbt.py`（`from hypothesis import given, strategies`）で日付生成の不変条件・スキーマのシリアライズ往復・ドメイン生成器を検証しています。一部にしか適用されていないのは、要件確認 Question 13 でユーザーが **B（Partial）** を選び、「純粋関数とシリアライズ往復に限定適用」と決めたためです（`requirement-verification-questions.md:21,193-206`、`requirements.md:77`、`nfr-requirements.md:29-36` NFR-RS-6）。PBT-02/03/07/08/09 のみ強制対象で、CRUD的なAPI層は例示ベーステスト（`tests/test_recurring_api.py`）でカバーする方針です。

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行われ、`overlaps` は `start_a < end_b and start_b < end_a` を使うため、`end == start`（隣接）は重ならない扱いになります（`app/availability/service.py:14-19`）。「10:00終了」の予約の `end_time` と「10:00開始」の予約の `start_time` が一致するだけなので重複せず、両方作成できます（README:9、`business-rules.md:25` BR-RS-OV1）。

**Q8.** 含まれます。`until` は inclusive（開始日が `until` 以下の回まで）で判定され、`generate_occurrences` は `if occ_start.date() > until: break`（より大きい場合のみ打ち切り）としているため、開始日が 2030-01-15 ちょうどの回は生成対象に入ります（`app/series/recurrence.py:44-53`、`business-rules.md:13` BR-RS-C6、schemas の説明「この日以前の開始回まで、inclusive」`app/series/schemas.py:21-23`）。

**Q9.** どちらの場合も 400（ValidationError）です。`count` と `until` は「ちょうど一方のみ」指定が必須で、両方指定・両方省略はいずれも拒否されます。判定は `(count is None) == (until is None)` で行われ（`app/series/service.py:50-53` BR-RS-C4、`app/series/recurrence.py:28-29` は同条件で `ValueError`）、両方Trueでも両方Falseでもエラーになります（`requirements.md:31` FR-1.4）。

**Q10.** 作成できます。過去判定は「厳密に過去（`<`）」のみを拒否し、`start == now` は許可する仕様です。定期予約では `if occurrences[0][0] < datetime.now()` で最初の回のみを判定します（`app/series/service.py:71-73` BR-RS-C8）。単発予約も同様に `if start_time < datetime.now()`（`app/reservations/service.py:40-42` BR-C4）で、コメントにも「start == now は許可」と明記されています。

**Q11.** `cancel_series` は `list_future_active_by_series`（`start_time > now` かつ `status == active`）で対象を絞ります（`app/series/repository.py:60-72`、`app/series/service.py:130-141`）。
- **(a) 過去に開始済みの回**：`start_time > now` を満たさないため対象外。変更されず active のまま残ります（BR-RS-X2）。
- **(b) 既にキャンセル済みの回**：`status == active` を満たさないため対象外。cancelled のまま変わりません。
- **(c) もう一度実行**：未来の active 回が無ければ状態を変えず 200 を返す冪等な挙動です（`service.py:135-141`、BR-RS-X3）。

**Q12.** リクエスト契約は変更なし、レスポンスは後方互換の追加のみです。単発予約の入力 `ReservationCreate` は不変です（`app/reservations/schemas.py:9-14`、C-1）。出力 `ReservationOut` には `series_id: str | None = None`（既定 None）が追加されました（同:17-29、`requirements.md:53-55` FR-4.1、`code-summary.md:42-44` C-1）。Optionalフィールドの追加で、既存テストは個別フィールド検証のため壊れず、既存の等値契約は維持されるという整理です。

**Q13.** いいえ、DBレベルの制約（ユニーク制約や排他制約）では実現されていません。防止はアプリ層で「`has_conflict` で既存 active 予約を走査してから INSERT」という方式です（`app/availability/service.py:28-46`、`app/reservations/service.py:44-45`、`app/series/service.py:79-81`）。モデルにも重複防止の一意制約はなく、あるのは検索効率化用の `Index("ix_reservations_room_id_status", ...)` のみです（`app/db/models.py:111-112`）。したがって、チェックとINSERTの間にロック機構が無いため、並行リクエストが同時に来た場合は理論上二重予約が起こりえます（TOCTOUレース）。NFR上も高負荷・並行制御はスコープ外とされています（`nfr-requirements.md:25-27`）。

**Q14.** ルートの `conftest.py`（`/Users/const/sori883/aidlc-workshop/aidlc-eval/work/brown-field/cond-B/conftest.py`）が、`brown` という名前のモジュールを本プロジェクトディレクトリへのパッケージエイリアスとして `sys.modules` に登録しているためです（`conftest.py:21-25`、`__path__ = [_here]`）。これにより `brown.tests.conftest` が `tests/conftest.py` に解決され、`create_room` 等がインポートできます。この規約に合わせた理由は、既存テストが元々 `from brown.tests.conftest import ...` 形式で書かれており、変更禁止制約 C-4「既存テストは改変不可・全パス維持」を満たすため、既存テストを一切変えずにこの規約を成立させる追加設定を入れたからです（`conftest.py:3-8`、`requirements.md:16,22` C-4、`requirement-verification-questions.md:24-27`）。

**Q15.** 起動時の `create_all()` が2つの処理を冪等に実行します（`app/db/database.py:54-62`）。旧スキーマの `reservations.db` がある場合、まず `_ensure_series_id_column` が `reservations` に `series_id` 列を `ALTER TABLE ADD COLUMN` で追加し、次に `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します（既存 `reservations`/`rooms` は再作成されません）。2回目の起動では、`series_id` 列は既に存在するので追加はスキップ、テーブルも既存なので作成されず、何も起きません（冪等）。設計文書でも「複数回起動しても安全」と明記されています（`infrastructure-design.md:38`）。

**Q16.** 手順は、仮想環境を有効化して `pytest` を実行します（README:60-64）。
```bash
source .venv/bin/activate   # または python -m venv .venv で作成後
pip install -r requirements.txt
pytest
```
実際に実行した結果、**66件** がパスします（`66 passed`。テストファイル: `tests/test_overlaps.py`, `test_availability_api.py`, `test_rooms_api.py`, `test_reservations_api.py`, `test_recurrence.py`, `test_recurring_api.py`, `test_recurring_pbt.py`）。

**Q17.** スキーマ層ではなくサービス層で検出します。`RecurringReservationCreate` の `count` は `Field(ge=1)` で下限のみ制約し、上限はかけていません（`app/series/schemas.py:18-20`）。そのため count=100 は Pydantic を通過します。`generate_occurrences` は無制限生成を防ぐため最大 `max_count + 1`（=53）件で打ち切り（`app/series/recurrence.py:36-40`）、サービス層の `if len(occurrences) > MAX_OCCURRENCES:` で 53 > 52 を検出して `ValidationError`（400）を投げます（`app/series/service.py:66-70` BR-RS-C7）。つまり「生成を上限+1で打ち切り→件数で判定」という2段構えです。

**Q18.** どのレイヤでも変換していません。時刻はナイーブ `datetime`（ローカル）として保存・処理され、タイムゾーン対応は明示的にスコープ外です（`app/db/models.py:11-13` 冒頭コメント「時刻はナイーブ datetime（ローカル）」、`nfr-requirements.md:38`、`requirements.md:69` NFR-5、README:83、Vision の Out of Scope `brownfield-vision.md:26`）。

**Q19.** できません（該当パラメータは存在しません）。この機能は週次（7日刻み固定）のみをサポートし、隔週・月次などの複雑な繰り返しは明示的にスコープ外です（`app/series/recurrence.py:10` `WEEK = timedelta(days=7)`、README:82-83、`requirements.md:69` NFR-5、Vision `brownfield-vision.md:23`）。リクエストにも間隔を指定するパラメータはなく、指定できるのは `count` または `until` のみです（`app/series/schemas.py:11-23`）。

**Q20.** 設定箇所は存在しません。このシステムには認証機能自体が実装されておらず（認証・権限はスコープ外 — `requirements.md:69` NFR-5、README:83、Vision `brownfield-vision.md:24`）、設定 `app/core/config.py` にも `database_url`/`host`/`port` のみでトークン関連の項目はありません。したがって「認証トークンの有効期限」を設定する場所はリポジトリ内に存在しません。
