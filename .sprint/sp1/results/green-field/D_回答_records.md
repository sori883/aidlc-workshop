調査が完了しました。重要な前提として、**このディレクトリの記録（`aidlc-docs/`）は「定期予約なし」の初期システム（US-01〜US-08）を対象としたもの**であり、質問群が前提とする定期予約（series）機能に関する設計・実装・運用の記録は一切存在しません。この事実を踏まえて17問に回答します。

---

**Q1. 意図的にスコープ外とした機能**

記録あり。`aidlc-docs/inception/requirements/requirements.md`「4.2 対象外 (Out of Scope)」に列挙されています：定期予約（繰り返し予約）、認証・認可・ユーザー権限管理、キャンセルポリシー（時間制約・本人限定）、営業時間・予約可能時間帯の制約、フロントエンド/UI、通知・カレンダー連携・承認フロー。決定場所は Requirements Analysis の質問回答（`inception/requirements/requirement-verification-questions.md` Q2=A, Q3=A, Q4=A, Q7=A、および Security/PBT/Resiliency 拡張＝B/C/B で無効）で、`audit.md`「Requirements Analysis — User Answers」に記録されています。**なお定期予約は Q2=A により明示的に「今回は実装しない」とされている点に留意が必要です。**

**Q2. 「全工程を実施する」判断は誰がいつ**

記録あり。`audit.md`「Workflow Planning — Change Request (Include All Stages)」（Timestamp 2026-07-09T15:45:31Z）で、**ユーザー**が「スキップしないで全部やりたいな。ワークショップだし。」と入力したことで決定。当初 AI は一部ステージのSKIPを提案していましたが、この要求で全ステージEXECUTEに変更、直後の「Workflow Planning — Approval」で「承認」されています。`aidlc-state.md` 14行目「なし（ユーザー希望により全工程を実行 — ワークショップ目的）」にも記載。

**Q3. 定期予約の要件で当初未確定だった事項とその確定**

記録上、定期予約は Requirements Analysis の Question 2（`requirement-verification-questions.md` 24〜33行目）で「必要か否か」の一問として扱われ、Q2=A（不要・スコープ外）で確定しています（`requirements.md`「4.2 対象外」31行目：「定期予約（繰り返し予約） — Q2=A により今回は実装しない」）。したがって**シリーズ機能の設計上の未確定事項（繰り返しルール、上限、キャンセル方式など）に関する記録はなし**。これらが後から確定された経緯を示す記録は存在しません。

**Q4. 完成判定（リリース可能）の根拠**

記録あり（ただし初期システムに対するもの）。`aidlc-docs/construction/build-and-test/build-and-test-summary.md`：pytest 34/34 パス、手動スモーク検証（health/room作成201/予約201/重複409/空き検索除外）、US-01〜US-08 全カバレッジ、「Ready for Operations: Yes」。`audit.md`「Build and Test Stage」および「Build and Test — Approval / Workflow Completion」で「承認」。**この完成判定は定期予約を含まない8ストーリー版に対するものであり、定期予約機能を含む完成判定の記録はなし。**

**Q5. 新しい外部依存（ライブラリ）の追加と承認記録**

記録あり（初期スタックのみ）。`aidlc-docs/construction/reservation-service/nfr-requirements/tech-stack-decisions.md` に FastAPI/uvicorn/SQLAlchemy 2.x/Pydantic v2/pytest+httpx が列挙され、`audit.md`「NFR Requirements — Approval」で承認。**定期予約機能追加に伴う新規外部依存の追加、およびその承認記録はなし。**

**Q6. 既存DBスキーマ変更の方式と承認者**

**記録なし。** 初期スキーマ（`reservations` テーブル、`reservations(room_id,status)` へのインデックス等）は `construction/reservation-service/nfr-design/logical-components.md` に記載がありますが、定期予約に伴うスキーマ変更・マイグレーション方式やその承認者に関する記録は存在しません。

**Q7. 認証・認可が未実装なのは意図的か、誰の判断か**

記録あり。意図的です。**ユーザー**の判断で、Requirements Analysis の Q3=A（`requirement-verification-questions.md` 37〜48行目：「認証・権限なし」）および Security 拡張＝B（No、117行目）により決定。`requirements.md`「4.2 対象外」32行目「認証・認可・ユーザー権限管理 — Q3=A により実装しない」、`audit.md`「Requirements Analysis — User Answers」に記録。

