調査が完了しました。以下、20問すべてに回答します。対象は `work/brown-field/cond-B`（現在の作業ディレクトリと同じ `cond-B` 条件の定期予約実装）です。

---

**Q1.** 「全体拒否（原子性）」を選んだのは、Vision の未確定事項（「全体拒否かスキップ作成か」）に対し、要件確定フェーズでユーザーが明示的に選択肢A（全体拒否）を選んだためです。2026-07-10 の対話で「Q1: 全体拒否（1回でも重複ならシリーズ全体を 409）」と回答が記録されています。設計上は「重複チェック→全回INSERTを単一トランザクションで実施しロールバック」という既存の予約作成パターン（原子性）を踏襲することを優先した結果です。実装は `app/series/service.py:78-81`（1回でも `has_conflict` なら `ConflictError`）。根拠: `aidlc-docs/inception/requirements/requirement-verification-questions.md:9,32-40`、`docs/writing-inputs/brownfield-vision.md`（In Scope / Open Questions）、`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md`（BR-RS-OV2）。

**Q2.** 「無限・過大なシリーズ作成を防ぐ上限」として設けられ、「52回＝約1年（週次）」という目安に基づきます。要件Q4で「上限を設ける（推奨。例: 最大52回=約1年。超過時は 400）」が選ばれています。根拠: `aidlc-docs/inception/requirements/requirement-verification-questions.md:12,73-79`、`app/series/service.py:22`（`MAX_OCCURRENCES = 52`）、`business-rules.md`（BR-RS-C7）。

**Q3.** シリーズの各回は「`series_id` を持つ通常の Reservation 行」に過ぎず、既存の単発キャンセルAPI `POST /reservations/{reservation_id}/cancel` がそのまま機能するため、専用APIを新設しない設計判断（新規ルール・新規コードなし）だからです。要件Q7で「個別回キャンセルは既存APIを流用」が確定しています。個別回のキャンセルは、その回の予約ID（`ReservationOut.id`）を使って既存の `POST /reservations/{reservation_id}/cancel` を呼び出して行います。根拠: `aidlc-docs/inception/requirements/requirements.md`（FR-3）、`business-rules.md`（BR-RS-I1）、`app/reservations/router.py:51-55`。

**Q4.** 既存の重複判定 `overlaps` 純粋関数と「同じ設計思想」で、副作用なし・DB非依存にして単体テストと Property-Based Testing を容易にするためです。ファイル冒頭のdocstringに「副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想。」と明記されています。NFR-3（テスト容易性: 日付生成・終了条件解決を純粋関数として切り出す）に対応します。根拠: `app/series/recurrence.py:1-5`、`aidlc-docs/inception/requirements/requirements.md`（NFR-3）、`aidlc-docs/.../functional-design/business-rules.md`（BR-RS-G*）。

**Q5.** 既存スタックが Alembic 等のマイグレーションツールを一切導入しておらず、スキーマ反映を `Base.metadata.create_all()` に依存する運用（ローカル実行 + SQLite、クラウド/コンテナ/IaC なし）だからです。ただし `create_all` は未作成テーブルしか作らず既存テーブルへの列追加はしないため、その隙間を埋める最小限・冪等な自動ALTERヘルパ（`_ensure_series_id_column`）を採用しました。設計文書に「軽量な自動 ALTER ヘルパ（冪等）」という決定として明記されています。根拠: `app/db/database.py:36-62`、`aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md:3-40`、`.../nfr-requirements/tech-stack-decisions.md`（マイグレーション方針）。

**Q6.** 目的は Property-Based Testing フレームワークとして日付生成・重複判定・シリアライズ往復に PBT を適用するためです（PBT-09準拠、Python標準的で shrinking と pytest 統合に優れるため Hypothesis を選定）。一部にしか適用されないのは、要件分析のオプトインでユーザーが「Partial（純粋関数とシリアライズ往復に限定適用）」を選んだためで、PBTは純粋関数 `generate_occurrences` とスキーマ往復（`tests/test_recurring_pbt.py`）にのみ適用されています。根拠: `requirements.md`（Extension Configuration: PBT Yes(Partial)）、`.../nfr-requirements/tech-stack-decisions.md`、`.aidlc-rule-details/extensions/testing/property-based/property-based-testing.opt-in.md`、`tests/test_recurring_pbt.py:1-5`。

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行われ、`overlaps` は `start_a < end_b and start_b < end_a` と厳密な不等号のため、「10:00終了」と「10:00開始」は隣接するだけで重ならない（`end_a == start_b`）扱いになります。根拠: `app/availability/service.py:14-19`、`business-rules.md`（BR-RS-OV1、隣接OK・重なりNG）。

**Q8.** 含まれます。`until` は「各回の開始日が until 以下（inclusive）」の回まで生成し、判定は `if occ_start.date() > until: break` と厳密な `>` のため、開始日が 2030-01-15 の回は `> until` にならず生成対象に含まれます。根拠: `app/series/recurrence.py:42-53`、`business-rules.md`（BR-RS-C6、inclusive）。

**Q9.** 両方指定すると 400（ValidationError「count または until のどちらか一方を指定してください」）になります。両方省略しても同じく 400 になります。サービス層で `(count is None) == (until is None)` が True の場合に弾いており、純粋関数側でも同条件で `ValueError` を投げます。根拠: `app/series/service.py:49-53`、`app/series/recurrence.py:28-29`、`business-rules.md`（BR-RS-C4）。

