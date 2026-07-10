# Functional Design Plan — recurring-reservations

## Approved Business-Logic Decisions（対話形式で取得、2026-07-10）

### Q1: 終了日 until の境界
[Answer]: 開始日 <= until（inclusive）。until は日付（date）として扱う。各回の開始日が until 以下の回まで生成。

### Q2: シリーズ全体キャンセルの「未来の回」
[Answer]: 開始時刻 > 現在（start_time > now）。既に開始した/開始時刻ちょうどの回は対象外。既存の予約過去判定と一貫。

### Q3: US-R07（シリーズ照会）の実装
[Answer]: 含める。GET /reservations/recurring/{series_id} でメタ情報 + 全回を返す。

## Execution Checklist

- [x] business-logic-model.md — 週次生成・原子的作成・シリーズキャンセルのアルゴリズム
- [x] business-rules.md — BR-RS*（作成/検証/重複/キャンセル/表示）
- [x] domain-entities.md — ReservationSeries / Reservation（series_id）のエンティティ定義
- [x] Testable Properties（PBT-01, Partial では助言扱い）を各コンポーネントに付与
- [x] 既存 business-rules（BR-C*/BR-X*/BR-OV/BR-A）との一貫性確認

## 曖昧さ分析
- 3問とも明確な選択で回答。矛盾なし。フォローアップ不要。
