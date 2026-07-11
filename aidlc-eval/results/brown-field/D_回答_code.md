調査が完了しました。このディレクトリ（`cond-D-none`）に実在する記録・ファイルは **README.md、ソースコード（app/）、テスト（tests/）、および各種キャッシュ（.pytest_cache/.coverage）のみ** です。設計・意思決定・監査・デプロイ等のプロセス記録（`aidlc-docs/` 配下の `business-rules.md`・`audit.md`・`aidlc-state.md` 等）は **このディレクトリには存在しません**。コード内コメントはそれらの文書（`business-rules.md` の BR-RS-*、`US-R*`、PBT モード等）を参照していますが、参照先の実体は本ディレクトリに含まれていないため、その内容は根拠として使えません。この前提で17問に回答します。

---

**Q1.** スコープ外機能は README.md「## 設計上の割り切り（今回のスコープ外）」（L82-83）に明記：*隔週・月次などの複雑な繰り返し / 認証・権限 / キャンセルポリシー（時間制約）/ 営業時間制約 / タイムゾーン / フロントエンド*。ただし「どこで（どの意思決定プロセスで）誰が決めたか」は README に**結果として列挙されているのみ**で、決定の経緯・主体の記録はこのディレクトリには**記録なし**。

**Q2.** 「全工程を実施する」という進め方を誰がいつ判断したか — **記録なし**。計画・進め方に関する記録（aidlc-state 等）はこのディレクトリに存在しません。

**Q3.** 定期予約要件で当初未確定だった事項と確定経緯 — **記録なし**。要件定義書・意思決定ログはこのディレクトリに存在しません。コード（`app/series/recurrence.py` L3、`app/series/service.py` 各所）は確定ルールとして `business-rules.md` の BR-RS-* を参照していますが、その `business-rules.md` 本体が本ディレクトリに不在のため、未確定事項の内容も確定過程も辿れません。

**Q4.** 完成判定（リリース可能）の根拠 — **記録なし**。リリース可否のチェックリスト・サインオフ記録はありません。存在するのはテスト群（`tests/`）と `.pytest_cache/v/cache/lastfailed`（内容は `{}`＝直近の失敗なし）のみで、これはテスト実行の痕跡ではあってもリリース判断の根拠記録ではありません。

**Q5.** 新規外部依存 — `requirements.txt` に PBT 用の `hypothesis` が記載され、`tests/test_recurring_pbt.py` L11-12 で使用。ただし定期予約コミット `878f9bd` の `requirements.txt` 差分は**空**（＝このコミットでは依存ファイルに変更なし＝hypothesis はそれ以前から存在）。いずれにせよ**追加の承認記録は記録なし**。

**Q6.** 既存DBスキーマ変更の方式は `app/db/database.py` の `_ensure_series_id_column()`：既存 `reservations` テーブルへ `ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)` を冪等に実行する**追記型マイグレーション**。加えて新規テーブル `reservation_series` を `create_all` で作成（`app/db/models.py` L55-82）。単発予約は `series_id=NULL`（models.py L100-103）で後方互換。**その方式を誰が承認したかの記録は記録なし**。

**Q7.** 認証・認可の未実装は、README.md L83 で「認証・権限」をスコープ外として明記しているため**意図的**と読み取れます。ただし**誰の判断かは記録なし**。

**Q8.** 既存機能の非破壊は、既存機能のテスト（`tests/test_rooms_api.py`, `test_reservations_api.py`, `test_availability_api.py`, `test_overlaps.py`）の存在、`.pytest_cache/.../lastfailed`＝`{}`（直近失敗なし）、およびスキーマ変更が追記のみ（`app/db/database.py`、単発予約 `series_id=NULL`）である点から**構造的には裏付けられます**。ただし「回帰試験を実施し非破壊を確認した」旨の**明示的な確認記録・レポートは記録なし**。

**Q9.** 「1回でも重複すると全体409」の理由は、`app/series/service.py` L78-81 のコメント「BR-RS-OV1/OV2: 1回でも重複すればシリーズ全体を拒否（**原子性**）」および README.md L41。すなわち根拠は「シリーズ作成の原子性」。ただし「重複回だけスキップして作成」案を検討・却下した**意思決定記録は記録なし**（根拠元の `business-rules.md` は本ディレクトリに不在）。

