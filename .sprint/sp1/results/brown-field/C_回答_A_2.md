すべて確認できました。66件のテストが通ります。以下、20問に回答します。

---

**Q1.** 「1回でも重複するとシリーズ全体を409で拒否」は、原子性（all-or-nothing）を業務ルールとして明示的に採用した設計です。`app/series/service.py:78-81` に「BR-RS-OV1/OV2: 1回でも重複すればシリーズ全体を拒否（原子性）」とあり、`app/series/service.py:83` で series と全回を単一トランザクションで登録しています。テスト `tests/test_recurring_api.py:68-89`（`test_conflict_rejects_whole_series_atomically`）も、重複時にシリーズの回が1件も作られないことを検証しています。ただし「重複回だけスキップする案を採らなかった具体的な検討経緯・議論」は、根拠となる設計ドキュメント（`business-rules.md` 等）が本作業コピーに存在しないため、コードからは「原子性を要件としたから」以上のことは分かりません。

**Q2.** 上限52回は `app/series/service.py:22`（`MAX_OCCURRENCES = 52`）および `app/series/recurrence.py:18`（`max_count: int = 52`）で定義されています。週次で52回はおよそ1年分に相当しますが、なぜ52なのかという明示的な理由・根拠はコード内コメントに記載がなく、根拠ドキュメント（`business-rules.md` の BR-RS-C7）も本作業コピーには含まれていないため、確たる理由は分かりません。

**Q3.** 各回は通常の `Reservation` 行として展開され `series_id` で紐付くだけ（`app/db/models.py:85-108`, `app/series/service.py:106-118`）なので、個別回のキャンセルは既存の単発予約キャンセルAPI `POST /reservations/{reservation_id}/cancel`（`app/reservations/router.py:51-56`）をそのまま流用できるためです。専用APIは不要という設計で、テスト `tests/test_recurring_api.py:161-173`（`test_individual_occurrence_cancel_via_existing_api`、コメントに「既存の個別キャンセル API を流用（US-R05）」）が対象回だけ cancelled になり他は active のままであることを確認しています。

**Q4.** 副作用がなくDB非依存で、単体テストおよびProperty-Based Testが容易になるためです。`app/series/recurrence.py:1-5` のモジュールdocstringに「副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想。」と明記されています。実際に `tests/test_recurrence.py` と `tests/test_recurring_pbt.py` がこの純粋関数を直接DB無しでテストしています。

