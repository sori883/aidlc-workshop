調査が完了しました。以下、20問すべてに回答します。

---

**Q1.** 「全体拒否（1回でも重複ならシリーズ全体を409）」は、Vision段階で「全体拒否かスキップ作成か」が未確定事項として明示され、要件確定の質問(Question 1)でユーザーが選択肢A「全体拒否 — 原子性を優先」を選んだためです（2026-07-10に対話形式で回答取得）。スキップ作成(選択肢B)も提示されていましたが採用されませんでした。設計上は「原子性（全成功または全ロールバック）」を優先し、重複チェック→全回INSERTを単一トランザクションで実施する方針として実装されています。
根拠: `docs/writing-inputs/brownfield-vision.md:17-19,34`, `aidlc-docs/inception/requirements/requirement-verification-questions.md:9,31-42`, `aidlc-docs/inception/requirements/requirements.md:35(FR-1.6),66(NFR-2)`, `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:26(BR-RS-OV2)`, `app/series/service.py:78-81`

**Q2.** 52回は「約1年（週次×52週=約1年）」に相当する上限で、無限・過大なシリーズ作成を防ぐためです。要件確定の質問(Question 4)で「上限を設ける（推奨。例: 最大52回=約1年。超過時は400）」が選ばれた結果です。
根拠: `aidlc-docs/inception/requirements/requirement-verification-questions.md:12,74-83`, `aidlc-docs/inception/requirements/requirements.md:34(FR-1.5)`, `app/series/service.py:22`

**Q3.** シリーズ内の各回は`series_id`を持つ通常の`Reservation`行であり、既存の単発予約用キャンセルAPI `POST /reservations/{reservation_id}/cancel` がそのまま機能するためです。要件確定の質問(Question 7)で「既存APIを流用する（新規APIを作らない）」が選ばれました。個別回のキャンセルは、その回の予約ID(`reservation_id`)を使って既存の `POST /reservations/{id}/cancel` を呼ぶことで行います。
根拠: `aidlc-docs/inception/requirements/requirements.md:48-50(FR-3)`, `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:43-45(BR-RS-I1)`, `aidlc-docs/inception/requirements/requirement-verification-questions.md:113-122`

**Q4.** テスト容易性(NFR-3)のためです。既存の重複判定 `overlaps` が純粋関数として切り出されている設計思想を踏襲し、日付生成・終了条件解決を副作用なし・DB非依存の純粋関数にすることで、単体テストおよびProperty-Based Testing(PBT)を容易にする目的です。ファイル冒頭のdocstringにも「副作用なし・DB非依存でテスト/PBTが容易。overlapsと同じ設計思想」と明記されています。
根拠: `app/series/recurrence.py:1-5`, `aidlc-docs/inception/requirements/requirements.md:67(NFR-3)`, `app/availability/service.py:14-19`

**Q5.** インフラ設計で「既存のローカル実行モデル(uvicorn + SQLite)を踏襲し、クラウド・コンテナ・IaCは導入しない」方針が採られ、既存の `create_all()` によるテーブル作成方針(create_all)に整合させるためです。Alembic等の重量なマイグレーションツールは導入せず、起動時に冪等に動く軽量な自動ALTERヘルパ(`_ensure_series_id_column`)を選択しました。SQLite限定(`PRAGMA table_info` / `ADD COLUMN`)を前提とし、既存ファイルDBへの「保険」として位置づけられています。
根拠: `aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md:3-4,15-41`, `aidlc-docs/inception/requirements/requirements.md:61(FR-5.3)`, `app/db/database.py:36-62`

**Q6.** hypothesis はProperty-Based Testing(PBT)フレームワークとして追加されました(PBT-09準拠。Python標準的で優れたshrinking・pytest統合が根拠)。一部にしか適用されていないのは、要件確定の質問(Question 13)でユーザーが「Partial — 純粋関数とシリアライズ往復に限定適用」を選んだためです。結果として、日付生成(`generate_occurrences`)とスキーマのシリアライズ往復のみにPBTが適用され(PBT-02/03/07/08)、DB統合層などには適用されていません。
根拠: `requirements.txt:7`, `aidlc-docs/construction/recurring-reservations/nfr-requirements/tech-stack-decisions.md:17,34-38`, `aidlc-docs/inception/requirements/requirements.md:77`, `aidlc-docs/inception/requirements/requirement-verification-questions.md:21,193-206`, `tests/test_recurring_pbt.py:1-14`

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行われ、隣接（`end_a == start_b`）は重ならない扱いだからです。`overlaps` は `start_a < end_b and start_b < end_a` を返すため、「10:00終了」の予約(end=10:00)と「10:00開始」の予約(start=10:00)では `10:00 < 10:00` が偽となり、重複しません。
根拠: `app/availability/service.py:14-19`

**Q8.** 含まれます。`until` は「各回の開始日が until 以下(inclusive)の回まで」生成する仕様で、`occ_start.date() > until` で初めて打ち切るため、開始日が until と等しい2030-01-15の回は生成対象に含まれます。
根拠: `app/series/recurrence.py:42-53`, `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:13(BR-RS-C6)`

**Q9.** 両方指定すると400（ValidationError）になります。`(count is None) == (until is None)` の判定で、両方指定・両方未指定はいずれもエラーとなり、「count または until のどちらか一方を指定してください。」を返します。両方省略した場合も同じ判定で400になります。
根拠: `app/series/service.py:49-53`, `app/series/recurrence.py:28-29`, `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:11(BR-RS-C4)`

**Q10.** 作成できます。過去日時チェックは `occurrences[0][0] < datetime.now()`（厳密な「より前」）であり、start == now は含まれないため許可されます。ビジネスルールにも「start == now は許可」と明記されています。
根拠: `app/series/service.py:71-73`, `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:15(BR-RS-C8)`

