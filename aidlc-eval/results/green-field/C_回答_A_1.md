調査が完了しました。結論から言うと、**この作業リポジトリ（`green-field/cond-A`）には「定期予約（recurring reservations）」機能が実装されていません**。README でも「今回のスコープ外」と明記され、`app/series/`・`series_id`・`hypothesis`・`until`/`count`/`weekly` 等のコード・依存は一切存在しませんでした。質問の多くはこの未実装機能を前提としているため、根拠がないものは「分からない」と回答します。

なお、「定期予約機能を追加」というコミット(878f9bd)は確認しましたが、その変更は**別ツリーの `brown-field/` 配下**（`brown-field/aidlc-docs/...`）に対するもので、cond-A には反映されていません。

---

Q1. 分からない（この機能はこのリポジトリに存在しません）。定期予約の作成APIそのものが実装されておらず、シリーズ生成・重複時の409挙動・スキップ仕様に関するコードや設計文書は cond-A 内に見当たりません。README には「定期予約 …（今回のスコープ外）」と明記されています。根拠: `README.md:66`、`app/reservations/`（単発予約のみ）、`grep` で `series`/`recurr` はコード内に不在。

Q2. 分からない。「52回」という上限を定める定数・バリデーション・設計記述はリポジトリ内に存在しません（`count`/`until`/回数上限に関するコードは皆無）。根拠: `app/` 全体の `grep`（該当なし）。

Q3. 分からない。そもそもシリーズ（定期予約）機能が未実装のため、個別回キャンセル専用APIの有無を論じる根拠がありません。現状のキャンセルは単発予約に対する `POST /reservations/{reservation_id}/cancel` のみです。根拠: `app/reservations/router.py:51-56`、`README.md:40`。

Q4. 分からない。`app/series/recurrence.py` はリポジトリに存在しません（`app/` 配下に `series` ディレクトリ自体がない）。純粋関数分離の理由を示す根拠もありません。根拠: `ls app`（series なし）、`find app`。

Q5. 分からない。`series_id` 列の追加や、そのためのSQL直書きヘルパ関数はリポジトリ内に存在しません。DBスキーマは `reservations(id, room_id, start_time, end_time, booker_name, booker_email, status, created_at)` のみで `series_id` を持ちません。根拠: `app/db/models.py:49-69`、`grep series_id`（該当なし）。

Q6. 分からない。`requirements.txt` に `hypothesis` は含まれておらず（`fastapi/uvicorn/sqlalchemy/pydantic/pytest/httpx` のみ）、Property-Based Testing を行うテストも存在しません。根拠: `requirements.txt:1-6`、`grep hypothesis`（該当なし）。

Q7. はい、共存できます。重複判定は半開区間 `[start, end)` で行われ、`overlaps` は `start_a < end_b and start_b < end_a` を返します。10:00終了の予約 `[…,10:00)` と 10:00開始の予約 `[10:00,…)` では `10:00 < 10:00` が偽となり重なり無しと判定されるため、隣接予約は許可されます（409になりません）。根拠: `app/availability/service.py:14-19`、`README.md:9`、テスト `tests/test_reservations_api.py:68-73`。

Q8. 分からない。`until` パラメータや定期予約の日付生成ロジックはリポジトリに存在しないため、`until=2030-01-15` の境界（inclusive/exclusive）を判断する根拠がありません。根拠: `grep until`（該当なし）。

Q9. 分からない。`count` と `until` というパラメータは実装されておらず、両立時・両省略時の挙動を規定するコードも存在しません。現状の予約作成スキーマは `room_id/start_time/end_time/booker_name/booker_email` のみです。根拠: `app/reservations/schemas.py:9-14`。

Q10. はい、作成できます。過去日時チェックは `if start_time < datetime.now(): raise ValidationError(...)` で、厳密な `<` 比較です。コメントにも「BR-C4: 過去日時の予約は拒否（start == now は許可）」とあり、`start_time == now` は拒否されません。根拠: `app/reservations/service.py:40-42`。

Q11. 分からない（シリーズ全体キャンセル機能が未実装のため）。参考までに単発キャンセルの挙動は、(既に cancelled の予約に対して) 状態を変えず200を返す冪等仕様です（active のときのみ cancelled に更新）が、シリーズ単位の過去回/キャンセル済み回/再実行の扱いを示す根拠はありません。根拠: `app/reservations/service.py:76-83`。

