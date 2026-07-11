必要な記録は揃いました。17問すべてに、ディレクトリ内の記録を根拠として回答します。

---

**Q1.** 意図的にスコープ外とした機能は次の通りです。①隔週・月次などの複雑な繰り返しルール、②認証・権限、③キャンセルポリシー、④営業時間制約、⑤タイムゾーン対応。決定箇所は `docs/writing-inputs/brownfield-vision.md`（"Out of Scope（スコープ外）" セクション）で、要件にも `aidlc-docs/inception/requirements/requirements.md`（NFR-5）として明記されています。

**Q2.** ユーザーが2026-07-10、Requirements Analysis 承認時に「ワークショップなので、全ての工程を行いたいです。」と発言して判断しました。根拠は `aidlc-docs/audit.md`（"Requirements Analysis Approval" セクション、User Input）および `aidlc-docs/aidlc-state.md`（"Execution Policy: ワークショップ目的のため全ステージを実施"）。

**Q3.** 当初未確定だった事項と確定内容は以下です。根拠は `docs/writing-inputs/brownfield-vision.md`（"Open Questions"）と、その回答記録 `aidlc-docs/inception/requirements/requirement-verification-questions.md`（"回答済み（2026-07-10、対話形式で取得）"）。
- 一部の回が重複する場合の扱い → **全体拒否**（1回でも重複ならシリーズ全体を409）(Q1)
- シリーズを新テーブルか列追加か → **新テーブル `reservation_series` + `reservations.series_id`（NULL可）列追加**(Q2)

なお、この2つ以外にも終了指定方式(count/until両方)、回数上限(52)、API形、キャンセル範囲、表示方式、拡張オプトイン等が同ファイルQ3〜Q13で確定しています。

**Q4.** `aidlc-docs/construction/build-and-test/build-and-test-summary.md` と `aidlc-docs/audit.md`（"Build and Test Stage"）に記録された、テスト全66件パス（既存回帰34+新規例示27+PBT5）、統合テスト4シナリオ、E2Eスモーク、既存DBマイグレーション検証、制約C-1〜C-4遵守を根拠にしています。build-and-test-summary.md には "Ready for Operations: Yes" と記載。ただし、本番リリース（デプロイ）そのものの実施記録はありません（Q16参照）。

**Q5.** はい、**Hypothesis**（PBTフレームワーク）が新規追加されました。承認記録としては、`aidlc-docs/audit.md`（"NFR Requirements"）でユーザーが対話形式で「PBT フレームワーク=Hypothesis 追加」と回答し、後続の各ステージ（NFR Requirements承認、Code Generation承認等）で承認済みです。詳細は `aidlc-docs/construction/recurring-reservations/nfr-requirements/tech-stack-decisions.md`（"依存関係の変更"、既存方針に合わせバージョン未固定）。

**Q6.** 方式は「軽量な自動ALTERヘルパ」（既存 `create_all()` の拡張 + 冪等な `series_id` 列追加ヘルパ、SQLite PRAGMA で列存在判定）です。承認したのはユーザーで、`aidlc-docs/audit.md`（"Infrastructure Design"：ユーザーが対話形式で「既存DBへのスキーマ反映=軽量な自動ALTERヘルパ」と回答、および "Infrastructure Design - Approval Response" で「承認」）。詳細設計は `aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md`。

**Q7.** はい、意図的です。判断者はユーザーで、Requirements Analysis の拡張オプトイン Q11(Security)=No として下しました。根拠は `aidlc-docs/inception/requirements/requirement-verification-questions.md`（"Q11 Security 拡張: No"）、`aidlc-docs/aidlc-state.md`（"Extension Configuration" 表、Security Baseline=No, Decided At=Requirements Analysis）、`aidlc-docs/inception/requirements/requirements.md`（NFR-5でスコープ外明記）。

**Q8.** 「既存テストの改変不可・全パス維持」（制約C-4）を守り、既存回帰テスト34件を未改変で全パスさせることで保証しました。根拠は `aidlc-docs/construction/build-and-test/build-and-test-summary.md`（"既存（回帰）: 34（未改変・全パス）"、"制約遵守 C-4"）。加えて `ReservationOut` へのフィールド追加が既存テスト（個別フィールド検証方式）を壊さない設計であること（requirements.md FR-4.1）、単発API契約不変をE2Eで確認（build-and-test-summary.md C-1）。

