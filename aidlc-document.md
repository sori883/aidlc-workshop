# ドキュメント一覧

`brown-field/aidlc-docs` と `green-field/aidlc-docs` に含まれるドキュメントの一覧です。

- **brown-field**: 既存の会議室予約システムに「定期予約（毎週同じ曜日・時間の繰り返し予約）」機能を追加するプロジェクト（Brownfield）
- **green-field**: 社内会議室予約システムをゼロから構築するプロジェクト（Greenfield）

---

## brown-field/aidlc-docs

### ルート

| ファイル名 | 概要 |
|---|---|
| `aidlc-state.md` | AI-DLC の進行状態トラッキング。プロジェクト種別（Brownfield）、対象ユニット（recurring-reservations）、各ステージの完了状況を記録 |
| `audit.md` | AI-DLC 監査ログ。ユーザーの初期リクエストから各ステージでのユーザー入力・AI応答の履歴を時系列で記録 |

### inception/reverse-engineering（既存システムの解析）

| ファイル名 | 概要 |
|---|---|
| `business-overview.md` | 既存システムのビジネス概要。会議室管理・予約管理・空き検索の業務コンテキスト図と説明 |
| `architecture.md` | 既存システムのアーキテクチャ。FastAPI + SQLAlchemy + SQLite のレイヤードアーキテクチャ（Router→Service→Repository→ORM）の構成図 |
| `code-structure.md` | コード構造の解析。ビルドシステム（pip）、主要クラス・モジュールのクラス図 |
| `api-documentation.md` | 既存 REST API のドキュメント。会議室 CRUD・予約・空き検索の各エンドポイント仕様 |
| `component-inventory.md` | コンポーネント目録。app 配下の各パッケージ（rooms / reservations / availability / db / common / core）の一覧と役割 |
| `interaction-diagrams.md` | 相互作用図。予約作成（重複防止つき）などのビジネストランザクションのシーケンス図 |
| `technology-stack.md` | 技術スタックの解析。Python 3.13 / FastAPI / Pydantic v2 / SQLAlchemy 2.0 / SQLite / uvicorn |
| `dependencies.md` | 内部モジュール間の依存関係図と外部依存の一覧 |
| `code-quality-assessment.md` | コード品質評価。テストカバレッジ（単体・統合）、Linting 状況、コードスタイルの評価 |
| `reverse-engineering-timestamp.md` | リバースエンジニアリングのメタデータ。解析日時・対象ファイル数・生成成果物のチェックリスト |

### inception/requirements（要件定義）

| ファイル名 | 概要 | 
|---|---|
| `requirements.md` | 定期予約機能の要件定義書。インテント分析、機能要件（FR）・非機能要件（NFR）・制約（C）を定義 |
| `requirement-verification-questions.md` | 要件確定のための確認質問と回答記録（重複時は全体拒否、新テーブル + series_id 列追加、など） |

### inception/user-stories（ユーザーストーリー）

| ファイル名 | 概要 |
|---|---|
| `personas.md` | ペルソナ定義。一般予約者（社員）・会議室運用担当・API 連携開発者の3ペルソナ |
| `stories.md` | ユーザーストーリー（US-R01〜US-R08）。シリーズ作成・重複時全体拒否・キャンセル・照会などを Given-When-Then 形式の受け入れ基準つきで定義 |

### inception/application-design（アプリケーション設計）

| ファイル名 | 概要 |
|---|---|
| `application-design.md` | アプリケーション設計の統合ドキュメント。新規 `app.series` モジュールの配置・純粋関数化・既存ロジック再利用の方針 |
| `components.md` | 新規コンポーネント定義（series の router / service / recurrence / schemas / repository）と責務 |
| `component-methods.md` | 各コンポーネントのメソッドシグネチャ定義（`generate_occurrences` など） |
| `services.md` | サービス層定義。RecurringReservationService のオーケストレーション手順（検証→生成→重複チェック→原子的登録） |
| `component-dependency.md` | コンポーネント間の依存マトリクス（series 各モジュールと既存モジュールの依存関係） |
| `unit-of-work.md` | ユニット定義。単一ユニット `recurring-reservations`（モノリス内論理モジュール）の目的と責務 |
| `unit-of-work-story-map.md` | ストーリーとユニット・担当コンポーネントの対応表 |
| `unit-of-work-dependency.md` | ユニットから既存モジュールへの依存マトリクス（再利用 / 変更の区別つき） |

### inception/plans（INCEPTION 各ステージの計画）

| ファイル名 | 概要 |
|---|---|
| `execution-plan.md` | 実行計画。Brownfield 変更スコープの分析（新エンドポイント・新テーブル・既存ロジック再利用）と実施ステージの決定 |
| `user-stories-assessment.md` | ユーザーストーリー生成の要否評価。リクエスト分析と優先度基準の判定 |
| `story-generation-plan.md` | ストーリー生成計画。ブレイクダウン方針・ペルソナ粒度・受け入れ基準形式の承認済み決定 |
| `application-design-plan.md` | アプリケーション設計計画。コンポーネント配置・純粋関数切り出し等の Q&A による承認済み設計決定 |
| `unit-of-work-plan.md` | ユニット分解計画。単一ユニットとする決定とその理由 |