**Q10.** 52回上限の根拠 — 値そのものは `app/series/service.py` L22 `MAX_OCCURRENCES = 52`、`app/series/recurrence.py` L18 `max_count: int = 52`、README.md L41/L83 に定義。**しかし「なぜ52か」という数値選定の根拠・理由の記録は記録なし**。

**Q11.** シリーズ内個別回のキャンセルに新規APIを作らなかった件 — 各回は独立した `Reservation` 行として生成される（`app/series/service.py` L106-118、`app/db/models.py`）ため、既存の `POST /reservations/{reservation_id}/cancel`（README.md L40）で個別キャンセル可能、という構造はコードから読み取れます。ただし「新規APIを作らないと判断した理由」自体の**記録は記録なし**。

**Q12.** `app/series` を独立モジュールにした理由は、`app/series/recurrence.py` の docstring（L1-5）「副作用なし・DB非依存でテスト/PBTが容易。overlaps と同じ設計思想」に、純粋関数を分離する設計思想として記載。ただしモジュール構成の設計判断を記した設計ドキュメントは本ディレクトリに不在で、**根拠はコードコメント上の設計思想に留まります**（それ以上の設計判断記録は記録なし）。

**Q13.** PBTの適用範囲は `tests/test_recurring_pbt.py` docstring（L1-6）に記載：「**PBT Partial モード**で強制対象の PBT-02（Round-trip）/03（Invariant）/07（Generator quality）/08 に対応。**純粋関数・スキーマが対象のため DB 非依存**」。対象は `generate_occurrences`（純粋関数）と `RecurringReservationCreate`（スキーマ）。全面適用でない理由は「Partial モード」かつ「純粋関数・スキーマが対象（DB非依存）」と明記されていますが、**その「Partial モード」を選択した意思決定の背景文書はこのディレクトリに不在**（モード選択の理由は記録なし）。

**Q14.** `until` 指定の終了日**当日**に開始する回は生成対象に**含まれます（inclusive）**。根拠：`app/series/recurrence.py` L42-49（`if occ_start.date() > until: break` ＝当日 `==until` は含む）、`app/series/schemas.py` L21-23（`until` 説明「この日以前の開始回まで、inclusive」）、README.md L79「終了日指定（inclusive）」。仕様は README・スキーマ・コードで inclusive と確定・一致。なお正式仕様書（`recurrence.py` L3 が参照する `business-rules.md` の BR-RS-G*）は本ディレクトリには不在です。

**Q15.** テストパスの内訳記録は限定的：`.pytest_cache/v/cache/nodeids`（収集済みテストID一覧）、`.pytest_cache/v/cache/lastfailed`＝`{}`（直近失敗なし）、`.coverage`（カバレッジDB）が存在。ただし「何件成功／合否サマリ」といった**明示的なテスト結果レポートは記録なし**。再現手順は**残っています**：README.md「## テスト」の `pytest`、`requirements.txt`（依存）、`conftest.py`／`tests/conftest.py`、`.venv`。

**Q16.** 本番デプロイの実施時期・承認者 — **記録なし**。デプロイ記録・承認記録・インフラ/デプロイ関連ドキュメントはこのディレクトリに存在しません。

**Q17.** 過去の本番障害と対応記録 — **記録なし**。障害・インシデントに関する記録はこのディレクトリに存在しません。

---

補足（説明責任の観点）：本ディレクトリのコード・テストは `business-rules.md`（BR-RS-*）、`US-R*`、PBT モード定義、`audit.md` 等の**上流ドキュメントを前提に参照**していますが、それらの実体が `cond-D-none` に含まれていないため、Q2〜Q4・Q7（判断主体）・Q9〜Q11・Q16・Q17 など**ガバナンス／意思決定に関わる問いの多くが「記録なし」**となります。これらの根拠が必要な場合、参照元の設計・監査ドキュメント一式を本ディレクトリに同梱する必要があります。
