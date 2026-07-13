調査が完了しました。重要な前提として、**この cond-B リポジトリには「定期予約（recurring reservations）機能」が実装されていません**。要件定義で明示的にスコープ外とされています（`aidlc-docs/inception/requirements/requirements.md:31,85` に「定期予約（繰り返し予約） — Q2=A により今回は実装しない」「割り切り: …定期予約…は今回スコープ外」）。`app/` 配下に `series/` モジュールや `recurrence.py` は存在せず、コード検索でも `series`/`recur`/`weekly`/`until` の実装は 0 件でした。

そのため、定期予約の設計判断を問う質問群（Q1〜Q6, Q8, Q9, Q11, Q12, Q17, Q19 など）は、このリポジトリからは根拠が得られません。以下、番号順に回答します。

---

Q1. 分からない。定期予約機能そのものが cond-B に実装されていないため、「重複回のスキップ／シリーズ全体409」といった仕様も存在せず、その選択理由を裏付ける根拠がリポジトリにありません。単発予約の重複時挙動としては 409 を返すのみです（`app/reservations/service.py` BR-C5、`app/common/errors.py`）。

Q2. 分からない。シリーズの回数上限（52回など）に関する定数・ロジックはリポジトリに存在しません（`app/` 全体を検索しても該当なし）。

Q3. 分からない（シリーズ機能自体が無いため専用APIも存在しません）。なお、通常の（単発）予約のキャンセルは `POST /reservations/{reservation_id}/cancel` で行えます（`app/reservations/router.py:51`、`app/reservations/service.py` の `cancel_reservation`、冪等）。

Q4. 分からない。`app/series/recurrence.py` は存在しません。参考までに、純粋関数として分離されているのは重複判定の `overlaps()` で、これは `app/availability/service.py` にモジュール関数として定義されています（テストしやすさのため）。ただしこれは週次日付生成とは無関係です。

Q5. 分からない。`series_id` 列や、そのための SQL 直書きヘルパは存在しません。cond-B はマイグレーションツールを使わず、`app/db/database.py` の `create_all()`（`Base.metadata.create_all`）で起動時にテーブルを作成する方式です。列追加のようなスキーマ変更処理は実装されていません。

Q6. リポジトリの前提が異なります。`hypothesis` は依存に**追加されていません**（`requirements.txt` は fastapi / uvicorn[standard] / sqlalchemy>=2.0 / pydantic>=2.0 / pytest / httpx のみ）。したがって Property-Based Testing も導入されていません。目的や適用範囲の根拠はありません。

Q7. **共存できます。** 重複判定は半開区間 `[start, end)` で行われ、`overlaps()` は `start_a < end_b and start_b < end_a` を用いるため、隣接（一方の `end == 他方の start`、例: 10:00終了と10:00開始）は「重ならない」と判定されます（`app/availability/service.py` の `overlaps()` とその docstring「隣接（end_a == start_b など）は重ならない扱い」）。

Q8. 分からない。`until` パラメータや定期予約の日付生成対象判定は実装されていないため、境界（inclusive/exclusive）を判断する根拠がありません。

Q9. 分からない。`count` / `until` パラメータは存在しません（予約作成スキーマは `app/reservations/schemas.py` の `ReservationCreate` = room_id / start_time / end_time / booker_name / booker_email のみ）。

Q10. **作成できます（許可されています）。** `app/reservations/service.py` の BR-C4 で `if start_time < datetime.now(): raise ValidationError(...)` となっており、コメントにも「過去日時の予約は拒否（start == now は許可）」と明記されています。等しい場合は拒否されません。

Q11. 分からない。シリーズ全体キャンセル機能は存在しません。単発予約のキャンセルについてのみ根拠があり、(b)(c)に相当する挙動として、既に `cancelled` の予約に対する再キャンセルは状態を変えず冪等に成功します（`app/reservations/service.py` の `cancel_reservation`、BR-X3）。(a) 過去に開始済みの回に対する扱いは、そもそもシリーズが無いため根拠なし。

