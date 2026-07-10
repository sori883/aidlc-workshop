# Unit of Work Plan — 定期予約機能

## Approved Decomposition Decision（対話形式で取得、2026-07-10）

### Q1: 分解方針
単一ユニット / 複数ユニットに分割
[Answer]: 単一ユニット（`recurring-reservations`）

**理由**: 既存は単一 FastAPI モノリス。定期予約機能は US-R01〜R08 が共有データモデル（reservation_series / series_id）と共通オーケストレーション（RecurringReservationService）で強く結合しており、分割すると調整コストが増える。モノリスの定義（単一ユニット=論理モジュール群を含むアプリ全体）に従い1ユニットとする。

## Unit Definition

- **Unit 名**: `recurring-reservations`
- **種別**: Module（既存モノリス内の論理モジュール `app.series` + 既存モジュールへの後方互換変更）
- **含むストーリー**: US-R01, US-R02, US-R03, US-R04, US-R05, US-R06, US-R07, US-R08

## Execution Checklist（Part 2 で生成）

- [x] `unit-of-work.md` — ユニット定義と責務、含むコンポーネント/ストーリー、コード編成
- [x] `unit-of-work-dependency.md` — 依存マトリクス（単一ユニットの内部依存 + 既存モジュールへの依存）
- [x] `unit-of-work-story-map.md` — ストーリー↔ユニットのマッピング
- [x] ユニット境界と依存の検証
- [x] 全ストーリーがユニットに割当済みであることを確認

## Planning Questions（回答済み・曖昧さ分析）

- Story Grouping: 単一ユニットに全ストーリー集約（回答済み）。
- Dependencies: 既存 availability.service（不変）/ common / db.database に依存。ユニット内は service 中心の直接呼び出し。
- Team Alignment: 単一開発者/小チーム想定（ワークショップ）。
- Technical: デプロイ単位は既存モノリスと同一（独立デプロイ不要）。
- Business Domain: 「予約」境界づけられたコンテキスト内の定期予約サブ機能。
- **曖昧さ分析**: 回答は「単一ユニット」で明確。矛盾なし。フォローアップ不要。
