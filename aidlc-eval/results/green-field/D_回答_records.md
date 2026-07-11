調査が完了しました。回答の前に、17問全体に関わる**重要な構造的事実**を1点述べます。

このディレクトリ `green-field/cond-D-records/` に存在する記録（`aidlc-docs/` 配下）は、**定期予約機能を含まない**元の会議室予約システムのものです。git コミット `878f9bd`「定期予約（recurring reservations）機能を追加」で追加された series モジュールとその設計記録は、すべて**別ディレクトリ `brown-field/aidlc-docs/` 配下**にあり、この `cond-D-records` ディレクトリ内には存在しません。したがって定期予約（series）に関する質問（Q3, Q9, Q10, Q11, Q12, Q14 など）は、このディレクトリの記録だけを根拠とする限り「記録なし」となります。以下、ルールに従い各問に回答します。

---

**Q1.** 意図的にスコープ外とした機能は、`aidlc-docs/inception/requirements/requirements.md`「4.2 対象外 (Out of Scope)」に列挙されています：**定期予約（繰り返し予約, Q2=A）／認証・認可・ユーザー権限管理（Q3=A）／キャンセルポリシー（時間制約・本人限定, Q4=A）／営業時間・予約可能時間帯の制約（Q7=A）／フロントエンド・UI／通知・カレンダー連携・承認フロー**。決定箇所は、要件分析フェーズでのユーザー回答（`aidlc-docs/audit.md`「Requirements Analysis — User Answers」、回答「Q2.A Q3.A Q4.A … Q7.A」）で、それが requirements.md に反映されています。

**Q2.** 「スキップせず全工程を実施する」という判断は、**ユーザー（依頼者本人）**が**Workflow Planning フェーズ**で下しました。根拠は `aidlc-docs/audit.md`「Workflow Planning — Change Request (Include All Stages)」のユーザー入力「スキップしないで全部やりたいな。ワークショップだし。」です。当初 AI は5段階のスキップを提案しましたが、この要望で全段階 EXECUTE に変更され、続く「Workflow Planning — Approval」で「承認」されました。`aidlc-docs/aidlc-state.md`「Execution Plan Summary」にも「ユーザー希望により全工程を実行 — ワークショップ目的」と記録。なお記録上のタイムスタンプは全エントリが `2026-07-09T15:45:31Z` と同一で、正確な時刻分解能は記録されていません。

**Q3.** 記録なし。このディレクトリ内には定期予約機能そのものの記録が存在しません（`requirements.md` 4.2 で定期予約はスコープ外と明記）。定期予約の要件・未確定事項の確定経緯は、別ディレクトリ `brown-field/aidlc-docs/` 側の記録にあり、本ディレクトリの根拠では回答できません。

**Q4.** この（元の会議室予約システムの）完成・リリース可能判定は、`aidlc-docs/construction/build-and-test/build-and-test-summary.md`「Overall Status / Next Steps」を根拠にしています：**ビルド成功、pytest 34/34 合格（約0.25秒）、手動スモーク検証（/health, room作成201, 予約201, 重複409, 空き検索除外）、全8ストーリー US-01〜US-08 検証済み**で「Ready for Operations: Yes」。ただし同書には「Operations フェーズはプレースホルダ」とあり、正式リリース判定ではなく「ワークショップの完成物として利用可能」という位置づけです。定期予約機能の完成判定は本ディレクトリには記録なし。

**Q5.** 記録なし（＝このディレクトリ内で「新規追加された外部依存」を示す記録はありません）。本ディレクトリの `aidlc-docs/construction/reservation-service/nfr-requirements/tech-stack-decisions.md`「依存パッケージ」に挙がるのは元システムの依存（`fastapi, uvicorn[standard], sqlalchemy, pydantic, pytest, httpx`）で、これらは NFR Requirements 段階でユーザー「承認」済み（`audit.md`「NFR Requirements — Approval」）。定期予約機能に伴う新規ライブラリ追加とその承認記録は、本ディレクトリには存在しません。

**Q6.** 記録なし（既存スキーマへの「変更」記録は本ディレクトリにありません）。本ディレクトリの記録では、DB はグリーンフィールドで新規作成される方式です：`aidlc-docs/construction/reservation-service/infrastructure-design/deployment-architecture.md`「起動時処理」および同「データライフサイクル」に、起動時に `Base.metadata.create_all()` でテーブルを自動生成、と記載。既存スキーマの変更・マイグレーション方式とその承認者に関する記録は本ディレクトリにはありません（定期予約に伴うスキーマ変更は brown-field 側）。