**Q5.** `Base.metadata.create_all` は未作成テーブルしか作らず、既存テーブルへの列追加を行わないため、既存DBにも `series_id` を反映する目的でSQL直書きのヘルパを使っています。`app/db/database.py:36-52`（`_ensure_series_id_column`）にその理由がコメントされ、`ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を冪等に実行します。ただし「Alembicを敢えて採用しなかった意思決定の経緯」自体はコードに記載がなく、根拠ドキュメントも本作業コピーに無いため、その判断理由の詳細は分かりません（軽量・依存追加なしで済ませる意図と推測はできますが確証はありません）。

**Q6.** `hypothesis` は Property-Based Testing のために追加されています（`requirements.txt:7`、`tests/test_recurring_pbt.py:11-12` でインポート）。一部にしか適用されていないのは、PBTの対象を副作用のない純粋関数（`generate_occurrences`）とPydanticスキーマに限定しているためで、`tests/test_recurring_pbt.py:1-6` に「純粋関数・スキーマが対象のため DB 非依存」「PBT Partial モードで強制対象の PBT-02/03/07/08 に対応」と記されています。DB依存部分はPBT対象外という方針です。

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行い、隣接（`end_a == start_b`）は重ならない扱いだからです。`app/availability/service.py:14-19` の `overlaps` は `start_a < end_b and start_b < end_a` を返すため、前の予約の終了10:00と次の開始10:00では `10:00 < 10:00` が偽となり重複しません。READMEにも「半開区間で判定。隣接はOK」とあります（`README.md:9`）。

**Q8.** 含まれます。`app/series/recurrence.py:48` は `if occ_start.date() > until: break` で、開始日が until と等しい回（2030-01-15）は `>` に該当しないため生成対象になります（inclusive）。テスト `tests/test_recurrence.py:34-38`（`test_until_inclusive_boundary`）が境界含みを確認しています。

**Q9.** 両方指定すると400（ValidationError）になります（`app/series/service.py:49-53`「count または until のどちらか一方」、テスト `tests/test_recurring_api.py:92-98`）。両方省略しても同じく400になります（同条件 `(count is None) == (until is None)` が真、テスト `tests/test_recurring_api.py:101-105`）。

**Q10.** 作成できます。単発予約は `app/reservations/service.py:41` が `if start_time < datetime.now()` で過去のみ拒否するため、`start == now` は許可されます（コメントにも「start == now は許可」）。定期予約も同様に `app/series/service.py:71-72` が「start == now は許可」で最初の回の開始が過去のときのみ拒否します。

**Q11.** シリーズ全体キャンセルは `app/series/service.py:130-141`。対象は「開始時刻が now より後（未来）の active 回」のみ（`list_future_active_by_series`、`app/reservations/repository.py:60-72`、`start_time > now` かつ status=active）。
- (a) 過去に開始済みの回：`start_time > now` に該当せず対象外で、そのまま変更されません。
- (b) 既にキャンセル済みの回：status が active でないため対象外で、cancelled のまま変わりません。
- (c) もう一度実行：1回目で未来回が全て cancelled になっているため `future_active` が空になり、何も変更せず200を返します（冪等）。テスト `tests/test_recurring_api.py:147-154`（`test_cancel_series_idempotent`）が確認しています。

**Q12.** 単発予約のレスポンス契約には追加変更があります。`ReservationOut` に `series_id: str | None = None` が追加され（`app/reservations/schemas.py:28-29`）、単発予約では `null`、シリーズ回ではシリーズIDが返ります（テスト `tests/test_recurring_api.py:200-213`）。リクエスト側（`ReservationCreate`、`app/reservations/schemas.py:9-14`）は変更されていません。

**Q13.** DBレベルの制約では実現されていません。`app/db/models.py:112` にあるのは検索効率化用の非ユニーク `Index("ix_reservations_room_id_status", ...)` のみで、重複防止はアプリ層の `AvailabilityService.has_conflict`（`app/availability/service.py:28-46`）による走査チェックに依存します。そのため、UNIQUE制約や行ロックが無く、並行リクエストが同時に来た場合はチェックと挿入の間に競合が起こり、二重予約が発生しうります（`create_reservation`/`create_series` はチェック後に挿入・commitする逐次処理で、悲観・楽観ロックは実装されていません）。

**Q14.** ルート直下の `conftest.py`（`conftest.py:19-24`）が、本プロジェクトディレクトリを `brown` パッケージとして `sys.modules` にエイリアス登録し、`brown.tests.conftest` を実ファイル `tests/conftest.py` に解決させているため動きます。同ファイルのdocstring（`conftest.py:3-8`）に「既存規約 `from brown.tests.conftest import create_room` でヘルパを取得するため…エイリアスを登録する。既存テストのソースは一切変更せず、この規約を成立させるための追加設定」と記されており、既存テストの規約に合わせるため（テスト本体を書き換えないため）この方式を採っています。

**Q15.** 旧スキーマの `reservations.db` がある環境で起動すると、`create_all()`（`app/db/database.py:54-62`）が動き、`_ensure_series_id_column` が既存 `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE` で追加します。加えて `reservation_series` テーブルは未作成なので `Base.metadata.create_all` が新規作成します。2回目の起動では、`series_id` 列が既に存在するため列追加はスキップされ（冪等）、テーブルも既存のため作成されず、何も変化しません。

**Q16.** リポジトリルート（`cond-A`）で仮想環境を有効化し `pytest` を実行します（`README.md:60-64`、ルートの `conftest.py` がパス解決と`brown`エイリアスを設定）。手順例:
```bash
source .venv/bin/activate
pytest
```
実際に実行したところ **66件がパス** しました（`66 passed`）。

**Q17.** 上限超過はサービス層で検出されます。Pydanticスキーマは `count: int | None = Field(None, ge=1, ...)`（`app/series/schemas.py:18-20`）で下限1のみ課し上限を持たないため、`count=100` はスキーマを通過します。`generate_occurrences` は無制限生成を防ぐため最大 `max_count+1`（=53）件で打ち切り（`app/series/recurrence.py:36-40`）、`RecurringReservationService.create_series` が `if len(occurrences) > MAX_OCCURRENCES:` で検知して `ValidationError`→400を返します（`app/series/service.py:67-70`、BR-RS-C7）。テスト `tests/test_recurring_api.py:108-112`（count=53で400）で確認できます。

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。`app/db/models.py:2-6` のコメントに「時刻はナイーブ datetime（ローカル）」とあり、`start_time`/`end_time` は naive `datetime`（`DateTime`）として扱われます。READMEの「設計上の割り切り（今回のスコープ外）」にもタイムゾーンが挙げられており（`README.md:82-83`）、変換処理は存在しません。

**Q19.** 隔週・月次は作成できません。生成ロジックは週次固定（`app/series/recurrence.py:10` `WEEK = timedelta(days=7)`、7日刻み固定）で、頻度を指定するパラメータは `RecurringReservationCreate` に存在しません（`app/series/schemas.py:11-23` は `count`/`until` のみ）。READMEの「設計上の割り切り（今回のスコープ外）」に「隔週・月次などの複雑な繰り返し」が明記されています（`README.md:82-83`）。したがって指定するパラメータは無く、実現できません。

**Q20.** 分かりません。リポジトリ内に認証・認可の実装は一切存在せず（`app` 配下に token/auth/jwt 等の該当コードなし）、認証トークンやその有効期限を設定する箇所は見当たりません。READMEでも「認証・権限」はスコープ外と明記されています（`README.md:82-83`）。