Q12. 変更は確認できません（そもそも定期予約機能がこのリポジトリに追加されていないため）。単発予約の作成スキーマ `ReservationCreate` にはシリーズ関連フィールドが一切なく、契約は従来どおりです。根拠: `app/reservations/schemas.py:9-14`、`app/reservations/router.py`。

Q13. いいえ、データベースレベルの制約では実現していません。`reservations(room_id, status)` に付いているのは通常のインデックスのみで、ユニーク制約や排他制約はありません。重複防止はアプリ層で「`has_conflict` で走査 → 問題なければ挿入」というチェック・アンド・挿入で行っています。ロックを取らないため、並行リクエストが同時に来た場合は TOCTOU により二重予約が起こりえます。根拠: `app/db/models.py:68-69`（Index のみ、unique なし）、`app/availability/service.py:28-46`、`app/reservations/service.py:43-58`。

Q14. 実際には**動きません**。`pytest` を実行すると `ModuleNotFoundError: No module named 'brown'` で3ファイルとも収集エラーになります。`brown` パッケージはこのリポジトリに存在せず（`tests/conftest.py` は `tests` パッケージ配下にあり `create_room` を定義しているのに、テストは `brown.tests.conftest` から import している）、import が解決されません。この規約に合わせた理由を示す根拠もありません（おそらく `brown` をパッケージ名とする別プロジェクトからテストを流用した名残と推測されますが、断定はできません）。根拠: `tests/test_reservations_api.py:4`・`tests/test_rooms_api.py:2`・`tests/test_availability_api.py:4`、`tests/conftest.py:55-67`、実行結果（3 errors during collection）。

Q15. 起動時に `create_all()` が呼ばれますが、これは「存在しないテーブルのみ作成」する動作で、既存テーブルへの列追加やスキーマ変更（マイグレーション）は行いません。したがって旧スキーマの `reservations.db` があっても、テーブルが既存であれば何も変更されません。2回起動しても同様で、`create_all` は冪等なため追加の変化は起きません（データも保持されたまま）。根拠: `app/db/database.py:35-40`、`app/main.py:38-40`、`app/core/config.py:12`（既定DB `sqlite:///./reservations.db`）。なお `series_id` 追加のような処理は存在しません。

Q16. 手順は「`pip install -r requirements.txt` 後にリポジトリルートで `pytest`」です（`README.md:57-61`）。ただし現状では前述の `brown` import エラーにより**1件もパスしません**（収集段階で3ファイルがエラーになり、0 passed）。したがって「何件パスするはずか」＝現状は0件です。根拠: `README.md:60`、`pytest` 実行結果。

Q17. 分からない。`count` パラメータおよび回数上限超過の検出処理はリポジトリに存在しません。`count=100` を扱うコードパスがないため、どこで検出されるかを答える根拠がありません。根拠: `grep count`（`app/rooms/service.py:74` のクエリ `.count()` のみで無関係）。

Q18. タイムゾーン変換はどのレイヤでも行っていません。時刻はナイーブな `datetime`（ローカル）としてそのまま扱い・保存しています（モデルにも「時刻はナイーブ datetime（ローカル）」と明記）。根拠: `app/db/models.py:1-12,56-57`、`app/reservations/schemas.py:11-12`（`datetime` を変換なしで受領）。

Q19. 分からない。隔週（biweekly）・月次（monthly）はもちろん、頻度を指定するパラメータ自体が実装されていません（`weekly`/`interval`/`frequency` などのコードは不在）。根拠: `grep`（該当なし）、`app/reservations/schemas.py`。

Q20. 分からない（該当なし）。認証・権限はスコープ外で、認証トークンやその有効期限を設定する箇所は存在しません（`app/core/config.py` は `database_url/host/port` のみ）。根拠: `README.md:66`、`app/core/config.py:8-14`、`grep token/auth/expire`（該当なし）。

---

補足: 質問群が前提とする定期予約機能は、`git show 878f9bd` によると本リポジトリの別ツリー `brown-field/` 側に追加されたもので、あなたの作業対象である `green-field/cond-A` には存在しません。cond-A の実態に即して回答しています。
