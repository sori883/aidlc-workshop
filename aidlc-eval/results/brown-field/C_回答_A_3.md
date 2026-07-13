調査完了です。cond-A リポジトリ内の実装・コメント・README・テストのみを根拠に回答します。なお、コードが参照している設計ドキュメント（`business-rules.md` 等）は本リポジトリ（cond-A）内には存在せず、docstring からの参照のみである点を前提とします。

---

Q1. 生成された各回のうち1回でも既存予約と重複すると、シリーズ全体を 409 で拒否します（部分成功させない）。実装は `app/series/service.py:78-81` で、全 occurrence をループして `has_conflict` が1つでも真なら `ConflictError` を投げ、この判定は予約登録より前に行われるため回は1件も作られません。コメントには「BR-RS-OV1/OV2: 1回でも重複すればシリーズ全体を拒否（原子性）」とあり、根拠となる設計思想は「原子性（all-or-nothing）」です（`tests/test_recurring_api.py:68-89` の `test_conflict_rejects_whole_series_atomically` が原子性を検証）。ただし「重複回だけスキップする案を検討して却下した経緯」を記した設計ドキュメントは本リポジトリ内に存在しない（`business-rules.md` は参照のみで未収録）ため、"原子性を優先した"という結論以上の詳細な選定経緯は分からない。

Q2. 上限52回は `app/series/service.py:22` の `MAX_OCCURRENCES = 52` と `app/series/recurrence.py:18` の `max_count: int = 52` で定義されています。ただし「なぜ52なのか」という明示的な理由はコード・コメント・README のいずれにも記載がなく、本リポジトリからは根拠が見つからないため、正確な理由は分からない（52は週次で約1年分に相当しますが、これが意図だと断定できる記述はありません）。

Q3. 定期予約の各回は通常の `Reservation` レコードとして展開され、それぞれ独自の予約IDと `series_id` を持つため（`app/series/service.py:106-118`）、個別回のキャンセルは既存の単発予約用API `POST /reservations/{reservation_id}/cancel` をそのまま流用します。専用APIが無いのはこの流用で用が足りるためで、`tests/test_recurring_api.py:161-173`（`test_individual_occurrence_cancel_via_existing_api`、コメント「既存の個別キャンセル API を流用（US-R05）」）が、対象回だけ cancelled になり他の回は active のまま残ることを検証しています。

Q4. `app/series/recurrence.py:1-5` の docstring に「副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想。」と明記されています。すなわち、日付生成ロジックをDBや副作用から切り離して純粋関数にすることで、単体テストおよび Property-Based Testing（`tests/test_recurring_pbt.py` が `generate_occurrences` を直接検証）が容易になるためです。既存の重複判定 `overlaps`（`app/availability/service.py:14`）と同じ設計方針に揃えています。

Q5. `app/db/database.py:36-52` の `_ensure_series_id_column` が、`inspect` で既存 `reservations` テーブルに `series_id` 列が無ければ `ALTER TABLE ... ADD COLUMN` を実行します（冪等）。コメントの根拠は「`Base.metadata.create_all` は未作成テーブルしか作らず、既存テーブルへの列追加は行わないため」で、起動時に不足列を補う目的です。ただし「なぜ Alembic 等のマイグレーションツールを使わなかったか」を明示した記述は本リポジトリ内に無く、`requirements.txt` にもマイグレーションツールは含まれていません（起動時 `create_all` に依存する軽量構成）。ツールを選ばなかった明示的な理由・経緯は分からない。

Q6. `hypothesis` は Property-Based Testing のために追加されており（`requirements.txt`）、`tests/test_recurring_pbt.py` で `generate_occurrences`（純粋関数）とスキーマの往復（round-trip）・不変条件（invariant）・境界を検証しています。一部のテストにしか適用されていない理由は、同ファイル docstring（`tests/test_recurring_pbt.py:6`）に「純粋関数・スキーマが対象のため DB 非依存」とある通り、PBTが向く純粋関数／スキーマだけを対象にしているためです。

Q7. 共存できます。重複判定は半開区間 `[start, end)` で行われ（`app/availability/service.py:14-19` の `overlaps` は `start_a < end_b and start_b < end_a`）、隣接（`end == start`）は重ならない扱いになります。したがって「10:00終了の予約」と「10:00開始の予約」は重複せず両立します（README:9「隣接はOK、重なりは 409」）。

Q8. 含まれます。`until` は inclusive で、`app/series/recurrence.py:48` の判定は `if occ_start.date() > until: break` であり、開始日が `until` と等しい回（2030-01-15開始）はスキップされず生成対象になります（`tests/test_recurring_api.py:50-56` が inclusive を検証）。

Q9. 両方指定すると 400（ValidationError）になります（`app/series/service.py:50-53` の BR-RS-C4、`(count is None) == (until is None)` が真＝両方指定または両方未指定で拒否。`tests/test_recurring_api.py:92-98`）。両方省略した場合も同じ条件で 400 になります（`tests/test_recurring_api.py:101-105`）。どちらか一方のみ指定が必須です。