Q12. 変更はありません（正確には、定期予約機能自体が cond-B では追加されていないため）。単発予約APIの契約は `app/reservations/schemas.py`（`ReservationCreate` / `ReservationOut`）と `app/reservations/router.py` のとおりで、`series_id` 等の追加フィールドはありません。

Q13. **DBレベルの制約では実現されていません。** モデル（`app/db/models.py`）に重複を禁じる UNIQUE 制約や排他制約はなく、インデックス `ix_reservations_room_id_status` は検索効率化のためのものです。防止はアプリ層で、`AvailabilityService.has_conflict`（`app/availability/service.py`）が対象会議室の active 予約を走査して判定 → `service.py` で挿入、という「チェックしてから挿入」方式です。ロックや DB制約が無いため、**並行リクエストが同時に来ると二重予約は起こりえます**（チェックと挿入の間に競合する余地があるレースコンディション）。

Q14. リポジトリの前提と実態が食い違っています。確かに `tests/test_rooms_api.py` / `test_reservations_api.py` / `test_availability_api.py` は `from brown.tests.conftest import create_room` でインポートしていますが、cond-B には `brown` パッケージが存在しません。そのため**これらのテストは実際には動きません**（`ModuleNotFoundError: No module named 'brown'` で収集時にエラー）。実際の共通フィクスチャ・ヘルパは `tests/conftest.py` にあり、この import パスと不整合です。「この規約に合わせた理由」の根拠はリポジトリにありません（おそらく別ディレクトリ構成（`brown-field/`）を前提としたコードが移植された際の不整合と見られますが、確証はありません）。

Q15. 既存の `reservations.db` があっても、cond-B にはスキーマ変更が無いため問題は起きません。起動時 `create_all()`（`app/db/database.py`）は `Base.metadata.create_all` で「未作成のテーブルのみ作成」する動作で、既存テーブルの ALTER や再作成は行いません。既存 `rooms`/`reservations` テーブルはそのまま使われ、2回起動しても create_all は冪等なので何も変わりません。（「旧スキーマに series_id を追加」というマイグレーション処理は存在しません。）

Q16. 手順: リポジトリ直下で（依存を入れた上で）`pytest` を実行します（`README.md`「テスト」節）。ただし現状**全件はパスしません**。上記 Q14 の理由で API テスト3モジュール（test_rooms_api / test_reservations_api / test_availability_api）は収集エラーになり、正常に収集・パスするのは `tests/test_overlaps.py` の **7件のみ**です（実行結果: `7 passed`、`3 errors in collection`）。`brown` パッケージ相当の解決を行えばより多く通る想定ですが、現状のリポジトリ状態では 7 件です。

Q17. 分からない。`count` パラメータや回数上限（例: 100 vs 52）の検出ロジックは実装されていません。

Q18. タイムゾーン変換は**どのレイヤでも行われていません**。`app/db/models.py` の冒頭 docstring に「時刻はナイーブ datetime（ローカル）」と明記され、`start_time`/`end_time` は `DateTime`（timezone なし）で保持されます。サービス層でも `datetime.now()`（naive）を使用（`app/reservations/service.py`）しており、`astimezone`/`utc`/`tzinfo` 等の変換コードは存在しません。

Q19. 分からない。隔週・月次を指定するパラメータ（frequency / interval など）は予約作成スキーマ（`app/reservations/schemas.py`）に存在せず、定期予約自体が未実装です。

Q20. 分からない（該当する設定が存在しません）。認証機構自体が実装されておらず、`token`/`auth`/`jwt`/`bearer` 等のコードはリポジトリに見当たりません。要件でも認証はスコープ外です（`aidlc-docs/inception/requirements/requirements.md:85`）。したがって認証トークンの有効期限を設定している箇所はありません。