**Q7.** はい、認証・認可の未実装は**意図的**で、判断者は**ユーザー（依頼者）**です。根拠は `aidlc-docs/inception/requirements/requirements.md`「4.2 対象外」の「認証・認可・ユーザー権限管理 — Q3=A により実装しない」、および元入力の制約回答（`aidlc-docs/audit.md`「Requirements Analysis — User Answers」の Q3=A「name/email string only, no auth/permissions」）。requirements.md「7. 前提・制約」にも「認証がないため、予約者情報は自己申告の文字列として扱う」と明記。

**Q8.** 本ディレクトリの記録での「壊れていないこと」の保証手段は、`aidlc-docs/construction/build-and-test/build-and-test-summary.md` にある **pytest 34/34 全合格＋手動スモーク検証＋全8ストーリーのカバレッジ表**です。ただしこれは元システムの初回構築時の検証であり、定期予約機能追加後に「既存機能を壊していないこと」を保証した回帰テスト記録は、本ディレクトリには存在しません（記録なし）。

**Q9.** 記録なし。シリーズ作成時の 409 一括拒否 vs「重複回だけスキップ」の設計判断は、本ディレクトリの記録には存在しません（定期予約自体がスコープ外）。この論点は brown-field 側の business-rules 等に記録されている可能性がありますが、本ディレクトリの根拠では回答できません。

**Q10.** 記録なし。シリーズ回数上限（52回）の根拠は、本ディレクトリ内のいずれのファイルにも記載がありません（`series|52|weekly` 等での全文検索でも該当なし）。

**Q11.** 記録なし。シリーズ内個別回のキャンセルに新規APIを設けなかった理由は、本ディレクトリの記録に存在しません。（本ディレクトリの元システムでは、キャンセルは FR-08「予約IDを指定すれば誰でもキャンセル可能」のみが `requirements.md` に規定されています。）

**Q12.** 記録なし。`app/series` モジュールを独立させた理由は本ディレクトリに記録がありません。本ディレクトリの記録では、コード構成は Units Generation で「Unit-1 モノリス（rooms/reservations/availability/db モジュール）」（`aidlc-docs/audit.md`「Units Generation」）とされ、series モジュールは含まれていません。

**Q13.** 本ディレクトリの記録では、Property-Based Testing（PBT）は**プロジェクト全体で無効（適用範囲ゼロ）**です。根拠は `aidlc-docs/aidlc-state.md`「Extension Configuration」の「Property-Based Testing = No（Requirements Analysis で決定）」、および `aidlc-docs/audit.md`「Requirements Analysis — User Answers」の「Q9=C PBT→No」。全面適用でない理由は、ユーザーが要件分析時に拡張機能を無効と回答したためです（`requirements.md` NFR-07「セキュリティ/レジリエンシー/PBT 拡張はいずれも無効（ワークショップ・PoC のため）」）。定期予約への部分適用という話は本ディレクトリには記録なし。

**Q14.** 記録なし。`until` で指定した終了日当日の回を生成対象に含めるか（境界仕様）の記録は、本ディレクトリには存在しません。定期予約の生成ロジック仕様は本ディレクトリの範囲外です。

**Q15.** テスト合格の内訳は `aidlc-docs/construction/build-and-test/build-and-test-summary.md`「Test Execution Summary」に記録：**合計34・成功34・失敗0（約0.25秒）**、内訳は `test_overlaps.py`:7 / `test_rooms_api.py`:9 / `test_reservations_api.py`:13 / `test_availability_api.py`:5、加えて統合フローと手動スモーク結果。テスト環境の再現手順は `aidlc-docs/construction/build-and-test/build-instructions.md`・`unit-test-instructions.md`・`integration-test-instructions.md`、および `deployment-architecture.md`「セットアップ手順」（venv 作成 → `pip install -r requirements.txt` → uvicorn 起動）に残っています。ただしこれらは元システムのものです。

**Q16.** 記録なし（本番デプロイの記録はありません）。本ディレクトリで「起動」に最も近い記録は `aidlc-docs/audit.md`「Operational Request — LAN Access」で、ユーザー要望により **ローカルで uvicorn を 0.0.0.0:8000 に起動し同一LAN内スマホからアクセス可能にした**もの（開発機での一時起動、pid 95381, LAN IP 192.168.11.5）です。これは本番環境デプロイではなく、`aidlc-state.md`「OPERATIONS PHASE — Operations - PLACEHOLDER」の通り運用フェーズはプレースホルダです。承認者・実施日を伴う本番デプロイの記録は存在しません。

**Q17.** 記録なし。過去の本番障害およびその対応記録は、本ディレクトリ内のいずれのファイル（audit.md、build-and-test 配下、aidlc-state.md 等）にも存在しません。
