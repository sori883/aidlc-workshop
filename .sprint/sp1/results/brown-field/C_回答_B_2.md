調査完了しました。66件のテストが全てパスすることも確認しました。以下、20問への回答です。

---

**Q1.** 「重複した回だけスキップ」ではなく「シリーズ全体を409で拒否（原子性優先）」にしたのは、要件確定フェーズでユーザーがそう選択したためです。`aidlc-docs/inception/requirements/requirement-verification-questions.md` の Question 1 で「A) 全体拒否」「B) スキップ作成」「C) 呼び出し側が選択（on_conflict パラメータ）」の3案が提示され、`aidlc-docs/audit.md`（45行目）の対話記録で「Q1=全体拒否」が採用されています。設計意図は「シリーズ作成を全成功または全ロールバックの単一トランザクションにし、途中まで作られた中途半端な状態を残さない」という原子性の担保です（`app/series/service.py:78-81`、`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md` BR-RS-OV2）。

**Q2.** 52回は「約1年ぶん（52週）」に相当するためです。無限・過大なシリーズ作成を防ぐ上限として設定され、`requirement-verification-questions.md:77` に「最大52回=約1年。超過時は 400」と明記され、これがユーザーに採用されています（`audit.md:45` Q4=上限あり(52)）。定数は `app/series/service.py:22`（`MAX_OCCURRENCES = 52`）。

**Q3.** 各回は `series_id` を持つ通常の `Reservation` 行にすぎず、既存の単発予約用キャンセルAPI `POST /reservations/{reservation_id}/cancel` がそのまま機能するため、新規APIを作らない方針にしたからです（`aidlc-docs/inception/requirements/requirements.md` FR-3、`business-rules.md` BR-RS-I1）。個別回のキャンセルは、対象の回の予約IDを使って既存の `POST /reservations/{id}/cancel` を呼びます（テスト `tests/test_recurring_api.py:161-173` の `test_individual_occurrence_cancel_via_existing_api` で実証、実装は `app/reservations/service.py:76-83`）。

**Q4.** 副作用なし・DB非依存でユニットテストおよびProperty-Based Testingが容易になるためです。既存の重複判定 `overlaps`（`app/availability/service.py:14`）と同じ設計思想を踏襲しています。`app/series/recurrence.py:1-5` のdocstring、および `requirements.md` NFR-3、`nfr-requirements.md` NFR-RS-4 に明記されています。

**Q5.** このプロジェクトが元々マイグレーションツールを使っておらず、起動時の `Base.metadata.create_all()` でスキーマを作る方式だからです。`create_all` は未作成テーブルしか作らず既存テーブルへの列追加を行わないため、既存の `reservations.db` に `series_id` 列を補うヘルパ `_ensure_series_id_column`（`app/db/database.py:36-51`）を追加し、`create_all()` の前に冪等な `ALTER TABLE` を実行しています。既存方式との整合を優先した結果です（`tech-stack-decisions.md` の「マイグレーション方針」）。

**Q6.** hypothesis はProperty-Based Testing（PBT）フレームワークとして追加されました（`requirements.txt:7`、`tech-stack-decisions.md`）。一部のテストにしか適用されていないのは、拡張のオプトインで「PBT = Partial」が選ばれ、PBT-02（Round-trip）/PBT-03（Invariant）/PBT-07（Generator quality）/PBT-08（Shrinking）のみを強制対象とし、対象を純粋関数（`generate_occurrences`）とスキーマのシリアライズ往復に限定したためです（`requirements.md` の Extension Configuration、`nfr-requirements.md` NFR-RS-6、`tests/test_recurring_pbt.py` の冒頭docstring）。

**Q7.** 共存できます。重複判定は半開区間 `[start, end)` で行われ、隣接（`end_a == start_b`）は「重ならない」扱いだからです。`app/availability/service.py:14-19` の `overlaps` は `start_a < end_b and start_b < end_a` を返すため、10:00終了と10:00開始は `10:00 < 10:00` が偽となり重複しません。

**Q8.** 含まれます。`until` は「各回の開始日が until 以下（inclusive）」で判定され、`app/series/recurrence.py:48` の打ち切り条件は `occ_start.date() > until`（厳密に超えた場合のみ break）です。よって開始日がちょうど 2030-01-15 の回は含まれます（`tests/test_recurrence.py:34-38` の `test_until_inclusive_boundary` で実証）。ただし、これは週次刻みが実際にその日付に到達する場合に限られます（起点から7日刻みで 2030-01-15 に一致する回があるとき）。

**Q9.** 両方指定すると400（ValidationError）になります。両方省略しても400になります。終了条件は count か until の「ちょうど一方のみ」が要求されるためです（`app/series/service.py:50-53` の `if (count is None) == (until is None):`、`app/series/recurrence.py:28-29`、business-rules BR-RS-C4）。テスト `test_both_count_and_until_400` / `test_neither_count_nor_until_400`（`tests/test_recurring_api.py:92-105`）で確認できます。

**Q10.** 作成できます。過去判定は `occurrences[0][0] < datetime.now()`（`app/series/service.py:72`）で「厳密に過去」のみを拒否し、start == now は許可します（単発予約 `app/reservations/service.py:41` も同様、business-rules BR-RS-C8）。