**Q10.** ルール上は許可されます（BR-RS-C8「start == now は許可」、判定は `occurrences[0][0] < datetime.now()` と厳密な `<`）。ただし実装上、比較に使う `datetime.now()` はリクエスト時点より後に評価されるため、厳密に「現在時刻ちょうど」の start_time は評価時点では過去（マイクロ秒差）となり実質的に拒否され得ます。設計意図としては「現在ちょうどは許可、厳密に過去のみ拒否」です。根拠: `app/series/service.py:71-73`、`business-rules.md`（BR-RS-C8）。

**Q11.** (a) 過去に開始済みの回（`start_time <= 現在`）は変更されません。(b) 既にキャンセル済みの回も変更されません。キャンセル対象は `list_future_active_by_series`（`start_time > now` かつ `status == active`）に限定されるためです。(c) もう一度実行しても、対象となる未来のactive回が無ければ状態を変えず 200 を返します（冪等）。根拠: `app/series/service.py:130-141`、`app/reservations/repository.py:60-71`、`business-rules.md`（BR-RS-X1/X2/X3）。

**Q12.** リクエスト契約に変更はありません。レスポンス契約は `ReservationOut` に `series_id`（`str | None`、単発は `null`）を1フィールド**追加**していますが、`ReservationCreate`（リクエスト）は不変です。既存テストはレスポンス全体一致ではなく個別フィールドを検証しているため後方互換を保っています（制約C-1を満たす）。根拠: `app/reservations/schemas.py:9-29`、`requirements.md`（FR-4.1、C-1、BR-RS-D2）。

**Q13.** いいえ、DBレベルの制約では実現されていません。`has_conflict` が対象会議室のactive予約を走査するアプリケーション層の判定で、`reservations(room_id, status)` のインデックスは重複防止の一意制約ではなく走査の高速化用です。並行リクエストが同時に来た場合、チェックとINSERTの間にロックや排他制約がないため二重予約は起こり得ます。根拠: `app/availability/service.py:28-46`、`app/db/models.py:111-112`（Indexはパフォーマンス用）。

**Q14.** ルートの `conftest.py` が、`brown` という名前のモジュールエイリアスを動的に登録し、その `__path__` を本プロジェクトディレクトリに向けているため、`brown.tests.conftest` が `tests/conftest.py` に解決されます（併せてワークスペースルートを `sys.path` に追加し `app` を import 可能にしています）。この規約に合わせた理由は、制約C-4「既存テストはすべてパスし続ける・既存テストの改変は不可」を満たすためで、既存テストが使う `from brown.tests.conftest import ...` を成立させる追加設定です。根拠: `conftest.py`（ルート、全文）、`requirements.md`（Existing System Context / C-4）。

**Q15.** 起動時に `create_all()` が走り、`_ensure_series_id_column` が既存 `reservations` テーブルに `series_id` 列が無いことを検出して `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を実行（既存行の `series_id` は NULL）、続く `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します。2回目の起動では、列もテーブルも既に存在するため何も起きません（冪等）。根拠: `app/db/database.py:36-62`、`infrastructure-design.md:38`（冪等）。

**Q16.** 手順: (1) `python -m venv .venv && source .venv/bin/activate`、(2) `pip install -r requirements.txt`（pytest・hypothesis を含む）、(3) プロジェクトルート（`brown-field/cond-B`）で `pytest` を実行。ルートの `conftest.py` が `brown` エイリアスと `sys.path` を設定するため、ルートから実行する必要があります。実行結果は **66件** パスします（実際に `.venv/bin/python -m pytest` で 66 passed を確認）。根拠: `README.md:16-23,63`、`conftest.py`、実行結果（66 passed）。

**Q17.** Pydanticスキーマは `count` に `ge=1` のみで上限がないため 100 は入力として通過します。純粋関数 `generate_occurrences` は無制限生成を防ぐため最大 `max_count + 1`（=53）件で打ち切り、その後サービス層 `create_series` が `if len(occurrences) > MAX_OCCURRENCES` を満たすと `ValidationError` を投げて 400 を返します。つまり検出は「サービス層の生成後の件数チェック」で行われます。根拠: `app/series/schemas.py:18-20`、`app/series/recurrence.py:36-40`、`app/series/service.py:66-70`。

**Q18.** タイムゾーンの変換はどのレイヤでも行われていません。モデルは「時刻はナイーブ datetime（ローカル）」で保存し、タイムゾーン対応は明示的にスコープ外（NFR-5）です。したがって「変換レイヤは存在しない」が答えです。根拠: `app/db/models.py:1-13`（ナイーブdatetime）、`requirements.md`（NFR-5 スコープ外）、`docs/writing-inputs/brownfield-vision.md`（Out of Scope: タイムゾーン対応）。

**Q19.** 分かりません。隔week・月次は明示的にスコープ外（Vision の Out of Scope / NFR-5）であり、実装は週次固定（`WEEK = timedelta(days=7)`、7日刻み固定）で、頻度・間隔を指定するリクエストパラメータは存在しません。現状のAPIでは隔週・月次の定期予約は作成できません。根拠: `app/series/recurrence.py:10,37,46`、`app/series/schemas.py:11-23`（間隔パラメータなし）、`docs/writing-inputs/brownfield-vision.md`（Out of Scope）。

**Q20.** 分かりません。このアプリケーションには認証機構自体が存在せず（認証・権限はスコープ外）、認証トークンやその有効期限を設定する箇所はコードベースに見当たりません。根拠: `docs/writing-inputs/brownfield-vision.md`（Out of Scope: 認証・権限）、`requirements.md`（NFR-5）、`app/core/config.py`（DB URL・host・port のみで認証設定なし）。
