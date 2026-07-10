# Tech Stack Decisions — recurring-reservations

## 方針
既存スタックを最大限継承し、新規追加は最小限（PBT フレームワークのみ）。

## 技術選定

| 分類 | 技術 | 決定 | 根拠 |
|---|---|---|---|
| 言語 | Python 3.13 | 継承 | 既存コードベース |
| API フレームワーク | FastAPI | 継承 | 既存の router 構成に新 router を追加 |
| バリデーション | Pydantic v2 | 継承 | 既存スキーマ方式（ConfigDict from_attributes） |
| ORM | SQLAlchemy 2.0 | 継承 | 既存モデル方式（Mapped/mapped_column） |
| DB | SQLite | 継承 | 既存。新テーブル `reservation_series` を追加 |
| テストランナー | pytest | 継承 | 既存テストと同一 |
| API テスト | FastAPI TestClient / httpx | 継承 | 既存の conftest 方式 |
| **PBT フレームワーク** | **Hypothesis** | **新規追加** | **PBT-09 準拠。Python 標準的、優れた shrinking、pytest 統合。日付生成・重複判定・往復に適用** |

## 依存関係の変更

`requirements.txt` に以下を追加（既存方針に合わせバージョン未固定）:
```
hypothesis
```
- 既存エントリ（fastapi / uvicorn[standard] / sqlalchemy>=2.0 / pydantic>=2.0 / pytest / httpx）は変更しない。

## トランザクション戦略
- SQLAlchemy Session の単一 `commit` でシリーズ作成を原子化（既存 `ReservationService.create_reservation` の commit パターンを踏襲）。重複検出時は commit せず、例外送出でロールバック。

## マイグレーション方針（Infrastructure Design で詳細化）
- 新テーブルは `Base.metadata.create_all`（既存 `create_all()`）で作成。
- 既存 `reservations` への `series_id` 列追加は、新規DBでは create_all で対応。既存DB（reservations.db）への適用手順は Infrastructure Design で扱う。

## PBT-09 検証
- [x] フレームワーク選定・文書化: Hypothesis
- [x] 依存追加予定: requirements.txt に hypothesis
- [x] カスタム生成器・shrinking・seed 再現性をサポート（Hypothesis 標準機能）
- [x] 単一言語（Python）のため単一フレームワークで充足
