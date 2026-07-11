調査が完了しました。重要な発見として、この作業ディレクトリ（green-field/cond-A）は、質問が前提とする「定期予約（series）機能」を実装していません。質問の多くはブラウンフィールド側の別実装を前提としており、本リポジトリには根拠がありません。事実に基づいて回答します。

---

まず全体像として重要な事実を共有します。**本リポジトリ（`work/green-field/cond-A`）は単発予約のみの会議室予約システムで、定期予約 / series 機能は実装されていません。** README.md の「設計上の割り切り（今回のスコープ外）」に「定期予約 / 認証・権限 / …」と明記されており（`README.md`）、`app/` 配下に `series` モジュールや `recurrence.py`、`series_id` 列、`count`/`until` パラメータは一切存在しません（`grep` で該当なし、`app/` ツリー確認済み）。したがって定期予約に関する質問の多くは、本リポジトリには根拠がなく「分からない（存在しない）」が正直な回答になります。

---

**Q1.** 分からない（本リポジトリには定期予約機能自体が存在しないため）。`app/` 配下に series/recurrence 関連コードはなく、README.md でも定期予約はスコープ外と明記されています（`README.md`, `app/` ツリー全体）。「重複時にシリーズ全体を409で拒否する／重複回だけスキップする」といった挙動を判断する根拠はありません。

**Q2.** 分からない。52回上限を示す定数・ロジックはリポジトリ内に存在しません（`grep` で `52`/series 該当なし）。

**Q3.** 分からない（シリーズ／個別回という概念が存在しないため）。なお本リポジトリの予約キャンセルは単発予約に対する `POST /reservations/{reservation_id}/cancel`（冪等）のみで、これは `app/reservations/service.py` の `cancel_reservation` および `README.md` に記載されています。シリーズ個別回のキャンセル手段については根拠がありません。

**Q4.** 分からない。`app/series/recurrence.py` は本リポジトリに存在しません（`app/` 配下に `series` ディレクトリなし）。純粋関数として分離されている中核ロジックとしては、重複判定の `overlaps()` が `app/availability/service.py` に純粋関数として定義されていますが、これは週次日付生成とは無関係です。

**Q5.** 分からない。`series_id` 列は存在せず、Alembic 等のマイグレーションツールもSQL直書きヘルパも見当たりません。本リポジトリのスキーマ管理は `app/db/database.py` の `create_all()`（`Base.metadata.create_all`）による「未作成テーブルの自動生成」のみで、列追加のマイグレーションは行っていません（`app/db/database.py`, `app/main.py`）。

**Q6.** 前提が本リポジトリに当てはまりません。`hypothesis` は依存に**追加されていません**。`requirements.txt` は `fastapi / uvicorn[standard] / sqlalchemy>=2.0 / pydantic>=2.0 / pytest / httpx` のみで、コード内にも `hypothesis` の import はありません（`requirements.txt`、`grep hypothesis` 該当なし）。したがって Property-Based Testing は本リポジトリでは用いられていません。

**Q7.** はい、共存できます。重複判定は半開区間 `[start, end)` で行い、`overlaps()` は `start_a < end_b and start_b < end_a` を返すため、「10:00終了（…-10:00）」と「10:00開始（10:00-…）」は隣接扱いで重ならず、両方 active で作成できます（`app/availability/service.py` の `overlaps` と docstring「隣接（end_a == start_b など）は重ならない扱い」、`tests/test_overlaps.py`）。

**Q8.** 分からない（`until` パラメータおよび定期予約生成ロジックが存在しないため）。`app/reservations/schemas.py`・`router.py` に `until` は存在しません。

**Q9.** 分からない（`count` / `until` パラメータが存在しないため）。定期予約作成APIそのものが本リポジトリにありません。

**Q10.** はい、作成できます。`app/reservations/service.py` の過去日時チェックは `if start_time < datetime.now(): raise ValidationError(...)` であり、`start == now` は拒否対象外です（同ファイルのコメントにも「BR-C4: 過去日時の予約は拒否（start == now は許可）」と明記）。ただし判定は naive なローカル `datetime.now()` との比較です。

