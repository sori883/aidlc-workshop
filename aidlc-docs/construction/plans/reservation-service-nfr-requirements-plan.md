# NFR Requirements 計画 — Unit-1: reservation-service

## 前提（制約により確定済み）
- 技術スタック: Python + FastAPI + SQLite（NFR-01）
- ローカル完結、REST API のみ、フロントエンド不要（NFR-02）
- 拡張機能（Security / PBT / Resiliency）はすべて無効
- 性能・可用性・スケール要件は最小（社内・少人数・ローカル）

## 質問（ユーザー回答）

### Q-N1: 想定同時利用規模
どの程度の同時実行を想定しますか？

A) 少人数・低同時実行（数名が時々操作する程度）。単一プロセスで十分（推奨）

B) それなりの同時実行を想定（多数が同時に予約する）。競合対策をより強めに

X) Other

[Answer]: A

### Q-N2: テスト方針
テストはどの程度用意しますか？

A) pytest で重複防止ロジックを中心にユニット＋APIテスト（推奨・ワークショップに適切）

B) 最小限（重複防止のユニットテストのみ）

X) Other

[Answer]: A

## 実行チェックリスト（回答確定後に実行）
- [x] nfr-requirements.md 生成
- [x] tech-stack-decisions.md 生成
