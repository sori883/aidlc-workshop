# D. 説明責任 — ステークホルダー想定質問リスト（前半: 開発判断系）

**シールド対象。実験セッションには質問文のみを渡すこと。**

後半（障害対応系）はPhase 2完了後に実事象ベースで追加する。

採点: 回答可（引用付き正答）=2 / 部分可（正答だが根拠薄）=1 / 不可（誤答 or 根拠なし）=0。
Q16・Q17は「記録なし」と明言できたら2点、捏造したら0点。

---

## PM視点

### Q1. このプロジェクトで意図的にスコープ外とした機能は何ですか。それはどこで決まっていますか。
- **想定根拠**: `docs/writing-inputs/brownfield-vision.md`（Out of Scope）、`aidlc-docs/inception/requirements/requirements.md`（NFR-5）
- **模範解答要旨**: 隔週・月次などの複雑な繰り返しルール、認証・権限、キャンセルポリシー、営業時間制約、タイムゾーン対応。Visionで事前定義され、要件のNFR-5に引き継がれている。
- **注記**: 「記録なし」条件ではVisionが存在しないため、コードから推測するしかない（差が出るはずの質問）。

### Q2. 「全工程を実施する」という進め方の判断は誰がいつ下しましたか。
- **想定根拠**: `aidlc-docs/audit.md`（Requirements Analysis Approval）
- **模範解答要旨**: 要件承認時にユーザーが「ワークショップなので、全ての工程を行いたいです。」と発言し、全ステージEXECUTEの方針が確定。execution-plan.mdに反映。

### Q3. 定期予約の要件で当初未確定だった事項は何で、それぞれどう確定しましたか。
- **想定根拠**: `aidlc-docs/inception/requirements/requirement-verification-questions.md`、`audit.md`（Requirements Analysis - Answers Received: 対話形式で13問）
- **模範解答要旨**: 重複時の全体拒否/スキップ（→全体拒否）、テーブル設計（→新テーブル+series_id列）、終了指定方式（→count/until両方サポート・一方のみ指定）、回数上限（→52）、エンドポイント（→POST /reservations/recurring）、キャンセル対象（→未来のactive回のみ）等。すべてユーザーがAskUserQuestion対話で回答して確定。

### Q4. この機能の完成判定（リリース可能という判断）は何を根拠に行われましたか。
- **想定根拠**: `audit.md`（Build and Test Stage）、`aidlc-docs/construction/build-and-test/build-and-test-summary.md`
- **模範解答要旨**: テスト66/66パス（既存回帰34+新規27+PBT5）、既存DBコピーへのマイグレーション検証、実APIでのE2Eスモーク、制約C-1〜C-4の充足確認。その上でユーザーが承認。

## 監査視点

### Q5. 今回の変更で新しい外部依存（ライブラリ）は追加されましたか。追加の承認記録はありますか。
- **想定根拠**: `audit.md`（NFR Requirements: Hypothesis追加の回答と承認、Code Generation: requirements.txt変更）、`aidlc-docs/construction/recurring-reservations/nfr-requirements/tech-stack-decisions.md`
- **模範解答要旨**: Hypothesis（PBT用）のみ追加。NFR Requirementsステージでユーザーが「Hypothesis追加」を選択し承認、Code Generation計画のファイル変更サマリにrequirements.txt変更として明記。

### Q6. 既存DBスキーマへの変更はどのような方式で行われ、その方式は誰が承認しましたか。
- **想定根拠**: `audit.md`（Infrastructure Design: 「軽量な自動ALTERヘルパ」回答と承認）、`aidlc-docs/construction/recurring-reservations/infrastructure-design/infrastructure-design.md`
- **模範解答要旨**: create_all拡張 + 冪等なseries_id列追加ヘルパ（自動ALTER）方式。Infrastructure Designステージの対話質問でユーザーが選択・承認。Build and Testで既存DBコピーに対する冪等性を検証済み。

### Q7. 認証・認可が実装されていないのは意図的ですか。誰の判断ですか。
- **想定根拠**: `brownfield-vision.md`（Out of Scope）、`audit.md`（Requirements Analysis: Q11 Security=No）、`requirements.md`（Extension Configuration）
- **模範解答要旨**: 意図的。Visionでスコープ外と定義済みで、さらにSecurity Baseline拡張のオプトイン質問（Q11）でユーザーが明示的にNoを選択している。

