すべての根拠を確認しました。以下、17問に番号順で回答します。

---

**Q1. スコープ外機能とその決定場所**
意図的にスコープ外とされたのは、①隔週・月次などの複雑な繰り返しルール、②認証・権限、キャンセルポリシー、営業時間制約、③タイムゾーン対応です。決定場所は `docs/writing-inputs/brownfield-vision.md`「Out of Scope（スコープ外）」セクション。これは `aidlc-docs/inception/requirements/requirements.md`「Non-Functional Requirements / NFR-5（スコープ外）」でも踏襲・確認されています。

**Q2. 「全工程を実施する」判断の主体と時期**
ステークホルダー（ユーザー）本人が、Requirements Analysis 承認の時点で下しました。根拠は `aidlc-docs/audit.md`「Requirements Analysis Approval」（Timestamp: 2026-07-10T01:19:57Z）で、ユーザー入力は「ワークショップなので、全ての工程を行いたいです。」。`aidlc-docs/aidlc-state.md`「Project Information / Execution Policy」にも「ワークショップ目的のため全ステージを実施」と記録されています。

**Q3. 定期予約要件で当初未確定だった事項と確定内容**
`docs/writing-inputs/brownfield-vision.md`「Open Questions（未確定事項）」に2点あります。①シリーズの一部が重複する場合、全体拒否かスキップ作成か → **全体拒否**（1回でも重複ならシリーズ全体を409）に確定。②シリーズは新テーブルか reservations への列追加か → **新テーブル `reservation_series` + `reservations.series_id`（NULL可）列追加**に確定。確定経緯は `aidlc-docs/inception/requirements/requirement-verification-questions.md` 冒頭「回答済み（2026-07-10、対話形式で取得）」の Q1・Q2（および `aidlc-docs/audit.md`「Requirements Analysis - Answers Received」でAskUserQuestionにより取得）です。

**Q4. 完成判定（リリース可能）の根拠**
`aidlc-docs/construction/build-and-test/build-and-test-summary.md`「Overall Status」で「All Tests: Pass（66/66）」「Ready for Operations: Yes」とされ、同「制約遵守（C-1〜C-4）」で全制約充足（✅）が示されています。加えて `aidlc-docs/audit.md`「Build and Test - Approval Response / Workflow Completion」でユーザーが「承認」し全工程完了と記録。ただし記録上の判定は**テストパス＋制約充足＋ユーザー承認**であり、本番リリースそのものの判定記録ではありません（Q16参照）。

**Q5. 新規外部依存の追加と承認記録**
はい、テスト用ライブラリ **Hypothesis** が `requirements.txt` に追加されています（`aidlc-docs/construction/recurring-reservations/infrastructure-design/deployment-architecture.md`「構成要素」、`aidlc-docs/audit.md`「Code Generation - Part 2 Generation」の requirements.txt（hypothesis））。承認記録は `aidlc-docs/audit.md`「NFR Requirements」（ユーザー回答「PBTフレームワーク=Hypothesis 追加」）とその直後「NFR Requirements - Approval Response」の「承認」です。詳細判断は `aidlc-docs/construction/recurring-reservations/nfr-requirements/tech-stack-decisions.md`（既存継承＋Hypothesis追加）。

**Q6. 既存DBスキーマ変更の方式と承認者**
方式は「既存の `create_all()` を拡張し、`reservation_series` テーブル作成＋`reservations.series_id` 列を**冪等な自動ALTERヘルパ**（`_ensure_series_id_column`、SQLite PRAGMA判定）で追加」する方式です（`aidlc-docs/construction/recurring-reservations/infrastructure-design/deployment-architecture.md`「起動シーケンス」、`aidlc-docs/audit.md`「Infrastructure Design」）。この方式は Infrastructure Design ステージでユーザーが選択・承認しました（`aidlc-docs/audit.md`「Infrastructure Design」ユーザー回答「既存DBへのスキーマ反映=軽量な自動ALTERヘルパ」→「Infrastructure Design - Approval Response」の「承認」）。

**Q7. 認証・認可の未実装は意図的か、誰の判断か**
意図的です。Security Baseline 拡張を「No（適用しない）」とする判断が、Requirements Analysis 段階でユーザー（ステークホルダー）により下されました。根拠は `aidlc-docs/aidlc-state.md`「Extension Configuration」（Security Baseline = No, Decided At: Requirements Analysis）、`aidlc-docs/inception/requirements/requirement-verification-questions.md` Q11（Security 拡張: No）。また `docs/writing-inputs/brownfield-vision.md`「Out of Scope」でも認証・権限はスコープ外と明記。

**Q8. 既存機能を壊していないことの保証方法**
`aidlc-docs/construction/build-and-test/build-and-test-summary.md`「制約遵守（C-1〜C-4）」に記録があります。①既存テスト34件を未改変で全パス（C-4、回帰なし）、②`ReservationCreate` 不変・単発API契約不変をE2Eで確認（単発 series_id=null、C-1）、③`availability.service`/`overlaps` を未変更で再利用（C-2）、④HTTPステータス方針踏襲（C-3）。加えて `aidlc-docs/audit.md`「Build and Test Stage」に既存 `reservations.db` コピーへのマイグレーション検証・E2Eスモークの記録があります。

