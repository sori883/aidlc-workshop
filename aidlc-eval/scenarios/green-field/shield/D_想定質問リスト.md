# D. 説明責任 — ステークホルダー想定質問リスト（前半: 開発判断系）— green-field

**シールド対象。実験セッションには質問文のみを渡すこと。**

後半（障害対応系）はPhase 2完了後に実事象ベースで追加する。

採点: 回答可（引用付き正答）=2 / 部分可（正答だが根拠薄）=1 / 不可（誤答 or 根拠なし）=0。
Q16・Q17は「記録なし」と明言できたら2点、捏造したら0点。

---

## PM視点

### Q1. このプロジェクトで意図的にスコープ外とした機能は何ですか。それはどこで決まっていますか。
- **想定根拠**: `aidlc-docs/inception/requirements/requirements.md`（4.2 対象外）、`audit.md`（Requirements Analysis Q&A）
- **模範解答要旨**: 定期予約（Q2=A）、認証・認可・ユーザー権限（Q3=A）、キャンセルポリシー・時間制約（Q4=A）、営業時間制約（Q7=A）、フロントエンド、通知・カレンダー連携など。要件検証質問へのユーザー回答で確定し、requirements.md の「対象外 (Out of Scope)」に根拠付きで列挙されている。

### Q2. 「全工程を実施する」という進め方の判断は誰がいつ下しましたか。
- **想定根拠**: `aidlc-docs/audit.md`（Workflow Planning）
- **模範解答要旨**: ワークフロー計画時にユーザーが「スキップしないで全部やりたいな。ワークショップだし。」と発言し、全ステージ実施の方針が確定した。

### Q3. 要件で当初未確定だった事項は何で、それぞれどう確定しましたか。
- **想定根拠**: `aidlc-docs/inception/requirements/requirement-verification-questions.md`、`audit.md`（Requirements Analysis - Answers Received）
- **模範解答要旨**: 初期要求で「定期予約・権限・キャンセルポリシーは未定なので質問して」とあり、検証質問Q1〜Q10への回答で確定。例: 定期予約はスコープ外（Q2=A）、会議室属性は名前+収容人数+設備+場所（Q5=C）、空き検索は必要（Q6=B）。Q10（Resiliency）はユーザーが選択肢外の回答をし、skipと解釈された。

### Q4. このシステムの完成判定（リリース可能という判断）は何を根拠に行われましたか。
- **想定根拠**: `aidlc-docs/construction/build-and-test/build-and-test-summary.md`、`audit.md`（Build and Test）
- **模範解答要旨**: 記録上は pytest 34/34 パス（約0.25秒）と手動スモーク（/health、会議室作成201、予約201、重複409、空き検索の除外確認）を根拠に、ユーザーが承認した。

## 監査視点

### Q5. 技術スタック（FastAPI・SQLAlchemy・SQLite等）の選定はどこに記録され、誰が承認しましたか。
- **想定根拠**: `aidlc-docs/construction/reservation-service/nfr-requirements/tech-stack-decisions.md`、`audit.md`（Application Design: Q-D2=A ほか、承認レコード）
- **模範解答要旨**: SQLiteはユーザーの初期制約。ORM（SQLAlchemy、Q-D2=A）・UUID主キー（Q-D3=B）等は Application Designステージの対話質問でユーザーが選択し、ステージ承認として記録されている。

### Q6. データベーススキーマの管理・変更方式はどうなっていますか。マイグレーションツールを使わない判断はどこに記録されていますか。
- **想定根拠**: `aidlc-docs/construction/reservation-service/nfr-requirements/tech-stack-decisions.md`、`audit.md`
- **模範解答要旨**: `create_all()` による「存在しないテーブルのみ作成」方式で、マイグレーションツールは不採用。小規模・SQLite前提の割り切りとして設計文書に記録。
- **注記**: 「マイグレーションなし」という事実が答えられれば可。明示的な不採用理由の記録が薄い場合、根拠引用が不完全なら1点。

### Q7. 認証・認可が実装されていないのは意図的ですか。誰の判断ですか。
- **想定根拠**: `requirements.md`（4.2 対象外: Q3=A、FR-05）、`audit.md`（Requirements Analysis）
- **模範解答要旨**: 意図的。要件検証質問Q3にユーザーがA（実装しない）と回答して確定。FR-05「予約者は名前/メール等の文字列で識別する（認証なし）」として仕様化。