**Q11.** 分からない（シリーズ全体キャンセルという機能が存在しないため）。本リポジトリの単発キャンセル `cancel_reservation` は、active のときのみ cancelled にし、既に cancelled なら状態を変えず冪等に成功します（(c) 相当の再実行は冪等）が、(a) 過去に開始済みの回・(b) シリーズという概念自体の扱いについては根拠がありません（`app/reservations/service.py`）。

**Q12.** 本リポジトリには定期予約機能の追加自体がありません。よって「今回の追加による契約変更」を語る根拠はなく、単発予約API（`POST /reservations` ほか）の契約は `app/reservations/schemas.py`・`router.py` に定義されたものがそのまま存在するのみです。

**Q13.** いいえ、DBレベルの制約では実現されていません。重複防止はアプリケーション層で、`AvailabilityService.has_conflict()` が対象会議室の active 予約を走査して `overlaps()` で判定し、`create_reservation` が「重複チェック→挿入」を行う実装です（`app/availability/service.py`, `app/reservations/service.py`）。`app/db/models.py` には一意制約や排他制約はなく、`(room_id, status)` の**非ユニークなインデックス**があるだけです。したがって、チェックと挿入の間に別リクエストが割り込む並行実行では、二重予約が起こりえます（チェックと挿入がアトミックにロックされていないため）。

**Q14.** 前提の「なぜ動くのか」に反し、**本リポジトリではこのインポートは解決できません**。`tests/test_rooms_api.py`・`test_reservations_api.py`・`test_availability_api.py` は `from brown.tests.conftest import create_room` としていますが、リポジトリにも環境にも `brown` パッケージは存在しません（`find` で該当なし、`python -c "import brown"` は ImportError）。実体の共通フィクスチャ・`create_room` ヘルパは `tests/conftest.py` にあり、`brown.tests.conftest` ではありません。つまりこの3ファイルはこの環境ではコレクション時に ImportError となり、そのままでは動きません（`app.availability.service` を直接 import する `tests/test_overlaps.py` のみ import 可能）。この規約に合わせた理由は、リポジトリ内に根拠がなく分かりません（ブラウンフィールド側の別実装からテストが持ち込まれた痕跡と推測されますが、確証はありません）。

**Q15.** `app/db/database.py` の `create_all()` は `Base.metadata.create_all(bind=engine)` を呼ぶだけで、これは「存在しないテーブルのみ作成」する動作です。既存テーブルへの列追加・変更は行いません。したがって旧スキーマの `reservations.db` があれば既存テーブルはそのまま保持され（不足列があってもマイグレーションされない）、2回起動しても `create_all` は冪等で何も変更しません（`app/db/database.py`, `app/main.py`）。なお本リポジトリには `series_id` 追加のようなスキーマ変更自体がありません。

**Q16.** 手順は README.md 記載の通り、`python -m venv .venv && source .venv/bin/activate`、`pip install -r requirements.txt`、`pytest` です（`README.md`）。ただし「全部で何件パスするか」は確定的に答えられません。テスト関数は計34個（`test_availability_api.py`=5, `test_overlaps.py`=7, `test_reservations_api.py`=13, `test_rooms_api.py`=9）ですが、うち27個を含む3ファイルが解決不能な `from brown.tests.conftest import create_room` を import しており（Q14 参照）、この環境ではコレクション段階で失敗します。self-contained なのは `test_overlaps.py`（7件）のみです。よって「34件全部パス」とは言えず、正確なパス件数は現状の環境では確認できません。

**Q17.** 分からない（`count` パラメータおよびシリーズ回数の上限検出ロジックが存在しないため）。`app/reservations/` に count/上限の検証は見当たりません。

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。`app/db/models.py` の docstring に「時刻はナイーブ datetime（ローカル）」と明記され、`start_time`/`end_time` は `DateTime`（timezone なし）で保存され、比較は `datetime.now()`（naive ローカル）と行われます（`app/db/models.py`, `app/reservations/service.py`）。変換レイヤは存在しません。

**Q19.** 分からない（隔週・月次を含む定期予約の作成APIやパラメータが存在しないため）。`app/reservations/schemas.py` に周期指定パラメータはありません。

**Q20.** 分からない（認証機構が存在しないため）。README.md で「認証・権限」はスコープ外と明記され、`app/core/config.py` の設定は `database_url` / `host` / `port` のみで、トークンや有効期限の設定は存在しません（`README.md`, `app/core/config.py`）。
