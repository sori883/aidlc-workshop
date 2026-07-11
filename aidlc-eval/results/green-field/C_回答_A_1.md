調査が完了しました。重要な発見をまとめると、**この cond-A ディレクトリは会議室予約システムのグリーンフィールド実装で、定期予約・認証などは README で明示的にスコープ外**とされており、コミットで brown-field 側に追加された「定期予約機能」はこの作業ディレクトリには存在しません。以下、根拠とともに回答します。

---

**Q1.** 分からない（根拠なし）。この cond-A のコードベースには定期予約（シリーズ）機能そのものが存在しません。`app/series/` は無く、予約作成は単発のみ（`app/reservations/service.py` の `create_reservation`、`app/reservations/schemas.py` の `ReservationCreate` に `count`/`until` 等は無し）。README.md でも「定期予約 … は今回のスコープ外」と明記（README.md:66）。したがって「409でシリーズ全体を拒否する／重複回だけスキップする」という設計判断は本リポジトリには存在せず、その理由も根拠がありません。

**Q2.** 分からない（根拠なし）。シリーズや回数上限（52回）を定義するコード・設定は本リポジトリに存在しません（`app/` 全体を grep しても `series`/`recurr`/`count` 上限のロジック無し）。

**Q3.** 本リポジトリに「シリーズ」概念が無いため、個別回キャンセルAPIという前提自体が成立しません。存在するキャンセルは単発予約に対する `POST /reservations/{reservation_id}/cancel` のみで、これで1件の予約を `cancelled` にします（`app/reservations/router.py`、`app/reservations/service.py` の `cancel_reservation`）。シリーズ由来の「個別回」という区別は無い、というのが実態です。

**Q4.** 分からない（根拠なし）。`app/series/recurrence.py` は存在しません（`find` で `series` 配下のファイルは0件）。週次日付生成の純粋関数も本リポジトリには見当たりません。

**Q5.** 分からない（根拠なし）。`series_id` 列は `app/db/models.py` にも実DB（`reservations.db`）のスキーマにも存在しません（`sqlite_master` を確認済み。列は id/room_id/start_time/end_time/booker_name/booker_email/status/created_at のみ）。マイグレーション用のSQLヘルパもAlembicも本リポジトリには無し。

**Q6.** 分からない（根拠なし）。`requirements.txt` に `hypothesis` は含まれていません（内容は fastapi / uvicorn[standard] / sqlalchemy / pydantic / pytest / httpx のみ）。Property-Based Testing のコードも存在しません。

**Q7.** はい、共存できます。重複判定は半開区間 `[start, end)` で行われ、`overlaps(a,b,c,d) = start_a < end_b and start_b < end_a` のため、隣接（一方の `end` == 他方の `start`、例: 10:00終了 と 10:00開始）は「重ならない」と判定されます（`app/availability/service.py` の `overlaps`、コメント「隣接（end_a == start_b など）は重ならない扱い」）。テストでも `test_adjacent_reservation_ok`（`tests/test_reservations_api.py`）と `test_adjacent_is_not_overlap`（`tests/test_overlaps.py`）で保証されています。

**Q8.** 分からない（根拠なし）。`until` パラメータを解釈する定期予約生成ロジックが本リポジトリに存在しないため、包含/非包含を判断する根拠がありません。

**Q9.** 分からない（根拠なし）。`count`／`until` を受け取る仕組みが存在しません（`ReservationCreate` にこれらのフィールドは無い、`app/reservations/schemas.py`）。

**Q10.** はい、作成できます。過去日時チェックは `if start_time < datetime.now()` で、等号（`start == now`）は拒否対象外です（`app/reservations/service.py` の BR-C4、コメント「過去日時の予約は拒否（start == now は許可）」）。

**Q11.** 分からない（根拠なし）。シリーズ全体キャンセル機能が存在しないため、(a)(b)(c) いずれも本リポジトリからは判断できません。なお単発予約のキャンセルは冪等で、既に `cancelled` の予約を再キャンセルしても `200`／`cancelled` のまま状態を変えません（`cancel_reservation`、`tests/test_reservations_api.py::test_cancel_is_idempotent`）が、これはシリーズとは無関係です。

