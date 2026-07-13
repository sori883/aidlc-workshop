調査が完了しました。以下、20問すべてに回答します。

**重要な前提**: 私が引き継いだこのリポジトリ（作業ディレクトリ `green-field/cond-A`）は、**定期予約（recurring reservations）機能を実装していません**。`README.md` の「設計上の割り切り（今回のスコープ外）」に「定期予約 / 認証・権限 / …」と明記されており、`app/` 配下に `series` モジュール・`recurrence.py`・`series_id` 列・`count`/`until`/`frequency` 等は一切存在しません（`grep` で確認済み）。質問の多くはこのリポジトリには存在しない機能・設計判断を前提としているため、その旨を根拠付きで回答します。

---

Q1. **回答できません（この機能はこのリポジトリに存在しません）。** 定期予約機能自体が未実装で、シリーズ生成や重複時の409挙動を扱うコードは見当たりません。`README.md` は定期予約を明確に「スコープ外」としています。よって「重複回だけスキップしない理由」を語る根拠はなく、分かりません。根拠: `README.md`（設計上の割り切り）、`app/reservations/service.py`（単発予約のみ）。

Q2. **分からない。** シリーズの回数上限（52回）に相当するコードも定数も存在しません。`grep -rniE "series|count|until"` でヒットするのは `app/rooms/service.py:74` の `.count()`（会議室の予約件数集計）のみで、シリーズ上限とは無関係です。根拠: `app/` 全体の検索結果、`app/reservations/`。

Q3. シリーズ（定期予約）機能自体が存在しないため「シリーズ内の個別回キャンセル専用API」も存在しません。このリポジトリの予約キャンセルは単発予約に対する `POST /reservations/{reservation_id}/cancel`（冪等）のみです。根拠: `app/reservations/router.py`（`cancel_reservation`）、`app/reservations/service.py:76-83`、`README.md`（API概要表）。

Q4. **分からない。** `app/series/recurrence.py` というファイルは存在しません（`app/series` ディレクトリ自体がない）。週次の日付生成ロジックや純粋関数への分離は確認できないため、その理由を答える根拠がありません。根拠: `find app -name '*.py'`（seriesモジュールなし）。

Q5. **分からない。** `series_id` 列は `reservations` テーブルにも `Reservation` モデルにも存在しません（列は id/room_id/start_time/end_time/booker_name/booker_email/status/created_at のみ）。SQL直書きヘルパやマイグレーション処理も見当たりません。よって列追加の手段や経緯を答える根拠がありません。根拠: `app/db/models.py:49-65`、既存 `reservations.db` のスキーマ確認結果。

Q6. **該当なし（この目的は確認できません）。** `hypothesis` は依存に**含まれていません**。`requirements.txt` は `fastapi / uvicorn[standard] / sqlalchemy>=2.0 / pydantic>=2.0 / pytest / httpx` のみで、Property-Based Testing も使われていません。根拠: `requirements.txt`、`grep -r hypothesis`（該当なし）。

Q7. **共存できます（重ならない扱い）。** 重複判定は半開区間 `[start, end)` で行われ、`overlaps()` は `start_a < end_b and start_b < end_a` を返します。「10:00終了」の予約の `end=10:00` と「10:00開始」の予約の `start=10:00` は隣接であり、`start_b(10:00) < end_a(10:00)` が偽になるため重ならず、両方作成できます。根拠: `app/availability/service.py:14-19`、`README.md`（「隣接はOK、重なりは409」）。

Q8. **分からない（`until` パラメータは存在しません）。** 定期予約・`until` 指定の概念がこのリポジトリにないため、境界（生成対象に含むか）を答える根拠がありません。根拠: `app/reservations/schemas.py`（`ReservationCreate` に until なし）、`app/` 全体の検索結果。

Q9. **分からない（`count`/`until` は存在しません）。** 予約作成スキーマ `ReservationCreate` は room_id/start_time/end_time/booker_name/booker_email のみで、`count`・`until` フィールドはありません。両方指定/両方省略時の挙動を答える根拠がありません。根拠: `app/reservations/schemas.py:9-14`。

Q10. **作成できます。** バリデーションは `if start_time < datetime.now()` で、`start_time == now`（ちょうど同時刻）は条件を満たさないため拒否されません。コードのコメントにも「BR-C4: 過去日時の予約は拒否（start == now は許可）」と明記されています。根拠: `app/reservations/service.py:40-42`。

Q11. **回答できません（シリーズ全体キャンセルは存在しません）。** 定期予約のシリーズ一括キャンセル機能が未実装のため、(a)過去に開始済みの回、(b)キャンセル済みの回、(c)再実行時の挙動を答える根拠がありません。なお単発予約のキャンセルは冪等で、既に `cancelled` の場合は状態を変えず成功します（`service.py:78-83`）が、これはシリーズとは無関係です。根拠: `app/reservations/service.py`、`app/reservations/router.py`。

