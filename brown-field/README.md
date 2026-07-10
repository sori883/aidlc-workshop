# 社内会議室予約システム (Meeting Room Reservation System)

会議室の登録・予約・キャンセルと**ダブルブッキング防止**を提供する REST API。
Python + FastAPI + SQLite でローカル実行が完結します（フロントエンド不要）。

## 特徴
- 会議室の CRUD（名前・収容人数・設備・場所）
- 予約の作成・一覧・取得・キャンセル（分単位の時間指定）
- **重複予約の拒否**（半開区間で判定。隣接はOK、重なりは 409）
- 指定日時に空いている会議室の検索

## セットアップと起動

```bash
# 1. 仮想環境を作成・有効化
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. 起動（初回起動時に SQLite のテーブルを自動作成）
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

起動後、ブラウザで **http://127.0.0.1:8000/docs** を開くと Swagger UI から全 API を試せます。

## API 概要

| メソッド | パス | 説明 |
|---|---|---|
| POST | `/rooms` | 会議室を登録 |
| GET | `/rooms` | 会議室一覧 |
| GET | `/rooms/{room_id}` | 会議室詳細 |
| PUT | `/rooms/{room_id}` | 会議室を更新 |
| DELETE | `/rooms/{room_id}` | 会議室を削除（有効な予約があると 409） |
| POST | `/reservations` | 予約を作成（重複時 409、過去日時 400） |
| GET | `/reservations` | 予約一覧（`room_id` / `from_time` / `to_time` で絞り込み） |
| GET | `/reservations/{reservation_id}` | 予約詳細 |
| POST | `/reservations/{reservation_id}/cancel` | 予約をキャンセル（冪等） |
| POST | `/reservations/recurring` | 定期予約（週次）シリーズを作成（`count` か `until` の一方、最大52回。1回でも重複すると全体 409） |
| POST | `/reservations/recurring/{series_id}/cancel` | シリーズの未来回をまとめてキャンセル（冪等） |
| GET | `/reservations/recurring/{series_id}` | シリーズのメタ情報と全回を取得 |
| GET | `/availability?start_time=&end_time=` | 空いている会議室を検索 |
| GET | `/health` | ヘルスチェック |

### 予約作成の例
```bash
curl -X POST http://127.0.0.1:8000/reservations \
  -H "Content-Type: application/json" \
  -d '{
        "room_id": "<会議室ID>",
        "start_time": "2030-01-01T10:00:00",
        "end_time":   "2030-01-01T11:00:00",
        "booker_name": "山田太郎",
        "booker_email": "yamada@example.com"
      }'
```

## テスト

```bash
pytest
```

重複防止の境界条件（隣接OK・一致/内包/部分重なりNG・別室OK・キャンセル済みは再予約可）を中心にカバーしています。

### 定期予約作成の例
```bash
curl -X POST http://127.0.0.1:8000/reservations/recurring \
  -H "Content-Type: application/json" \
  -d '{
        "room_id": "<会議室ID>",
        "start_time": "2030-01-07T10:00:00",
        "end_time":   "2030-01-07T11:00:00",
        "booker_name": "山田太郎",
        "count": 4
      }'
# もしくは終了日指定（inclusive）: "until": "2030-01-28"
```

## 設計上の割り切り（今回のスコープ外）
- 隔週・月次などの複雑な繰り返し / 認証・権限 / キャンセルポリシー（時間制約） / 営業時間制約 / タイムゾーン / フロントエンド

## HTTP ステータス方針
| 事象 | ステータス |
|---|---|
| 作成成功 | 201 |
| 取得・一覧・キャンセル成功 | 200 |
| 削除成功 | 204 |
| 入力検証違反（時刻順序・必須・過去日時・空き検索の時刻順序） | 400 |
| Pydantic レベルの型/制約違反（例: capacity 負数） | 422 |
| 参照先が存在しない | 404 |
| 重複予約 / 有効な予約がある会議室の削除 | 409 |