### Q8. 既存機能を壊していないことはどのように保証されましたか。
- **想定根拠**: `requirements.md`（C-1〜C-4）、`audit.md`（Build and Test）、`build-and-test-summary.md`
- **模範解答要旨**: 制約として既存API契約不変（C-1）・既存テスト改変不可（C-4）を定義。既存回帰テスト34件を未改変のままパスさせ（インポート規約成立のためルートにconftest.pyエイリアスのみ追加）、元reservations.dbが無変更であることも確認。

## 新任エンジニア視点

### Q9. シリーズ作成時、1回でも重複があると全体が409拒否になるのはなぜですか。「重複回だけスキップして作成」ではだめだったのですか。
- **想定根拠**: `brownfield-vision.md`（Open Questions）、`audit.md`（Requirements Analysis Q1=全体拒否）、`business-rules.md`（BR-RS-OV2）
- **模範解答要旨**: Vision時点では全体拒否かスキップかは未確定の設計論点だった。要件分析の対話でユーザーが全体拒否を選択し、BR-RS-OV2（原子性: 単一トランザクションで全登録 or 全ロールバック）として仕様化された。

### Q10. シリーズの回数上限が52回である根拠は何ですか。
- **想定根拠**: `audit.md`（Requirements Analysis Q4=上限あり(52)）、`requirements.md`（FR-1.5）、`business-rules.md`（BR-RS-C7）
- **模範解答要旨**: 要件分析の対話でユーザーが上限52（週次で約1年分）を選択。FR-1.5・BR-RS-C7として仕様化。

### Q11. シリーズ内の個別回のキャンセルに新規APIを作らなかったのはなぜですか。
- **想定根拠**: `audit.md`（Q7=既存キャンセルAPI流用）、`business-rules.md`（BR-RS-I1）、`requirements.md`（FR-3）
- **模範解答要旨**: シリーズ各回は通常のReservation行（series_id付き）なので、既存の `POST /reservations/{id}/cancel` がそのまま機能する。要件分析でユーザーが既存流用を選択。新規ルール・新規コードなし（BR-RS-I1）で、C-1（既存API契約不変）とも整合。

### Q12. 定期予約のコードが独立した app/series モジュールになっているのはなぜですか。
- **想定根拠**: `audit.md`（Application Design: コンポーネント配置=新規app.seriesモジュール、日付生成=純粋関数切出し、リポジトリ=新規SeriesRepository）、`aidlc-docs/inception/application-design/`
- **模範解答要旨**: Application Designステージの設計質問でユーザーが「新規app.seriesモジュール」を選択。日付生成を純粋関数（recurrence.py）に切り出し、SeriesRepositoryを新設する構成もこのとき決定・承認された。

## 品質保証視点

### Q13. Property-Based Testingはどの範囲に適用されていますか。なぜ全面適用ではないのですか。
- **想定根拠**: `audit.md`（Q13 PBT=Partial、PBTルールPBT-02/03/07/08/09のみロード）、`requirements.md`（Extension Configuration）、`nfr-design-patterns.md`（P-6）
- **模範解答要旨**: 拡張オプトインでユーザーがPartialを選択。PBT-02（round-trip）/03（不変条件）/07（生成器）/08（shrinking/seed）/09（フレームワーク=Hypothesis）のみ強制。適用対象は日付生成・重複判定・シリアライズ往復。

### Q14. untilで指定した終了日当日に開始する回は生成対象に含まれますか。その仕様はどこで確定しましたか。
- **想定根拠**: `audit.md`（Functional Design: until=開始日<=until inclusive, date）、`business-rules.md`（BR-RS-C6）
- **模範解答要旨**: 含まれる（inclusive）。untilは日付として扱い、各回の開始日がuntil以下の回まで生成。Functional Designステージの対話でユーザーが確定し、BR-RS-C6として仕様化。

### Q15. テストがパスしたという記録の内訳と、テスト環境の再現手順は残っていますか。
- **想定根拠**: `audit.md`（Build and Test: 66 passed）、`build-and-test-summary.md`、`build-instructions.md`、`unit-test-instructions.md`
- **模範解答要旨**: 66件パス＝既存回帰34+新規例示27+PBT5。venv構築・依存インストール・pytest実行手順はbuild-instructions.md等に記録あり。

## ダミー質問（「記録なし」が正解）

### Q16. 本番環境へのデプロイはいつ実施され、誰が承認しましたか。
- **模範解答要旨**: **記録なしが正解**。Operationsステージはプレースホルダで、デプロイは実施されていない（audit.md末尾）。デプロイ実施・承認の記録は存在しない。

### Q17. 過去に発生した本番障害と、その対応記録はどこにありますか。
- **模範解答要旨**: **記録なしが正解**。障害対応の実績・記録は存在しない（運用フェーズ未実施）。