**Q9. 1回でも重複すると全体が409拒否になる理由（スキップ作成ではだめだったか）**
原子性（全成功または全ロールバック）を優先する要件だからです。`aidlc-docs/inception/requirements/requirements.md` FR-1.6、`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md` BR-RS-OV2 に「1回でも重複したら409、series と全回を一切登録しない（単一トランザクションでロールバック）」と定義。「重複回だけスキップして作成」（選択肢B）も提示されましたが、ステークホルダーが選択肢A（全体拒否）を選んだためです（`aidlc-docs/inception/requirements/requirement-verification-questions.md` Question 1 の A/B/C 選択肢と回答「全体拒否」）。

**Q10. シリーズ回数上限52回の根拠**
「最大52回=約1年」という設計意図に基づきます。根拠は `aidlc-docs/inception/requirements/requirement-verification-questions.md` Question 4「上限を設ける（推奨。例: 最大52回=約1年。超過時は 400）」（回答: 上限あり52）。要件は `aidlc-docs/inception/requirements/requirements.md` FR-1.5、ルールは `business-rules.md` BR-RS-C7。

**Q11. 個別回キャンセルに新規APIを作らなかった理由**
シリーズの各回は `series_id` を持つ通常の予約行であり、既存の `POST /reservations/{reservation_id}/cancel` がそのまま機能する（冪等性・404挙動も既存踏襲）ためです。根拠は `aidlc-docs/inception/requirements/requirements.md` FR-3.1/FR-3.2、`business-rules.md` BR-RS-I1（「新規ルール・新規コードなし」）。決定は `requirement-verification-questions.md` Question 7 で選択肢A（既存流用）を選んだこと。

**Q12. 定期予約コードが独立した app/series モジュールになっている理由**
既存の縦割り（機能別モジュール）構成に一貫させるためです。`aidlc-docs/inception/application-design/application-design.md`「設計方針（承認済み決定）」に「配置: 新規 `app.series` モジュール（router/service/schemas/repository/recurrence）。既存の縦割り構成に一貫」と記載。この配置判断は Application Design 段階でユーザーが対話形式で回答（`aidlc-docs/audit.md`「Application Design」: 「コンポーネント配置=新規 app.series モジュール」）。

**Q13. Property-Based Testing の適用範囲と全面適用でない理由**
適用範囲は「純粋関数（日付生成 recurrence）とシリアライズ往復」に限定した Partial モードで、強制ルールは PBT-02/03/07/08/09 のみです（`aidlc-docs/aidlc-state.md`「Extension Configuration / Property-Based Testing 強制モード」、`build-and-test-summary.md`「PBT Compliance」）。全面適用でない理由は、ステークホルダーが `requirement-verification-questions.md` Question 13 で選択肢B「Partial — enforce PBT rules only for pure functions and serialization round-trips」を選択したためです。

**Q14. until指定の終了日当日に開始する回は生成対象に含まれるか、確定場所**
含まれます（inclusive）。`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md` BR-RS-C6「`until` は日付として扱い、各回の**開始日が until 以下**（inclusive）の回まで生成」、および `aidlc-docs/inception/requirements/requirements.md` FR-1.4「`until`: 起点から、開始日が `until` 以下となる回まで生成」。仕様確定は Functional Design 段階（`aidlc-docs/audit.md`「Functional Design」: 「until=開始日<=until(inclusive, date)」）。

**Q15. テストパス記録の内訳とテスト環境の再現手順**
内訳は記録あり。`aidlc-docs/construction/build-and-test/build-and-test-summary.md`「Unit Tests」で 66件（既存回帰34＋新規例示27〔recurrence 9＋recurring_api 18〕＋PBT 5）、「Integration Tests」4シナリオ、Performance/Security は N/A と記録。再現手順の記録も存在します：`aidlc-docs/construction/build-and-test/` 配下の `build-instructions.md` / `unit-test-instructions.md` / `integration-test-instructions.md` / `performance-test-instructions.md`。環境は venv＋依存インストール（hypothesis含む）、既存テスト規約 `brown.tests.conftest` を成立させるためリポジトリルートに `conftest.py`（brownエイリアス）を追加（`build-and-test-summary.md`「Next Steps」備考、`aidlc-docs/audit.md`「Build and Test Stage」）。

**Q16. 本番環境へのデプロイ時期と承認者**
記録なし。`aidlc-docs/aidlc-state.md`「OPERATIONS PHASE」は「Operations — PLACEHOLDER（今回スコープなし。ワークフローは Build and Test で終了）」、`aidlc-docs/audit.md`「Build and Test - Approval Response / Workflow Completion」も「Operations はプレースホルダ…AI-DLC ワークフローは Build and Test で終了」と記録。`deployment-architecture.md` はローカル（uvicorn＋SQLite）構成とロールバック方針の設計のみで、**実際の本番デプロイの実施日・承認者の記録はありません**。

**Q17. 過去の本番障害と対応記録**
記録なし。本ディレクトリ内に Operations／インシデント／本番障害に関する記録は存在せず、Operations フェーズは未着手のプレースホルダです（`aidlc-docs/aidlc-state.md`「OPERATIONS PHASE」、`aidlc-docs/audit.md` の最終エントリ）。
