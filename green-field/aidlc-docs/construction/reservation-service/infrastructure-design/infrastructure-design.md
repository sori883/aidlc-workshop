# インフラ設計 (Infrastructure Design) — reservation-service

制約「ローカル実行で完結」に基づき、クラウド資源を用いず開発者のローカルマシンにマッピングする。

## 論理コンポーネント → インフラのマッピング
| 論理コンポーネント | インフラ実体 | 備考 |
|---|---|---|
| API Routers / Services / Repositories | Python プロセス（uvicorn） | 単一プロセスで全モジュールを内包 |
| DB Session Provider / ORM Engine | プロセス内 SQLAlchemy | — |
| データストア（rooms / reservations） | SQLite ファイル（例 `./reservations.db`） | 単一ファイル。プロセスと同一ホスト |
| API 公開 | localhost の TCP ポート（既定 8000） | 外部公開なし |
| ドキュメント/試行 UI | FastAPI Swagger UI（/docs） | 追加サーバー不要 |
| ログ | 標準出力（uvicorn/アプリログ） | 集約基盤なし |

## インフラ構成図（テキスト）

```
+------------------------------------------------+
|   開発者のローカルマシン (localhost)            |
|                                                |
|   +----------------------------+               |
|   |  uvicorn プロセス          |               |
|   |   FastAPI アプリ (app/)    |               |
|   |   - routers/services/repos |               |
|   +-------------+--------------+               |
|                 |  ファイルI/O                 |
|          +------v-------+                      |
|          | reservations |  (SQLite ファイル)   |
|          |    .db       |                      |
|          +--------------+                      |
|                                                |
|   HTTP: http://127.0.0.1:8000  (/docs で試行)  |
+------------------------------------------------+
```

## リソース要件
- **Compute**: 追加なし（ローカルPuの CPU/メモリで十分）。
- **Storage**: SQLite ファイル1つ（数MB想定）。
- **Network**: ループバック（127.0.0.1）。外部ポート開放・ファイアウォール設定は不要。
- **依存サービス**: なし（外部API・マネージドサービスに依存しない）。

## 環境変数 / 設定
| 設定 | 既定値 | 用途 |
|---|---|---|
| DATABASE_URL | `sqlite:///./reservations.db` | DB 接続先。テストで上書き可 |
| HOST | `127.0.0.1` | バインドアドレス |
| PORT | `8000` | 待受ポート |

## 対象外
- クラウド（AWS/Azure/GCP）資源、IaC（CDK/Terraform）
- コンテナ化（Docker）※任意で追加可能だが今回のコアには含めない
- ロードバランサ / API Gateway / CDN
- マネージド監視・ログ集約