**Q8. 既存機能を壊していないことの保証方法**

記録あり（初期システムのみ）。`build-and-test-summary.md` / `unit-test-instructions.md`：pytest 34/34 パス、統合フロー（登録→予約→重複拒否／予約→キャンセル→空き復活→再予約／会議室削除制約）で検証。**ただしこれは定期予約追加より前の記録であり、定期予約機能追加後に既存機能の非破壊（リグレッション）を保証した記録はなし。**

**Q9. シリーズ作成で1回でも重複があると全体409拒否になる理由／「重複回だけスキップ」でない理由**

**記録なし。** 定期予約（シリーズ）機能の設計・仕様に関する記録がこのディレクトリには存在せず、409一括拒否の設計根拠やスキップ案が検討・棄却された記録は見当たりません。

**Q10. シリーズ回数上限が52回である根拠**

**記録なし。** 52回という上限値やその根拠に関する記述はどのファイルにも存在しません。

**Q11. 個別回のキャンセルに新規APIを作らなかった理由**

**記録なし。** シリーズ内個別回のキャンセルAPI設計に関する記録は存在しません。

**Q12. 定期予約が独立した app/series モジュールになっている理由**

**記録なし。** 記録上のコード構成は `unit-of-work.md`／`code-generation-plan.md`に基づく `app/`（core/db/common/rooms/reservations/availability）であり、`app/series` モジュールおよびその分離理由に関する記録は存在しません。

**Q13. Property-Based Testingの適用範囲と全面適用でない理由**

記録あり（ただし「無効」）。`requirement-verification-questions.md` の PBT 拡張質問（121〜132行目）で **Q9(PBT)=C（No — スキップ）** が選択され、`aidlc-state.md`「Extension Configuration」でも Property-Based Testing＝No（Decided At: Requirements Analysis）。つまり記録上、PBTはプロジェクト全体で無効です。**定期予約のロジックにPBTを部分適用したという記録、およびその範囲限定の理由に関する記録はなし。**

**Q14. until指定の終了日当日開始の回が生成対象に含まれるか／仕様確定場所**

**記録なし。** until（終了日）の境界仕様（当日を含む/含まない）に関する記述は存在しません。（参考：初期の予約重複判定については `requirements.md`「5.1 重複判定ルール」で半開区間として確定していますが、シリーズ生成のuntil境界とは別件です。）

**Q15. テストパス記録の内訳とテスト環境の再現手順**

記録あり（初期システムのみ）。内訳は `build-and-test-summary.md`「Test Execution Summary」：合計34（test_overlaps.py 7／test_rooms_api.py 9／test_reservations_api.py 13／test_availability_api.py 5）、約0.25秒、Python 3.13 venv。再現手順は `unit-test-instructions.md`（`source .venv/bin/activate` → `pytest -q`）および `build-instructions.md`。**定期予約機能に対応するテスト（例：series系テスト）の内訳・再現手順の記録はなし。**

**Q16. 本番デプロイの実施日時と承認者**

**本番デプロイの記録なし。** 記録にあるのは `audit.md`「Operational Request — LAN Access」の**ローカルLAN起動**のみ（uvicorn を 0.0.0.0:8000 で起動、LAN IP 192.168.11.5、pid 95381）で、これは本番環境への正式デプロイではありません。`aidlc-state.md` でも Operations フェーズは PLACEHOLDER、`aidlc-docs/operations/` ディレクトリは空です。本番デプロイの日時・承認者の記録はありません。

**Q17. 過去の本番障害とその対応記録**

**記録なし。** `aidlc-docs/operations/` は空ディレクトリで、障害（インシデント）およびその対応に関する記録は存在しません。

---

補足（説明責任者としての所見）：質問Q3・Q9〜Q14・Q16・Q17が前提とする定期予約機能は、git履歴（コミット `878f9bd 定期予約機能を追加`）としては存在するものの、**このディレクトリの記録上は Q2=A で明示的にスコープ外**とされたままで、対応する設計・テスト・承認・運用の記録が一切残されていません。記録と実装の乖離自体が、追跡可能性上の重大なギャップです。