**Q12.** この cond-A リポジトリには定期予約機能の追加自体が存在しないため、その追加に伴う契約変更という前提は成立しません。単発予約APIの契約は `ReservationCreate`（room_id / start_time / end_time / booker_name / booker_email）と `ReservationOut`（+ id / status / created_at）のままです（`app/reservations/schemas.py`）。

**Q13.** いいえ、DBレベルの制約では実現されていません。`app/db/models.py` に一意制約や排他制約は無く（あるのは検索用の複合インデックス `ix_reservations_room_id_status` のみ）、重複防止はアプリ層の逐次チェック `AvailabilityService.has_conflict`（active 予約を走査）→挿入という手順です（`app/reservations/service.py` BR-C5、`app/availability/service.py`）。ロックも一意制約も無いため、並行リクエストが同時に来た場合はチェックと挿入の間に競合が起こり得て（TOCTOU）、二重予約は起こりえます。

**Q14.** 前提が誤りです。実際にはテストは**動きません**。`tests/test_rooms_api.py` / `test_reservations_api.py` / `test_availability_api.py` は `from brown.tests.conftest import create_room` を import しますが、`brown` パッケージはどこにも存在せず、pytest 実行時に3ファイルとも `ModuleNotFoundError: No module named 'brown'` で収集エラーになります（実行して確認済み）。`create_room` と `client` フィクスチャはローカルの `tests/conftest.py` に定義されているのに、なぜ `brown.tests.conftest` から import する規約にしたのかは、リポジトリ内に根拠が無く**分からない**（誤った import 先を指しているバグと考えられます）。

**Q15.** `create_all()` は `Base.metadata.create_all()` を呼ぶだけで、既存テーブルがあれば作成をスキップし、列の追加・変更（ALTER）は一切行いません（`app/db/database.py`）。新旧でスキーマは同一（`series_id` 等の新列は無い）ため、旧 `reservations.db` があっても起動時にDBには何も変化が起きません。2回起動しても同様に何も起きません。

**Q16.** README 記載の手順は「`pip install -r requirements.txt` 後に `pytest`」（README.md）。ただし現状そのまま実行すると、上記 Q14 の `brown` import エラーで3モジュールが収集失敗します。実際にパスするのは `tests/test_overlaps.py` の**7件のみ**（実行確認済み）。他3ファイル（テスト関数は rooms 9 + reservations 13 + availability 5 = 27件）は import を修正しない限り実行されません。つまり「全部で何件パスするはず」に対し、現状のパスは7件です。

**Q17.** 分からない（根拠なし）。`count` を受け取る処理・上限超過検出のロジックは本リポジトリに存在しません。

**Q18.** タイムゾーン変換はどのレイヤでも行われていません。時刻はナイーブ `datetime`（ローカル）として保存・比較されます（`app/db/models.py` のコメント「時刻はナイーブ datetime（ローカル）」、`DateTime`（timezone なし）を使用、`datetime.now()` を各所で使用）。変換層は存在しない、が正しい答えです。

**Q19.** 分からない（根拠なし）。隔週・月次を含む定期予約のパラメータを受け取る仕組みが本リポジトリに存在しません（`ReservationCreate` に該当フィールド無し）。

**Q20.** 分からない（根拠なし）。認証・トークンの実装は本リポジトリに存在しません（`token`/`jwt`/`auth` は grep でヒットせず、README でも「認証・権限 … は今回のスコープ外」と明記、README.md:66）。有効期限を設定する箇所もありません。

---

補足: 質問群の多く（Q1〜Q6, Q8, Q9, Q11, Q17, Q19, Q20）は、コミット `878f9bd` が **brown-field ディレクトリ側**に追加した定期予約機能を前提にしていますが、今あなたが引き継いだ作業ディレクトリ `green-field/cond-A` はそれらを含まないグリーンフィールド実装（git 管理外の別コピー）です。そのため該当機能に関する設計判断はこのコードベースからは確認できません。