Q12. **変更はありません（そもそも定期予約機能が追加されていません）。** このリポジトリには定期予約機能が導入されておらず、単発予約API（`POST /reservations` 等）のスキーマ `ReservationCreate`/`ReservationOut` は従来のフィールドのみです。根拠: `app/reservations/schemas.py`、`app/reservations/router.py`。

Q13. **DBレベルの制約では実現されていません。並行リクエストでは二重予約が起こりえます。** 重複防止はアプリ層で、`has_conflict()` が対象会議室の active 予約を Python でループ走査し `overlaps()` で判定するだけです。`reservations` テーブルには重複を禁止する UNIQUE 制約や排他制約はなく（インデックス `ix_reservations_room_id_status` は検索効率化目的）、チェックと挿入の間にロックもありません。よって同時に来た2つのリクエストが両方とも「重複なし」と判定して両方挿入する競合が起こりえます。根拠: `app/availability/service.py:28-46`、`app/db/models.py:49-69`、`app/reservations/service.py:43-58`。

Q14. **前提が誤りで、実際にはテストは動きません。** `tests/test_rooms_api.py`・`test_reservations_api.py`・`test_availability_api.py` は `from brown.tests.conftest import create_room` を import していますが、`brown` パッケージはこのリポジトリのどこにも存在しません。実際に `pytest` を実行すると3ファイルとも `ModuleNotFoundError: No module named 'brown'` で collection エラーになります。`create_room` ヘルパは実際には `tests/conftest.py` に定義されており、正しくは `from tests.conftest import` 等であるべきところが `brown.` プレフィックスになっている壊れた状態です。この規約に合わせた理由は根拠がなく分かりません。根拠: `tests/test_rooms_api.py:2` 他、`tests/conftest.py:55`、`pytest` 実行結果。

Q15. **既存の `reservations.db` があってもスキーマは変更されません。2回起動しても同じです（冪等）。** 起動時 `create_all()` は `Base.metadata.create_all(bind=engine)` を呼ぶだけで、既定の checkfirst により**既存テーブルは作り直さず／変更せず**、未作成テーブルのみ作成します。ALTER TABLE やマイグレーションは行いません。加えて、現行モデルのスキーマは既存 `reservations.db`（rooms/reservations の各列）と一致しており（`series_id` 等の新列もない）、旧スキーマとの差分自体が生じません。したがって初回・2回目とも DB に実質的な変化はありません。根拠: `app/db/database.py:35-40`、`app/db/models.py`、既存 `reservations.db` のスキーマ確認結果。

Q16. **手順**: `pip install -r requirements.txt` 後、リポジトリ直下で `pytest`。**現状パスするのは7件のみです（全部は通りません）。** `tests/test_overlaps.py` の7テストは全て pass しますが、他3ファイル（`test_rooms_api.py`・`test_reservations_api.py`・`test_availability_api.py`、テスト関数計27）は Q14 の `brown` import エラーで collection 自体に失敗します。したがって「全件パスするはず」という状態にはなく、7 passed / 3 errors です。根拠: `pytest` 実行結果、`tests/test_overlaps.py`、`README.md`（テスト節）。

Q17. **分からない（`count` パラメータ・上限検出は存在しません）。** 予約作成に `count` フィールドはなく、回数上限を検出するロジックもありません。`count=100` を「どこで検出するか」を答える根拠がありません。根拠: `app/reservations/schemas.py`、`app/reservations/service.py`。

Q18. **タイムゾーン変換は行われていません（どのレイヤでも実施なし）。** 時刻はナイーブ `datetime`（ローカル）として扱う設計で、`timezone`/`tzinfo`/`astimezone`/`utcnow`/`zoneinfo` の使用は `app/` 全体で1件もありません。比較・保存はナイーブ datetime のままです。根拠: `app/db/models.py:4`（「時刻はナイーブ datetime（ローカル）」）、`grep -rniE "timezone|tzinfo|astimezone|utcnow|zoneinfo"` の結果（該当なし）、`app/reservations/service.py:41`（`datetime.now()`）。

Q19. **分からない（隔週・月次の定期予約機能は存在しません）。** frequency/weekly/biweekly/monthly 等のパラメータや定期予約エンドポイントがこのリポジトリにないため、指定方法を答える根拠がありません。根拠: `app/reservations/schemas.py`、`app/` 全体の検索結果。

Q20. **設定箇所はありません（認証機能自体が未実装）。** 認証トークンやその有効期限を設定する箇所は存在せず、`auth`/`token`/`jwt`/`bearer`/`expire` は `app/` 全体で1件もヒットしません。`README.md` も認証・権限を「スコープ外」としています。よってトークン有効期限の設定場所は存在せず、分かりません。根拠: `grep -rniE "auth|token|jwt|bearer|expire" app/`（該当なし）、`README.md`（設計上の割り切り）。