**Q9.** 原子性（全成功または全ロールバック）を優先する要件だからです。ユーザーが Requirements Q1 で「全体拒否」を選択したことに基づきます。根拠は `aidlc-docs/inception/requirements/requirements.md`（FR-1.6、"1回でも…シリーズ全体を作成せず 409"）、`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md`（BR-RS-OV2）、`requirement-verification-questions.md`（Q1選択肢A「原子性を優先」、B「スキップ作成」は選ばれず）。「重複回だけスキップして作成」(選択肢B)はユーザーがA(全体拒否)を選んだため不採用となった、という以上の理由付けの記録はありません。

**Q10.** 記録上の根拠は「約52回=約1年」という目安のみです。`aidlc-docs/inception/requirements/requirement-verification-questions.md`（Q4選択肢A「最大52回=約1年。超過時は400」）でユーザーがこれを選択し確定。requirements.md FR-1.5、business-rules.md BR-RS-C7 に52回上限が反映されています。52という数値の定量的な追加根拠（それ以上の分析）は記録なし。

**Q11.** 各回は `series_id` を持つ通常の予約行であり、既存 `POST /reservations/{reservation_id}/cancel` がそのまま機能するためです。ユーザーが Requirements Q7 で「既存キャンセルAPI流用」を選択。根拠は `aidlc-docs/inception/requirements/requirements.md`（FR-3.1/FR-3.2）、`business-rules.md`（BR-RS-I1「新規ルール・新規コードなし」）、`requirement-verification-questions.md`（Q7=A）。

**Q12.** 「router/service/schemas/repository/recurrence の縦割り構成で既存モジュールと一貫させる」ためです。ユーザーが Application Design の対話で「新規 app.series モジュール」を選択しました。根拠は `aidlc-docs/inception/plans/application-design-plan.md`（"Q1: コンポーネント配置" の Answer）、`aidlc-docs/audit.md`（"Application Design"）。

**Q13.** 純粋関数（日付生成 `recurrence`／重複判定）とシリアライズ往復（schemas）に限定適用されています（強制ルールは PBT-02/03/07/08/09）。全面適用でない理由は、ユーザーが Requirements Q13 で「Partial — pure functions and serialization round-trips に限定」を選択したためです。根拠は `aidlc-docs/inception/requirements/requirement-verification-questions.md`（Q13=Partial）、`aidlc-docs/aidlc-state.md`（"Property-Based Testing 強制モード: Partial"）、`build-and-test-summary.md`（"PBT Compliance"）。選択そのものがユーザー判断で、Partial を選んだ定量的理由の追加記録はありません。

**Q14.** はい、含まれます（inclusive）。`until` は日付として扱い、各回の**開始日が until 以下**の回まで生成します。確定箇所は Functional Design で、`aidlc-docs/construction/recurring-reservations/functional-design/business-rules.md`（BR-RS-C6「開始日が until 以下（inclusive）」）、および `aidlc-docs/audit.md`（"Functional Design"：ユーザーが対話形式で「until=開始日<=until(inclusive, date)」と回答）。上位要件は requirements.md FR-1.4。

**Q15.** 内訳の記録はあります。`aidlc-docs/construction/build-and-test/build-and-test-summary.md` に「66/66 passed（既存回帰34 + 新規例示27〔recurrence 9 + recurring_api 18〕 + PBT 5）」、統合テスト4シナリオ、E2Eスモークが記載。再現手順は `aidlc-docs/construction/build-and-test/` 配下の `build-instructions.md` / `unit-test-instructions.md` / `integration-test-instructions.md` / `performance-test-instructions.md`（N/A）に残っています。環境はvenv+依存インストール（hypothesis含む）、既存テスト規約成立のためリポジトリルートに `conftest.py`（brownエイリアス）を追加（既存テスト未改変）と記録（build-and-test-summary.md "Next Steps"、audit.md "Build and Test Stage"）。ただし各instructions.mdの中身自体は今回未読のため、詳細手順の具体は該当ファイルを参照。

**Q16.** **記録なし。** AI-DLCワークフローは Build and Test で終了し、Operations フェーズはプレースホルダ（今回スコープ外）とされています。根拠は `aidlc-docs/aidlc-state.md`（"OPERATIONS PHASE … PLACEHOLDER（今回スコープなし）"）、`aidlc-docs/audit.md`（"Build and Test - Approval Response / Workflow Completion"）。本番デプロイの実施日・承認者の記録は存在しません。

**Q17.** **記録なし。** Operations フェーズがプレースホルダで本番運用に至っていないため、本ディレクトリ内に本番障害およびその対応記録は存在しません（`aidlc-docs/aidlc-state.md` "OPERATIONS PHASE"、`aidlc-docs/audit.md` ワークフロー完了記録より）。