### construction/plans（CONSTRUCTION 各ステージの計画）

| ファイル名 | 概要 |
|---|---|
| `recurring-reservations-functional-design-plan.md` | Functional Design 計画。until 境界・未来回の定義・シリーズ照会の実装など業務ロジック上の承認済み決定 |
| `recurring-reservations-nfr-requirements-plan.md` | NFR Requirements 計画。PBT フレームワーク（Hypothesis）追加・依存バージョン方針の決定 |
| `recurring-reservations-nfr-design-plan.md` | NFR Design 計画。各 NFR パターンカテゴリの適用可否評価（大半は N/A、トランザクションのみ適用） |
| `recurring-reservations-infrastructure-design-plan.md` | Infrastructure Design 計画。既存 DB への軽量な自動 ALTER ヘルパによるスキーマ反映の決定 |
| `recurring-reservations-code-generation-plan.md` | Code Generation 計画（実装の single source of truth）。ファイル配置・既存構造踏襲・in-place 変更方針 |

### construction/recurring-reservations（ユニットの設計・実装成果物）

| ファイル名 | 概要 |
|---|---|
| `functional-design/domain-entities.md` | ドメインエンティティ定義。新規 `ReservationSeries` エンティティの属性・制約と既存 Reservation への series_id 追加 |
| `functional-design/business-rules.md` | 業務ルール（BR-RS*）。入力検証・重複時全体拒否・キャンセル・照会の各ルールを既存ルール体系に倣って定義 |
| `functional-design/business-logic-model.md` | 業務ロジックモデル。週次生成の純粋関数 `generate_occurrences` やシリーズ作成・キャンセルのロジックフロー |
| `nfr-requirements/nfr-requirements.md` | 非機能要件（NFR-RS*）。原子性（全成功 or 全ロールバック）・後方互換性などを定義 |
| `nfr-requirements/tech-stack-decisions.md` | 技術スタック決定。既存スタック継承 + Hypothesis のみ追加、の選定根拠 |
| `nfr-design/nfr-design-patterns.md` | NFR 設計パターン。原子的トランザクション（単一 commit）など採用パターンと根拠 |
| `nfr-design/logical-components.md` | 論理コンポーネント構成。series 各モジュールの責務境界と NFR の対応表 |
| `infrastructure-design/infrastructure-design.md` | インフラ設計。既存ローカル実行モデル踏襲、スキーマ反映（マイグレーション）のみが関心事 |
| `infrastructure-design/deployment-architecture.md` | デプロイアーキテクチャ。uvicorn + FastAPI + SQLite のローカル単一プロセス構成図 |
| `code/code-summary.md` | コード生成サマリ。新規作成（app/series 配下）・変更（db.models 等）したファイルの一覧と役割 |

### construction/build-and-test（ビルド・テスト）

| ファイル名 | 概要 |
|---|---|
| `build-instructions.md` | ビルド手順。venv 作成・依存インストール・環境変数設定の手順 |
| `unit-test-instructions.md` | 単体テスト実行手順と結果（66 passed: 既存回帰 34 + 新規 27 + PBT 5） |
| `integration-test-instructions.md` | 統合テスト手順。series と既存モジュール（availability 等）の連携を API 結合テストで検証するシナリオ |
| `performance-test-instructions.md` | 性能テスト手順。今回スコープ外（N/A）の判断と軽量な性能上の考慮の記録 |
| `build-and-test-summary.md` | ビルド・テスト結果の総括。ビルド成功、全 66 テストパス、統合シナリオ 4 件の結果 |

---

## green-field/aidlc-docs

### ルート

| ファイル名 | 概要 |
|---|---|
| `aidlc-state.md` | AI-DLC の進行状態トラッキング。プロジェクト種別（Greenfield）、単一ユニット構成、各ステージの完了状況を記録 |
| `audit.md` | AI-DLC 監査ログ。初期リクエスト（会議室予約システム構築）から各ステージのユーザー入力・AI応答の履歴を記録 |

### inception/requirements（要件定義）

| ファイル名 | 概要 |
|---|---|
| `requirements.md` | 要件定義書。ダブルブッキング防止を中心とした会議室予約システムのインテント分析・機能/非機能要件 |
| `requirement-verification-questions.md` | 要件確定のための確認質問と回答記録（予約時間の管理方法など、スコープを絞る観点の質問） |

### inception/user-stories（ユーザーストーリー）

| ファイル名 | 概要 |
|---|---|
| `personas.md` | ペルソナ定義。認証なしの単一ロール「予約する社員」1ペルソナ |
| `stories.md` | ユーザーストーリー（US-01〜US-08）。会議室管理・予約・重複拒否・空き検索を INVEST 準拠・受け入れ基準つきで定義 |

### inception/application-design（アプリケーション設計）

