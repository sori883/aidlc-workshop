# Story Generation Plan — 定期予約機能

## Approved Decisions（対話形式で取得、2026-07-10）

- **ブレイクダウン方針**: 機能ベース（作成 / シリーズキャンセル / 個別キャンセル / 照会・表示）
- **ペルソナ粒度**: 複数ペルソナ（一般予約者、会議室運用担当、API 連携開発者）
- **受け入れ基準形式**: Given-When-Then（BDD 風シナリオ形式）
- **ストーリー粒度**: 1機能=1〜複数ストーリー。境界条件（重複=全体拒否、過去日時、回数上限、未来回のみキャンセル、冪等性）は受け入れ基準のシナリオとして表現。
- **参照**: `aidlc-docs/inception/requirements/requirements.md`（FR-1〜FR-5, NFR-1〜NFR-5, C-1〜C-4）

## Planning Questions（回答済み）

### Q1: ブレイクダウン方針
機能ベース / ユーザージャーニー / ハイブリッド
[Answer]: 機能ベース

### Q2: ペルソナ粒度
複数ペルソナ / 単一ペルソナ
[Answer]: 複数ペルソナ

### Q3: 受け入れ基準形式
Given-When-Then / チェックリスト
[Answer]: Given-When-Then

## Story Approach Options（検討結果）

- **選択: 機能ベース (Feature-Based)** — システム機能単位でストーリーを編成。今回のスコープ（作成・シリーズキャンセル・個別キャンセル・表示）と直接対応し、実装ユニットへの写像が容易。
- 却下: ユーザージャーニーベース（境界条件の網羅が散漫になりやすい）、純ペルソナベース（機能重複が生じやすい）。
- 境界条件はジャーニー的観点も受け入れ基準に織り込むことで補完（ハイブリッド的補強）。

## Execution Checklist（Part 2 で実行）

- [x] `personas.md` を生成（複数ペルソナ: 一般予約者 / 運用担当 / API 連携開発者。特徴・動機・関わる機能を記述）
- [x] `stories.md` を機能ベースで生成:
  - [x] Epic: 定期予約シリーズの作成
    - [x] US-R01 定期予約シリーズの作成（count/until、週次生成）
    - [x] US-R02 重複時のシリーズ全体拒否（原子性、409）
    - [x] US-R03 作成時の入力検証（過去日時400・回数上限52・終了条件の一方指定）
  - [x] Epic: シリーズのキャンセル
    - [x] US-R04 シリーズ全体キャンセル（未来 active 回のみ、冪等）
    - [x] US-R05 個別回のキャンセル（既存キャンセル API 流用）
  - [x] Epic: 照会・表示
    - [x] US-R06 予約一覧・詳細でのシリーズ情報表示（series_id）
    - [x] US-R07（任意）シリーズ単位の照会
  - [x] Epic: 互換性維持（非機能・横断）
    - [x] US-R08 既存の単発予約 API・既存テストの不変性維持
- [x] 各ストーリーに Given-When-Then の受け入れ基準を付与
- [x] INVEST 準拠（Independent, Negotiable, Valuable, Estimable, Small, Testable）を確認
- [x] ペルソナを各ストーリーにマッピング
- [x] 要件（FR/NFR/C）へのトレーサビリティを付与

## Mandatory Story Artifacts

- [x] stories.md — INVEST 準拠のユーザーストーリー + Given-When-Then 受け入れ基準
- [x] personas.md — ユーザー原型と特徴
- [x] ペルソナ↔ストーリーのマッピング
- [x] 各ストーリーの受け入れ基準