Q10. 作成できます。過去日時チェックは `start_time < datetime.now()` の厳密な小なり比較で、`start_time == now` は拒否されません（単発は `app/reservations/service.py:41-42` のBR-C4、定期は `app/series/service.py:72-73` のBR-RS-C8、コメント「start == now は許可」）。ただし実時刻は進むため、境界がちょうど一致するのは実質的に瞬間的なケースです。

Q11. `app/series/service.py:130-141`（`cancel_series`）と `app/reservations/repository.py:60-72`（`list_future_active_by_series`：`start_time > now` かつ `status == active`）に基づきます。(a) 過去に開始済みの回：`start_time > now` を満たさないためキャンセルされず、状態は据え置き（active のまま）。(b) 既にキャンセル済みの回：`status == active` の条件から外れるため対象外（cancelled のまま）。(c) もう一度実行すると：未来の active 回が無ければ何も変更せず 200 を返す冪等動作（`tests/test_recurring_api.py:147-154` の `test_cancel_series_idempotent`）。

Q12. リクエスト契約（`ReservationCreate`, `app/reservations/schemas.py:9-14`）に変更はありません。レスポンス契約（`ReservationOut`, 同:17-29）には `series_id: str | None = None` フィールドが追加されました（単発予約は None、シリーズの各回はシリーズID）。すなわち既存フィールドは不変で、新フィールドを追加した後方互換的（additive）な変更です（`tests/test_recurring_api.py:200-213` が単発の `series_id` が null であることを検証）。

Q13. データベースレベルの制約では実現されていません。`app/db/models.py:111-112` の `Index("ix_reservations_room_id_status", ...)` は性能用の複合インデックスであり、ユニーク制約や排他制約ではありません。ダブルブッキング防止はアプリ層の `AvailabilityService.has_conflict`（`app/availability/service.py:28-46`）で active 予約を走査して判定しています。チェックと挿入の間にロックが無い（read-check-insert）ため、並行リクエストが同時に来た場合は二重予約が起こりえます。

Q14. ルートの `conftest.py:19-24` が、`brown` という名前のモジュールをこのプロジェクトディレクトリへのパッケージエイリアスとして `sys.modules` に登録し、`__path__` を本ディレクトリに向けることで、`from brown.tests.conftest import create_room` を `tests/conftest.py` に解決させているためです。同 docstring（`conftest.py:1-8`）に「既存テストのソースは一切変更せず、この規約を成立させるための追加設定」とあり、既存テストが従っている `brown.tests.conftest` という規約に合わせるため（テストソースを書き換えずに動かすため）にエイリアスを用意した、というのが根拠です。

Q15. 起動時に `create_all`（`app/db/database.py:54-62`）が呼ばれ、その中で `_ensure_series_id_column` が既存 `reservations` テーブルを検査し、`series_id` 列が無ければ `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を実行します。続く `Base.metadata.create_all` が未作成の `reservation_series` テーブルを作成します。既存データは保持されたまま列とテーブルが追加されます。2回目の起動では列がすでに存在するため列追加はスキップされ（冪等）、テーブル作成も未作成分のみなので、DBに追加の変更は起きません。

Q16. 手順：(1) 仮想環境作成・有効化 `python -m venv .venv && source .venv/bin/activate`、(2) 依存インストール `pip install -r requirements.txt`、(3) リポジトリルートで `pytest` を実行（README:60-64）。ルートの `conftest.py` が `app` と `brown` の import 解決を行うため、ルートから実行します。実際に実行したところ **66件** がパスします（`pytest --collect-only` でも66件収集、`66 passed`）。

Q17. Pydantic スキーマ（`app/series/schemas.py:18-20`）は `count` に `ge=1` のみで上限を持たないため、`count=100` は 422 では弾かれません。`generate_occurrences`（`app/series/recurrence.py:36-40`）は `len(occurrences) > max_count(=52)` になった時点で生成を打ち切り、最大53件を返します。その値をサービス層 `create_series`（`app/series/service.py:67-70`、BR-RS-C7）が `len(occurrences) > MAX_OCCURRENCES(=52)` で検出し、`ValidationError` → 400 を返します。つまり上限超過はサービス層で検出されます（`tests/test_recurring_api.py:108-112` が `count=53` で 400 を検証）。

Q18. どのレイヤでもタイムゾーン変換は行われていません。`app/db/models.py:3` に「時刻はナイーブ datetime（ローカル）」とあり、`DateTime`（tz非対応）でナイーブな datetime を保存・比較しています。README:83 でもタイムゾーンは「スコープ外」と明記されています。したがってTZ変換レイヤは存在しません。

Q19. 指定できません。本システムは週次（7日刻み、`app/series/recurrence.py:10` の `WEEK = timedelta(days=7)`）のみを提供し、隔週・月次を指定するパラメータは存在しません（`RecurringReservationCreate` に間隔指定フィールドは無い、`app/series/schemas.py:11-23`）。README:83 でも「隔週・月次などの複雑な繰り返し」は「スコープ外」と明記されています。

Q20. 認証機能自体が実装されておらず、トークンやその有効期限を設定する箇所は存在しません（`app/core/config.py` は `database_url`/`host`/`port` のみ、`app/` 全体を検索しても `token`/`auth`/`expire` 等のヒットは0件）。README:83 でも「認証・権限」は「スコープ外」と明記されています。よって認証トークンの有効期限を設定する場所はこのリポジトリには存在しない。
