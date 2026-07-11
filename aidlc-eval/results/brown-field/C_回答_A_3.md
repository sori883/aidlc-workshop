十分な証拠が集まりました。回答をまとめます。

---

Q1. **重複した回だけスキップせず「1回でも重複したらシリーズ全体を409で拒否（原子性）」にした理由は、要件分析フェーズでユーザーが明示的にその方式を選択したためです。** brownfield-vision.md では「シリーズの一部が重複する場合、全体拒否かスキップ作成か」が Open Question として残されており（`brown-field/docs/writing-inputs/brownfield-vision.md`）、要件確認で「A) 全体拒否 — 原子性を優先 / B) スキップ作成」の二択が提示され、ユーザーは A（全体拒否）を選びました（`brown-field/aidlc-docs/inception/requirements/requirement-verification-questions.md` Q1、`brown-field/aidlc-docs/audit.md` の「Q1=全体拒否」）。これが FR-1.6／BR-RS-OV2 として確定し、`app/series/service.py:78-81`（1回でも `has_conflict` なら `ConflictError`）に実装されています。スキップ作成案は user story US-R08 として控えにはありますが未実装です（`brown-field/aidlc-docs/inception/user-stories/stories.md`）。

Q2. **52回は「週次で約1年分」に相当し、無限・過大なシリーズ生成を防いで1リクエストの処理量を有界にするためです。** 要件確認 Q4 で「最大52回=約1年」として上限案が提示・採用され（`requirement-verification-questions.md`、`audit.md` の「Q4=上限あり(52)」）、FR-1.5 として確定しています（`requirements.txt` ではなく `.../requirements/requirements.md:34`）。パフォーマンス面でも「上限（52回）により1リクエストの処理量が有界」「重複チェックは最大52回×会議室のactive予約走査」と根拠づけられています（`brown-field/aidlc-docs/construction/build-and-test/performance-test-instructions.md`、`.../nfr-requirements/nfr-requirements.md:26`）。定数は `app/series/service.py:22`（`MAX_OCCURRENCES = 52`）と `app/series/recurrence.py:18`。

Q3. **専用APIが無いのは、シリーズの各回が通常の `Reservation` として展開されており、既存の単発キャンセルAPIをそのまま流用できる＝新規コード不要と判断されたためです（BR-RS-I1）。** 個別回のキャンセルは既存の `POST /reservations/{reservation_id}/cancel`（冪等・404対応）で行います（`brown-field/aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md` の BR-RS-I1、`app/reservations/router.py:51-56`、`app/reservations/service.py:76-83`）。要件確認 Q7 で「既存キャンセルAPI流用」が選択されています（`audit.md`）。

Q4. **既存の重複判定 `overlaps` と同じ「純粋関数（Functional Core）／副作用は service（Imperative Shell）に隔離」という設計思想を踏襲し、DB非依存で単体テスト・Property-Based Testing を容易にするためです。** ソース冒頭コメントにも「副作用なし・DB非依存でテスト/PBTが容易。overlapsと同じ設計思想」と明記されています（`app/series/recurrence.py:1-5`）。設計段階でユーザーが「日付生成＝純粋関数モジュールに切出し」を選択し（`brown-field/aidlc-docs/inception/plans/application-design-plan.md`、`audit.md`）、NFR設計パターン P-3「純粋関数の分離（Functional Core/Imperative Shell）」として定式化されています（`.../nfr-design/nfr-design-patterns.md:14-16`、`.../requirements/requirements.md:67` NFR-3）。

Q5. **既存プロジェクトが `create_all()` によるテーブル自動作成方針で、Alemb* 等のマイグレーションツールを導入していないため、それに整合させて「新規依存を増やさない軽量な自動ALTERヘルパ（冪等）」が選ばれました。** `create_all` は未作成テーブルしか作らず既存テーブルへの列追加を行わないため、既存DBへ `series_id` を反映する保険として `_ensure_series_id_column` を用意しています（`app/db/database.py:36-62`）。設計判断は「決定: 軽量な自動ALTERヘルパ（冪等）／既存も SQLite 固定」として文書化され、SQLite前提（`PRAGMA table_info`／`ADD COLUMN`）である旨も記されています（`brown-field/aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md`）。技術スタックも「新規追加は hypothesis のみ」で、マイグレーションツールは追加していません（`.../nfr-requirements/tech-stack-decisions.md`）。