| ファイル名 | 概要 |
|---|---|
| `application-design.md` | アプリケーション設計の統合ドキュメント。レイヤ構成・SQLAlchemy 採用・UUID 文字列 ID などの確定事項 |
| `components.md` | コンポーネント定義。Room / Reservation / Availability の3コンポーネントの目的と責務 |
| `component-methods.md` | 各サービスのメソッド定義（高レベルシグネチャと入出力） |
| `services.md` | サービス層定義。RoomService / ReservationService / AvailabilityService のオーケストレーション |
| `component-dependency.md` | コンポーネント依存マトリクスと通信パターン（同一プロセス内の関数呼び出しのみ） |
| `unit-of-work.md` | ユニット定義。単一ユニット（モノリス）の決定と内部モジュール構成 |
| `unit-of-work-story-map.md` | 全ストーリーと担当モジュール・ユニットの対応表 |
| `unit-of-work-dependency.md` | ユニット内モジュール間の依存マトリクス |

### inception/plans（INCEPTION 各ステージの計画）

| ファイル名 | 概要 |
|---|---|
| `execution-plan.md` | 実行計画。変更影響評価・リスク評価と実施ステージの決定（ワークショップのため全工程実行） |
| `user-stories-assessment.md` | ユーザーストーリー生成の要否評価。リクエスト分析と優先度基準の判定 |
| `story-generation-plan.md` | ストーリー生成計画。機能ベース分類・単一ペルソナ・粗め粒度（6〜8本）の決定 |
| `application-design-plan.md` | アプリケーション設計計画。想定コンポーネントの初期案と設計質問 |
| `unit-of-work-plan.md` | ユニット分解計画。単一ユニット（モノリス）とする方針の Q&A と決定 |

### construction/plans（CONSTRUCTION 各ステージの計画）

| ファイル名 | 概要 |
|---|---|
| `reservation-service-functional-design-plan.md` | Functional Design 計画。会議室削除時の予約の扱い・キャンセル冪等性などの未確定論点の Q&A |
| `reservation-service-nfr-requirements-plan.md` | NFR Requirements 計画。想定同時利用規模などの質問と前提（拡張機能すべて無効）の整理 |
| `reservation-service-nfr-design-plan.md` | NFR Design 計画。各 NFR パターンカテゴリの適用可否評価（大半は N/A または限定的） |
| `reservation-service-infrastructure-design-plan.md` | Infrastructure Design 計画。ローカル実行制約によりインフラ確定済み、質問不要の判断 |
| `reservation-service-code-generation-plan.md` | Code Generation 計画（実装の single source of truth）。US-01〜08 のコード配置・技術スタック・実装方針 |

### construction/reservation-service（ユニットの設計・実装成果物）

| ファイル名 | 概要 |
|---|---|
| `functional-design/domain-entities.md` | ドメインエンティティ定義。Room / Reservation の属性・型・制約 |
| `functional-design/business-rules.md` | 業務ルール（BR-*）。会議室バリデーション・重複防止・削除拒否・冪等キャンセルのルール |
| `functional-design/business-logic-model.md` | 業務ロジックモデル。各ユースケース（UC-1〜）のロジックフロー（検証→永続化→レスポンス） |
| `nfr-requirements/nfr-requirements.md` | 非機能要件一覧。性能・スケール・可用性・保守性を軽量に定義（過剰エンジニアリング回避） |
| `nfr-requirements/tech-stack-decisions.md` | 技術スタック決定。Python 3.11+ / FastAPI / uvicorn / SQLite / SQLAlchemy 2.x / Pydantic v2 の選定根拠 |
| `nfr-design/nfr-design-patterns.md` | NFR 設計パターン。レイヤードアーキテクチャ・依存性注入など軽量パターンの採用 |
| `nfr-design/logical-components.md` | 論理コンポーネント構成。Router / Schema / Service / Repository の役割とパターン対応表 |
| `infrastructure-design/infrastructure-design.md` | インフラ設計。論理コンポーネントをローカルマシン（uvicorn プロセス + SQLite ファイル）へマッピング |
| `infrastructure-design/deployment-architecture.md` | デプロイアーキテクチャ。ローカル単一プロセスのデプロイモデルとセットアップ手順 |
| `code/code-summary.md` | コード生成サマリ。生成した app/ 配下の全ファイル・役割・関連ストーリーの対応表 |

### construction/build-and-test（ビルド・テスト）

| ファイル名 | 概要 |
|---|---|
| `build-instructions.md` | ビルド手順。venv 作成・依存インストール・環境変数の説明 |
| `unit-test-instructions.md` | 単体テスト実行手順と結果（34 passed。重複判定境界・CRUD・予約 API の内訳） |
| `integration-test-instructions.md` | 統合テスト手順。router→service→repository→SQLite を通した E2E API フローの検証シナリオ |
| `performance-test-instructions.md` | 性能テスト手順。本格的な負荷試験はスコープ外とし、任意の簡易スモーク手順のみ記載 |
| `build-and-test-summary.md` | ビルド・テスト結果の総括。ビルド成功、全 34 テストパス |

