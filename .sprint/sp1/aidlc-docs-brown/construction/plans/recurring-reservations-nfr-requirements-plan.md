# NFR Requirements Plan — recurring-reservations

## Approved Decisions（対話形式で取得、2026-07-10）

### Q1: PBT フレームワーク（PBT-09 強制）
[Answer]: Hypothesis を追加（requirements.txt に hypothesis 追加）

### Q2: 依存バージョン固定方針
[Answer]: 既存方針を踏襲（未固定。既存 requirements.txt のスタイルを維持）

## Context
- 技術スタックは既存を継承（Python 3.13 / FastAPI / SQLAlchemy 2.0 / SQLite / pytest / httpx）。新規追加は hypothesis のみ。
- Security/Resiliency 拡張は無効。PBT は Partial（PBT-02/03/07/08/09 強制）。

## Execution Checklist
- [x] nfr-requirements.md — 本ユニットの NFR（原子性・後方互換・信頼性・保守性・テスト）
- [x] tech-stack-decisions.md — 技術選定と根拠（既存継承 + hypothesis）

## 曖昧さ分析
- 回答は明確・矛盾なし。フォローアップ不要。