Q6. **hypothesis はProperty-Based Testing（PBT）フレームワークとして追加され、日付生成（純粋関数）・重複判定・スキーマのシリアライズ往復に適用されています。** 選定理由は「Python標準的・優れたshrinking・pytest統合」です（`requirements.txt:7`、`.../nfr-requirements/tech-stack-decisions.md:17`）。一部のテストにしか適用されていないのは、要件確認 Q13 でユーザーが拡張オプションを「Partial（部分適用）」と選択したためで、PBT-02（Round-trip）／03（Invariant）／07（Generator）／08（Shrinking/seed）／09（Framework）のみを強制し、純粋関数とシリアライズ往復に限定適用する方針が確定しています（`requirement-verification-questions.md` Q13、`audit.md` の「Q13 PBT=Partial」、`.../requirements/requirements.md:77`）。実装は `tests/test_recurring_pbt.py`（PBT 5件）に集約されています。

Q7. **共存できます。** 重複判定は半開区間 `[start, end)` で行い、`overlaps` は `start_a < end_b and start_b < end_a` を返します。「10:00終了」の予約（…–10:00）と「10:00開始」の予約（10:00–…）は隣接するだけで境界が重ならないため `10:00 < 10:00` が偽となり衝突しません（`app/availability/service.py:14-19`、README の「隣接はOK、重なりは409」`README.md:9`）。

Q8. **含まれます（inclusive）。** `until` は日付として扱われ、`generate_occurrences` は「`occ_start.date() > until` で打ち切り」なので、開始日が `until` と等しい回は生成対象に残ります。したがって 2030-01-15 に開始する回は含まれます（`app/series/recurrence.py:42-53`、スキーマ説明「この日以前の開始回まで、inclusive」`app/series/schemas.py:21-23`）。

Q9. **`count` と `until` を両方指定すると400（ValidationError）になります。両方省略しても400です。** 「ちょうど一方のみ」が要件（BR-RS-C4）で、service 側の `if (count is None) == (until is None): raise ValidationError` と、純粋関数側の同等チェックの二重で担保されています（`app/series/service.py:49-53`、`app/series/recurrence.py:28-29`）。

Q10. **作成できます。** 過去判定は「シリーズ最初の回の開始が現在より前」のときのみ拒否で、`if occurrences[0][0] < datetime.now()` と厳密な `<` を使っているため、`start_time == now`（同一時刻）は許可されます（`app/series/service.py:71-73`、BR-RS-C8「start == now は許可」）。単発予約も同方針です（`app/reservations/service.py:40-42`）。

Q11. (a) **過去に開始済みの回（`start_time <= 現在`）は変更されません。** (b) **既にキャンセル済みの回も変更されません。** キャンセル対象は `list_future_active_by_series` が返す「`start_time > now` かつ `status == active`」の回に限定されるためです（`app/series/service.py:130-141`、`app/reservations/repository.py:60-72`、BR-RS-X1/X2）。(c) **もう一度実行しても冪等で、状態は変わらず200を返します**（未来のactive回が無ければ `commit` もしない）（`app/series/service.py:135-141`、BR-RS-X3）。

Q12. **リクエスト契約（`ReservationCreate`）は不変ですが、レスポンス（`ReservationOut`）には任意項目 `series_id: str | None = None` が追加されました（後方互換の追加変更）。** 単発予約では `null`、シリーズの各回にはシリーズIDが入ります（`app/reservations/schemas.py:28-29`）。設計上はこの追加を「後方互換（既存の単発API契約・挙動は変わらない）」と位置づけています（BR-RS-D1/D2、`business-rules.md`、変更禁止事項 `brownfield-vision.md`）。厳密には出力スキーマにフィールドが1つ増えている点が唯一の差分です。

