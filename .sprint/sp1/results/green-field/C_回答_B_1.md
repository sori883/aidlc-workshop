調査が完了しました。事実関係を整理して回答します。

---

## 前提（重要）

私の作業ディレクトリ `green-field/cond-B` は、リポジトリ内の **「green」シナリオ（会議室予約システムをゼロから構築）** の成果物です（`prompt.md`）。ここには **定期予約（recurring reservations / series）機能は実装されていません**。以下の事実で確認できます:

- `app/` 配下に `series` モジュールは無い（`app/reservations`, `app/rooms`, `app/availability` のみ）
- `app/db/models.py` に `series_id` 列やSeriesモデルは無い
- `requirements.txt` に `hypothesis` は無い
- `app` 全体で `series|recurr|定期|weekly|until` 等が一切ヒットしない

一方、質問の大半が説明している定期予約機能（`app/series/recurrence.py`, `hypothesis`, `series_id`, 52回上限, `from brown.tests.conftest`）は、**同じgitリポジトリ内の別プロジェクト `brown-field/`（「brown」シナリオ＝既存システムへの定期予約追加）** に存在します（`/Users/const/sori883/aidlc-workshop/brown-field/app/series/recurrence.py` 等）。

ルールに従い、以下は **cond-B のコードに根拠があるものだけ回答し、cond-Bに根拠が無い（定期予約機能に依存する）ものは「分からない」** とします。cond-Bの内部を、別コードベースであるbrown-fieldの実装で推測補完することはしません。

---

Q1. 分からない。cond-Bのコードベースに定期予約（シリーズ）機能そのものが存在しないため（`app/` に `series` モジュール無し、`app/reservations/service.py` に一括生成・シリーズ重複ロジック無し）、409で拒否する/スキップするという設計判断の根拠は本リポジトリからは見つかりません。

Q2. 分からない。cond-Bにシリーズ機能・回数上限（52回）に関する記述・定数はありません（`app` 全体で該当語ヒット無し、`app/db/models.py` にSeriesモデル無し）。

Q3. 分からない（シリーズ前提の部分）。cond-Bにシリーズ（複数回の予約群）という概念自体が無いため、「個別回のキャンセル専用APIが無い理由」は根拠がありません。なお、cond-Bにある単発予約のキャンセルは `POST /reservations/{reservation_id}/cancel` で行います（`app/reservations/router.py:53-59`、`app/reservations/service.py:76-83`）。

Q4. 分からない。cond-Bに `app/series/recurrence.py` は存在しません。純粋関数として分離されている理由は本リポジトリからは確認できません。（参考までに、cond-Bで純粋関数として分離されているのは重複判定 `overlaps()` で、これは `app/availability/service.py:14-19` にあります。ただしこれは日付生成ではなく重複判定です。）

Q5. 分からない（`series_id` 列追加の部分）。cond-Bに `series_id` 列やその追加ヘルパは存在しません。なお、cond-Bはそもそもマイグレーションツールを使っておらず、起動時に `Base.metadata.create_all()` でテーブルを新規作成する方式です（`app/db/database.py:35-40`、`app/main.py:39`）。既存列の変更・追加は行いません。

Q6. cond-Bの `requirements.txt` に `hypothesis` は含まれていません（`requirements.txt` は `fastapi, uvicorn[standard], sqlalchemy>=2.0, pydantic>=2.0, pytest, httpx` のみ）。したがってcond-BではProperty-Based Testingは導入されておらず、「hypothesisが依存に追加されている目的」は本リポジトリには該当しません（分からない）。

Q7. はい、共存できます。重複判定は半開区間 `[start, end)` で行われ、隣接（`end_a == start_b`）は重ならない扱いです。`app/availability/service.py:14-19` の `overlaps()` は `start_a < end_b and start_b < end_a` を返すため、10:00終了の予約 `[…,10:00)` と 10:00開始の予約 `[10:00,…)` は `start_b < end_a`（10:00 < 10:00）が偽となり重複しません（同ファイルのdocstring「隣接は重ならない扱い（半開区間）」）。

Q8. 分からない。cond-Bに `until` パラメータや週次生成ロジックが存在しないため（`app` 全体で `until` ヒット無し）、`until=2030-01-15` の境界挙動は本リポジトリからは判断できません。

Q9. 分からない。cond-Bに `count`/`until` パラメータを受け付ける定期予約エンドポイントは存在しません（`app/reservations/schemas.py` の `ReservationCreate` は `room_id, start_time, end_time, booker_name, booker_email` のみ）。両指定・両省略時の挙動は本リポジトリからは確認できません。

Q10. はい、作成できます。`app/reservations/service.py:40-42` の BR-C4 は `if start_time < datetime.now(): raise ValidationError` であり、コメントにも「過去日時の予約は拒否（start == now は許可）」と明記されています。`start_time` が現在時刻とちょうど同じ場合は `<` を満たさないため拒否されず、作成可能です。

