# Application Design Plan — 定期予約機能

## Approved Design Decisions（対話形式で取得、2026-07-10）

### Q1: コンポーネント配置
新規 app.series モジュール / reservations 内に追加
[Answer]: 新規 app.series モジュール（router/service/schemas/repository/recurrence の縦割り構成、既存モジュールと一貫）

### Q2: 週次日付生成・終了条件解決の配置
純粋関数モジュールに切出し / service 内メソッド
[Answer]: 純粋関数モジュールに切出し（`app/series/recurrence.py`。`overlaps` と同じ設計思想。単体テスト/PBT が容易）

### Q3: 永続化アクセス（リポジトリ）
新規 SeriesRepository / ReservationRepository 拡張のみ
[Answer]: 新規 SeriesRepository（`reservation_series` 専用。既存 ReservationRepository は series_id 検索メソッドを追加）

## Design Scope

- **対象**: 週次定期予約の作成・シリーズ全体キャンセル・（任意）シリーズ照会。個別回キャンセルは既存 API 流用のため新規コンポーネント不要。
- **再利用**: `AvailabilityService.has_conflict`（重複判定、変更なし）、`common.exceptions`（例外）、`db.database`（セッション）。
- **参照**: requirements.md（FR/NFR/C）、stories.md（US-R01〜R08）。

## Execution Checklist（成果物生成）

- [x] components.md — コンポーネント定義と高レベル責務
  - [x] app.series（router/service/schemas/repository/recurrence）
  - [x] db.models 変更（ReservationSeries、Reservation.series_id）
  - [x] reservations.schemas 変更（ReservationOut に series_id）
  - [x] 再利用: availability.service, common, db.database
- [x] component-methods.md — メソッドシグネチャと入出力（業務ルール詳細は Functional Design へ）
- [x] services.md — サービス定義とオーケストレーション
- [x] component-dependency.md — 依存マトリクス・通信パターン・データフロー
- [x] application-design.md — 上記を統合
- [x] 設計の完全性・一貫性の検証（既存契約・半開区間・既存テスト不変の確認）

## PBT-01 メモ（Functional Design で詳細化）
- recurrence の日付生成: Invariant（生成数=count、7日間隔）、シリアライズ往復（schemas）は Round-trip 候補。