Q13. **いいえ、DBレベルの制約（ユニーク制約や排他制約）では実現されていません。** モデルにあるのはインデックス `ix_reservations_room_id_status` のみで、重複防止用のユニーク制約はありません（`app/db/models.py:112`）。防止は「対象会議室のactive予約をPythonで走査して `overlaps` 判定」というアプリ層のcheck-then-insertで行われます（`app/availability/service.py:28-46`、`app/reservations/service.py:43-58`）。そのため**同時並行リクエストが来た場合、チェックと挿入の間にレースが生じ二重予約は起こりえます**。Resiliency拡張は「No」で、並行制御は今回のスコープ外です（`audit.md` の「Q12 Resiliency=No」）。

Q14. **リポジトリルートの `conftest.py` が、このプロジェクトディレクトリを `brown` パッケージのエイリアスとして `sys.modules` に登録しているため動きます**（`_brown.__path__ = [_here]` により `brown.tests.conftest` が `tests/conftest.py` に解決される）（`conftest.py:19-24`）。この規約に合わせた理由は、リバースエンジニアリング時に既存テストが `from brown.tests.conftest import ...` という規約でインポートしている点が判明しており、「既存テストのソースを一切変更しない」という制約（変更禁止事項）を守りつつ規約を成立させるための追加設定だからです（`conftest.py:1-8`、`audit.md` の該当記述、`brownfield-vision.md` の変更禁止事項）。

Q15. **起動時に `create_all()` が走り、まず `_ensure_series_id_column` が既存 `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE ... ADD COLUMN series_id VARCHAR(36)` を実行し、続いて `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します**（`app/db/database.py:54-62`、`infrastructure-design.md`）。**2回起動しても冪等で、列は既存扱い・テーブルも既存扱いとなり、何も変更されません**（列存在チェックと create_all のスキップによる）。

Q16. **手順:** ①仮想環境を作成・有効化 `python -m venv .venv && source .venv/bin/activate`、②依存導入 `pip install -r requirements.txt`（hypothesis含む）、③ルートで `pytest` を実行（ルートの `conftest.py` が `brown` エイリアスと `app` のパス解決を行う）（`README.md:60-66`、`conftest.py`）。**パス件数は 66 件**です（既存回帰34＋新規例示27＋PBT 5）。実際に `pytest` を実行して `66 passed` を確認しました（`brown-field/aidlc-docs/construction/build-and-test/build-and-test-summary.md`、`audit.md`）。

Q17. **サービス層（`RecurringReservationService.create_series`）で検出され、400を返します。** 入力スキーマの `count` は `Field(None, ge=1, ...)` で下限のみ制約（上限 `le` は無し）なのでPydanticは `count=100` を通します（`app/series/schemas.py:18-20`）。次に `generate_occurrences` が「無制限生成を防ぐため最大 `max_count+1`（=53）件で打ち切って」返し、service が `if len(occurrences) > MAX_OCCURRENCES: raise ValidationError`（BR-RS-C7）で上限超過を判定して400にします（`app/series/recurrence.py:36-40`、`app/series/service.py:66-70`）。

Q18. **タイムゾーン変換はどのレイヤでも行われていません。** 時刻はナイーブ `datetime`（ローカル）として扱う設計で、タイムゾーン対応は明示的にスコープ外です（`app/db/models.py:1-8` の「時刻はナイーブdatetime（ローカル）」、`README.md:83` の「タイムゾーン」スコープ外、`brownfield-vision.md` Out of Scope）。

Q19. **指定できません。隔週・月次は今回のスコープ外で、対応するリクエストパラメータは存在しません。** 生成は週次固定（`WEEK = timedelta(days=7)`、7日刻み）で、`RecurringReservationCreate` にも間隔・頻度を指定する項目はありません（`app/series/recurrence.py:10`、`app/series/schemas.py:11-23`、README「隔週・月次などの複雑な繰り返し」はスコープ外 `README.md:83`、`brownfield-vision.md`）。

Q20. **分かりません（該当設定は存在しません）。** 本システムには認証機構そのものが実装されておらず（Security拡張は「No」＝`audit.md` の「Q11 Security=No」、README「認証・権限」はスコープ外）、設定ファイル `app/core/config.py` にもトークンや有効期限に関する項目はありません（`database_url`／`host`／`port` のみ）。したがって認証トークンの有効期限を設定する箇所はリポジトリ内に存在しません。