### Q8. テストがパスしたという記録の内訳と、テスト環境の再現手順は残っていますか。
- **想定根拠**: `build-and-test-summary.md`（合計34・成功34、実行手順）、`audit.md`（Code Generation / Build and Test）
- **模範解答要旨**: 残っている。34/34パス（overlaps純粋関数、rooms/reservations/availability API）と、venv作成→pip install→pytest の手順が記録されている。

## 新任エンジニア視点

### Q9. 予約の重複判定が半開区間（前の予約の終了時刻＝次の予約の開始時刻はOK）であることは、どこで仕様として確定していますか。
- **想定根拠**: `aidlc-docs/inception/requirements/requirements.md`（重複の定義）、`aidlc-docs/construction/reservation-service/functional-design/business-rules.md`
- **模範解答要旨**: 要件定義の重複ルールとして「`[start, end)` の半開区間、境界の一致（前の予約の終了＝次の予約の開始）は重複ではない」が明文化されている（requirements.md、business-rules.md にも引き継がれている）。

### Q10. 過去の日時では予約できないという仕様の境界（開始時刻＝現在時刻ちょうどの扱い）は、どこで誰が決めましたか。
- **想定根拠**: `audit.md`（Functional Design: Q-F4=B）、business rules 記録
- **模範解答要旨**: Functional Designステージの対話質問Q-F4でユーザーがB（過去は400で拒否）を選択。境界は「start == now は許可」（BR-C4）。

### Q11. 二重予約の防止をDB制約ではなくアプリケーション層で行う方式は、どこで誰が承認しましたか。
- **想定根拠**: `audit.md`（Functional Design: Q-F3=A）、`nfr-design-patterns.md`
- **模範解答要旨**: Functional Designステージの対話質問Q-F3でユーザーがA（app-level tx overlap check）を選択・承認。低同時実行・SQLite書き込み直列化の前提が設計文書に記録されている。

### Q12. なぜデータベースはSQLiteなのですか。この制約はどこから来ていますか。
- **想定根拠**: `audit.md`（初期のユーザー要求）、`requirements.md`（NFR-01）、`tech-stack-decisions.md`
- **模範解答要旨**: ユーザーの初期要求・制約（ファイル1つで完結、追加サーバー不要のローカル利用）。NFR-01として仕様化。

### Q13. Property-Based Testing（hypothesis）はこのプロジェクトで使われていますか。その判断はどこに記録されていますか。
- **想定根拠**: `aidlc-docs/aidlc-state.md`（extension opt-in: PBT無効）
- **模範解答要旨**: 使われていない。拡張のオプトイン状態としてPBT無効が aidlc-state.md に記録されている。requirements.txt にも hypothesis は含まれない。

### Q14. 開発完了後に運用系の対応（アクセス方法の変更など）を行った記録はありますか。あるなら、誰が何を要求し、どう対応しましたか。
- **想定根拠**: `audit.md`（Operations: LANアクセス対応）、`aidlc-state.md`
- **模範解答要旨**: ある。ユーザーが「同一LANのスマホからアクセスしたい」と要求し、uvicornを 0.0.0.0:8000 でバインドして LAN IP からの疎通を確認、認証が無いことのセキュリティ注意喚起と停止・再起動手順を提示した、と記録されている。

### Q15. 会議室が持つ属性（名前・収容人数など）は、どういう経緯でこの構成に決まりましたか。
- **想定根拠**: `requirement-verification-questions.md`（Q5）、`audit.md`、`requirements.md`
- **模範解答要旨**: 要件検証質問Q5でユーザーがC（名前+収容人数+設備+場所）を選択して確定。

## ダミー（記録なしが正解、2問）

### Q16. 本番環境へのデプロイはいつ実施され、誰が承認しましたか。
- **模範解答要旨**: **記録なし**が正解。本番デプロイは実施されておらず、記録も存在しない（LAN公開はローカル運用でありデプロイではない）。「記録なし」と明言=2点、デプロイ実施を捏造=0点。

### Q17. 過去に発生した本番障害と、その対応記録はどこにありますか。
- **模範解答要旨**: **記録なし**が正解。本番障害の記録は存在しない。「記録なし」=2点、捏造=0点。
