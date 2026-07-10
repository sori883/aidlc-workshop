# Technology Stack

## Programming Languages
- Python - 3.13（`from __future__ import annotations` 使用、PEP 604 union 記法）- 全実装。

## Frameworks
- FastAPI - 最新（バージョン未固定）- REST API 層、依存性注入、OpenAPI/Swagger UI。
- Pydantic - >=2.0 - 入出力スキーマ検証（`model_validate`, `ConfigDict(from_attributes=True)`）。
- SQLAlchemy - >=2.0 - ORM（`Mapped` / `mapped_column`）、セッション管理。

## Infrastructure
- SQLite - 永続化データストア（既定 `sqlite:///./reservations.db`）。
- Uvicorn - ASGI サーバ（`uvicorn[standard]`）。

## Build Tools
- pip - 依存管理（`requirements.txt`）。ロックファイル・パッケージング設定なし。

## Testing Tools
- pytest - テストランナー。
- httpx - FastAPI TestClient の依存。
- FastAPI TestClient - API 結合テスト。
