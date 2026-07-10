# 技術スタックの決定 (Tech Stack Decisions) — reservation-service

## 確定した技術スタック
| 領域 | 採用技術 | 根拠 |
|---|---|---|
| 言語 | Python 3.11+ | 制約（NFR-01）。3.11+ は型ヒント・パフォーマンス面で無難 |
| Web フレームワーク | FastAPI | 制約。自動 OpenAPI/Swagger、Pydantic バリデーション |
| ASGI サーバー | uvicorn | FastAPI の標準的な実行環境。ローカル起動が容易 |
| DB | SQLite | 制約。ファイル1つで完結、追加サーバー不要 |
| ORM | SQLAlchemy 2.x | Application Design 決定（Q-D2=A）。モデル定義が明確 |
| バリデーション/DTO | Pydantic v2 | FastAPI 標準。リクエスト/レスポンススキーマ |
| ID | UUID 文字列 | Application Design 決定（Q-D3=B） |
| テスト | pytest + httpx(TestClient) | ユニット＋APIテスト（Q-N2=A） |

## 依存パッケージ（requirements.txt 想定）
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
pytest
httpx
```
（バージョンは Code Generation で確定。過度なピン留めはしない）

## アーキテクチャ上の技術方針
- **レイヤ分離**: `router`（FastAPI）→ `service`（業務ロジック）→ `repository`（SQLAlchemy）→ SQLite。
- **DBセッション**: FastAPI の `Depends` でリクエストスコープのセッションを注入。
- **重複防止**: `service` 層で1トランザクション内に「重複チェック→挿入」（Q-F3=A）。
- **時刻**: ナイーブ datetime（ローカル）、API は ISO 8601 文字列。
- **設定**: DB ファイルパスを設定（既定 `./reservations.db`）。テストではインメモリ or 一時ファイル。

## 選定理由サマリ
すべて「制約に忠実」かつ「ワークショップの2〜3時間で完結」を最優先に選定。追加のインフラ・外部サービスは導入しない。