**Q11.** (a) 過去に開始済みの回(`start_time <= now`)は変更されません。キャンセル対象は `list_future_active_by_series` が返す「`start_time > now` の active 回」のみだからです。(b) 既にcancelled済みの回も、`status == active` の条件に該当しないため変更されません。(c) もう一度実行すると、対象となる未来のactive回が無いため状態を変えず、200を返します（冪等）。
根拠: `app/series/service.py:130-141`, `app/reservations/repository.py:60-72`, `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:37-41(BR-RS-X1/X2/X3)`

**Q12.** リクエスト契約に変更はありません。レスポンスは `ReservationOut` に `series_id`（`str | None`、単発予約は null）フィールドが追加されました。`ReservationCreate`（リクエスト）は不変です。既存テストは等値比較ではなく個別フィールド検証のため、このフィールド追加は互換性を壊さない（C-1/C-4を満たす）と整理されています。
根拠: `app/reservations/schemas.py:9-14(不変),17-29(series_id追加)`, `aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md:49-50(BR-RS-D1/D2)`, `aidlc-docs/inception/requirements/requirements.md:53-54(FR-4.1)`

**Q13.** DBレベルの制約では実現されていません。`has_conflict` によるアプリケーション層でのループ走査（対象会議室のactive予約を取得し `overlaps` で判定）で実現されています。一意制約や排他ロックは無く、インフラ設計でも「FK制約はSQLiteのADD COLUMNで厳密に付与できないため、アプリ層で整合を担保」とされています。したがって、並行リクエストが同時にチェックを通過すると二重予約は起こりえます（チェックと書き込みの間に排他制御がない）。
根拠: `app/availability/service.py:28-46`, `app/db/models.py:111-112`（インデックスのみ、unique制約なし）, `aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md:39`

**Q14.** ルートの `conftest.py` が、本プロジェクトディレクトリを `brown` パッケージとして `sys.modules` にエイリアス登録しているため動きます。`types.ModuleType("brown")` を生成し `__path__` を本ディレクトリに設定することで、`brown.tests.conftest` が `tests/conftest.py` に解決されます。この規約に合わせた理由は、既存テストが `from brown.tests.conftest import ...` 形式でインポートしており（既存の制約）、既存テストのソースを一切変更せずに(C-4)成立させるためです。
根拠: `conftest.py:1-24`, `aidlc-docs/inception/requirements/requirements.md:16(制約),24(C-4)`

**Q15.** 起動時に `create_all()` が実行され、(1) 新テーブル `reservation_series` が `Base.metadata.create_all` で作成され、(2) 既存の `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` で追加されます（既存データは保持）。2回目の起動では、`reservation_series` は既存のためスキップされ、`series_id` 列も既に存在するため列追加もスキップされます（冪等）。
根拠: `app/db/database.py:36-62`, `aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md:15-41`

**Q16.** リポジトリルートで `python3 -m pytest`（`python3 -m pytest -q`）を実行します。依存として `requirements.txt`（fastapi, sqlalchemy, pydantic, pytest, httpx, hypothesis 等）が必要です。実際に実行したところ **66件すべてがパス**しました（`66 passed`）。ルートの `conftest.py` が `app` のimportと `brown` エイリアスを設定するため、追加設定は不要です。
根拠: 実行結果 `66 passed`, `conftest.py:1-24`, `requirements.txt`, `aidlc-docs/construction/build-and-test/unit-test-instructions.md`（テスト手順）

**Q17.** サービス層で検出されます。`generate_occurrences` は無制限生成を防ぐため最大 `max_count + 1`（=53件）まで生成して打ち切り、その後 `RecurringReservationService.create_series` が `len(occurrences) > MAX_OCCURRENCES`（52）で判定してValidationError（400）を送出します。count=100 の場合、Pydanticの `ge=1` は通過し（上限は制約されていない）、53件生成された時点で打ち切られ、サービス層の件数チェックで上限超過を検出して400になります。
根拠: `app/series/recurrence.py:36-40,51-52`, `app/series/service.py:57-70`, `app/series/schemas.py:18-20`

**Q18.** タイムゾーンの変換はどのレイヤでも行われていません。時刻はナイーブ datetime（ローカル）として扱われ、タイムゾーン対応はスコープ外(NFR-5)です。
根拠: `app/db/models.py:1-4`（「時刻はナイーブ datetime(ローカル)」）, `aidlc-docs/inception/requirements/requirements.md:69(NFR-5)`, `docs/writing-inputs/brownfield-vision.md:25`

**Q19.** 作成できません。この機能は週次(7日刻み)固定であり、隔週・月次などの複雑な繰り返しはスコープ外(NFR-5/Out of Scope)です。そのようなパラメータ（間隔指定など）はリクエストスキーマ `RecurringReservationCreate` に存在せず、生成ロジックも `WEEK = timedelta(days=7)` の固定刻みです。したがって指定する手段はありません。
根拠: `app/series/schemas.py:11-23`, `app/series/recurrence.py:10,37`, `aidlc-docs/inception/requirements/requirements.md:69(NFR-5)`, `docs/writing-inputs/brownfield-vision.md:23`

**Q20.** 分かりません。このリポジトリには認証トークンの仕組みが存在しません。認証・権限はスコープ外(NFR-5)で、設定(`app/core/config.py`)にもトークン有効期限に相当する設定はありません（DBURL・host・portのみ）。設計文書でも認証は「N/A（Security拡張無効、スコープ外）」とされています。
根拠: `app/core/config.py:1-17`, `aidlc-docs/inception/requirements/requirements.md:69(NFR-5)`, `aidlc-docs/construction/recurring-reservations/nfr-design/nfr-design-patterns.md:45`