Q11. 分からない（シリーズ全体キャンセルの部分）。cond-Bにシリーズ一括キャンセル機能は存在しません。参考として、cond-Bの単発予約キャンセルは冪等で、`active` のときのみ `cancelled` に変更し、既に `cancelled` なら状態を変えず成功します（(b)(c)に相当：`app/reservations/service.py:78-83`、BR-X3）。ただし「(a)過去に開始済みの回」をシリーズキャンセルで除外する等の挙動は本リポジトリには根拠がありません。

Q12. cond-Bでは定期予約機能の追加自体が行われていないため（`app` に `series` 無し）、それに起因する単発予約APIの契約変更もありません。単発予約API（`app/reservations/router.py`、`app/reservations/schemas.py`）は定期予約と無関係に存在しています。「定期予約追加による契約変更」は本リポジトリには該当しません。

Q13. データベースレベルの制約では実現されていません。`app/db/models.py:68-69` にあるのは通常インデックス `ix_reservations_room_id_status`（重複チェック走査の高速化用）のみで、UNIQUE制約や排他制約はありません。重複防止はアプリケーション層の「`has_conflict` で走査→挿入」（`app/reservations/service.py:44-58`、`app/availability/service.py:28-46`）で行われます。DB制約が無いため、並行リクエストが同時に来た場合は両方が `has_conflict` を通過してから両方が挿入する競合（TOCTOU）が起こり得て、二重予約は発生し得ます。

Q14. cond-Bでは、実際にはテストは**動きません**。`tests/test_rooms_api.py:2`、`tests/test_reservations_api.py:4`、`tests/test_availability_api.py:4` はいずれも `from brown.tests.conftest import create_room` をインポートしていますが、`brown` パッケージはcond-B内に存在しないため、`python -m pytest` を実行すると3モジュールが `ModuleNotFoundError: No module named 'brown'` で収集エラーになります（実行確認済み）。したがって「なぜ動くのか」という前提はcond-Bでは成立せず、これらのテストは壊れています。この `brown.tests.conftest` という記述は、別プロジェクト `brown-field/` からの流用痕跡と考えられます（規約に合わせた理由自体は本リポジトリからは確認できず、分からない）。

Q15. cond-Bは起動時に `Base.metadata.create_all()` を呼ぶだけです（`app/main.py:39`、`app/db/database.py:35-40`）。`create_all` は「存在しないテーブルのみ作成」し、既存テーブルの列追加・スキーマ変更は行いません。したがって旧スキーマの `reservations.db` があっても、既存テーブルはそのまま・不足テーブルのみ作成され、列の移行は起きません（cond-Bには追加すべき `series_id` 等もありません）。2回起動しても `create_all` は冪等で、DBに変化は生じません。

Q16. 手順は、依存インストール（`pip install -r requirements.txt`）後、リポジトリルート（cond-B）で `python -m pytest` を実行します。ただし現状、上記Q14の `brown` インポート問題により、`test_availability_api.py`/`test_reservations_api.py`/`test_rooms_api.py` の3モジュール（計27テスト関数）が収集エラーで実行できません。実際にパスするのは `app` から正しくインポートしている `tests/test_overlaps.py` のみで、**7件パス**します（`python -m pytest tests/test_overlaps.py` → 7 passed を実行確認）。「全テストがパスするはず」という前提はcond-Bでは成立しません。

Q17. 分からない。cond-Bに `count` パラメータや回数上限（52回）チェックは存在しません（`app/reservations/schemas.py` に `count` 無し、`app` 全体で該当ロジック無し）。上限超過検出の場所は本リポジトリからは確認できません。

Q18. cond-Bではタイムゾーン変換はどのレイヤでも行われていません。時刻はナイーブ `datetime`（ローカル）として扱われます（`app/db/models.py` 冒頭コメント「時刻はナイーブ datetime（ローカル）」、`app/reservations/schemas.py` の `start_time`/`end_time` は素の `datetime`）。`app` 全体で `timezone|tzinfo|utc|astimezone|zoneinfo` は一切ヒットせず、変換ロジックは存在しません。

Q19. 分からない。cond-Bに定期予約（週次・隔週・月次）を作成する機能・パラメータは存在しません（`ReservationCreate` に繰り返し指定フィールド無し、`app` に `weekly`/`monthly` 等ヒット無し）。指定すべきパラメータは本リポジトリからは確認できません。

Q20. 分からない（該当なし）。cond-Bには認証機構そのものが存在しません。`app` 全体で `token|auth|jwt|login|password|expire` は一切ヒットせず、`app/core/config.py` の設定も `database_url`/`host`/`port` のみで、認証トークンや有効期限の設定箇所はありません。