**Q11.** キャンセルは「開始時刻が現在より後（未来）の active 回のみ」を対象とします（`app/series/service.py:130-141`、リポジトリ `list_future_active_by_series` で `start_time > now` かつ status=active を抽出、`app/reservations/repository.py:60-72`）。したがって、(a) 過去に開始済みの回は変更されず active のまま残ります。(b) 既にキャンセル済みの回も変更されません。(c) もう一度実行しても、対象となる未来のactive回が無ければ状態を変えずに200を返します（冪等、business-rules BR-RS-X1〜X3、テスト `test_cancel_series_idempotent`）。

**Q12.** ありません。リクエスト契約 `ReservationCreate` は不変で、レスポンス `ReservationOut` に `series_id`（`str | None`、単発は `null`）が追加されただけです（`app/reservations/schemas.py:9-29`）。フィールド追加のみで、既存テストは個別フィールド検証のため壊れません（制約 C-1、business-rules BR-RS-D1/D2、`requirements.md` FR-4.1）。

**Q13.** いいえ、DBレベルの制約（ユニーク制約など）では実現されていません。アプリケーション層で `AvailabilityService.has_conflict` が対象会議室の active 予約を走査して判定する方式です（`app/availability/service.py:28-46`）。モデルにはインデックス `ix_reservations_room_id_status` があるだけで重複防止用の一意制約はありません（`app/db/models.py:112`）。並行リクエストが同時に来た場合、「チェック→INSERT」の間にロックが無いため二重予約は起こりえます（read-then-write のレース）。NFR-5 で高負荷・並行性はスコープ外とされています。

**Q14.** リポジトリルートの `conftest.py`（`/conftest.py:19-24`）が、`brown` という名前を本ディレクトリへのパッケージエイリアスとして `sys.modules` に登録しているため動きます。`brown.__path__` を現ディレクトリに向けることで `brown.tests.conftest` が実ファイル `tests/conftest.py` に解決されます。この規約に合わせた理由は、既存テストが `from brown.tests.conftest import ...` という規約でインポートしており、その既存テストを一切改変せずにパスさせる制約（C-4）があったためです（`requirements.md:16` の Constraints、`conftest.py` のdocstring）。

**Q15.** 起動時の `create_all()`（`app/main.py:42` → `app/db/database.py:54-62`）が実行され、`_ensure_series_id_column` が既存 `reservations` テーブルに `series_id VARCHAR(36)` 列を追加し、続く `Base.metadata.create_all` が未作成の `reservation_series` テーブルを新規作成します。既存の予約行の `series_id` は NULL のまま維持されます。2回起動しても、列の存在チェック（`if "series_id" not in columns`）とテーブル存在チェックにより冪等で、何も追加変更されません（`audit.md:285` でマイグレーション冪等検証OKと記録）。

**Q16.** 手順: リポジトリルート（`cond-B`）で仮想環境を用意し `pip install -r requirements.txt`（hypothesis を含む）でインストール後、`python -m pytest` を実行します（`conftest.py` が `app` と `brown` の import 解決を行うため追加設定は不要）。全部で **66件** がパスするはずです（内訳: 既存回帰34 + 新規例示27 + PBT 5、`audit.md:285`。私の実行でも「66 passed」を確認）。ビルド/テスト手順は `aidlc-docs/construction/build-and-test/` にも記載されています。

**Q17.** まずスキーマ `count: Field(None, ge=1)`（`app/series/schemas.py:18`）は下限のみで上限が無いため、count=100 はPydantic検証を通過します。次に純粋関数 `generate_occurrences` が上限超過でも無制限生成を防ぐため `max_count + 1`（=53件）まで生成して打ち切り（`app/series/recurrence.py:39-40`）、サービス層の `if len(occurrences) > MAX_OCCURRENCES`（`app/series/service.py:67`、53 > 52）で `ValidationError` を送出し、400を返します（テスト `test_over_max_count_400`）。

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。時刻はナイーブな datetime（ローカル）として扱われ（`app/db/models.py:12` のモデル方針コメント、`DateTime` 列）、タイムゾーン対応は明示的にスコープ外とされています（`requirements.md` NFR-5、`nfr-requirements.md` の「非対象（明示）」）。

**Q19.** できません。この機能は週次（7日刻み固定）のみをサポートし、隔週・月次を指定するパラメータは存在しません。生成は `generate_occurrences` が `WEEK = timedelta(days=7)` を固定で使用しており（`app/series/recurrence.py:10,37,46`）、リクエストにも間隔指定フィールドはありません（`app/series/schemas.py`）。隔週・月次などの複雑な繰り返しは明示的にスコープ外です（`requirements.md` NFR-5）。

**Q20.** 設定されていません。このアプリケーションには認証・認可の仕組み自体が存在せず、トークンや有効期限を設定する箇所もありません。認証/認可は明示的にスコープ外とされています（`requirements.md` NFR-5、`nfr-requirements.md` の「非対象（明示）」、`app/core/config.py` にも認証関連設定は無し）。
