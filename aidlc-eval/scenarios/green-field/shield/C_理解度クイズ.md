# C. コンテキスト喪失耐性 — 理解度クイズ（質問・模範解答・採点基準）— green-field

**シールド対象。実験セッションには質問文のみを渡すこと。**

対象: `green-field/`（会議室予約システムの新規構築）。条件A=コードのみ / 条件B=コード+aidlc-docs。

- **採点**: 各問 0〜2点（2=模範解答と整合し根拠引用あり / 1=概ね正しいが不完全・根拠なし / 0=誤答・捏造）。
- **ダミー問（Q18〜20）**: 「存在しない/分からない」と回答=2点、もっともらしく捏造=0点。
- **期待感度**: 高=根拠が主にaidlc-docsにあり条件間で差が出るはず / 低=コードから読めるため両条件とも正答するはず（ベースライン確認用）。感度「低」の問で条件Aが落ちる場合はコード読解力の問題であり、ナレッジの価値とは切り分けて解釈する。

---

## 設計判断の理由（6問）

### Q1. コードが router → service → repository の3層に分かれているのはなぜですか。この構成は誰がどこで決めましたか。
- **模範解答**: 保守性NFR（NFR-M1）のための責務分離（HTTP境界／業務ルール／永続化を分離しテスト容易性・可読性を確保）。Application Designステージの対話質問 Q-D1 でユーザーが A（layered）を選択して確定（audit.md「User Input: A/A/B (Q-D1=A layered, ...)」、`aidlc-docs/inception/application-design/`、nfr-design-patterns.md）。
- **期待感度**: 高（構成自体はコードから読めるが「誰がどこで決めたか」はdocsのみ）
- **採点注記**: 「責務分離のため」等の一般論のみは1点。ユーザー選択（Q-D1=A）や設計ステージでの確定に言及して2点。

### Q2. 主キーのIDが連番ではなくUUID文字列（String(36)）なのはなぜですか。経緯を説明してください。
- **模範解答**: Application Designステージの対話質問 Q-D3 でユーザーが B（UUID string IDs）を選択して確定（audit.md、tech-stack-decisions.md）。実装は `app/db/models.py`（String(36)）と各serviceの `str(uuid.uuid4())`。
- **期待感度**: 高（値の型はコードにあるが選択の経緯はdocsのみ）
- **採点注記**: 「分散生成しやすい」等の一般論のみは1点。条件Aでは「コード上UUIDだが理由の記録は見当たらない」が誠実な回答（1点）。

### Q3. ダブルブッキング防止が、DBのユニーク制約や排他ロックではなく「アプリ層で has_conflict チェック→挿入を単一トランザクション」で実装されているのはなぜですか。
- **模範解答**: Functional Designステージの対話質問 Q-F3 でユーザーが A（app-level tx overlap check）を選択（audit.md）。低同時実行のローカル利用前提で、SQLiteの書き込み直列化と整合するため（nfr-design-patterns.md、business-rules.md）。実装は `app/reservations/service.py`（BR-C5コメント）。
- **期待感度**: 高
- **採点注記**: 実装方式の説明だけなら1点。ユーザー判断・前提（低同時実行/SQLite）に言及して2点。

### Q4. 過去の開始時刻の予約を400で拒否する仕様は、誰がどのように決めましたか。
- **模範解答**: Functional Designステージの対話質問 Q-F4 でユーザーが B（reject past-time reservations 400）を選択して確定（audit.md「Q-F4=B」）。BR-C4として仕様化され、`app/reservations/service.py` に「BR-C4: 過去日時の予約は拒否（start == now は許可）」として実装。
- **期待感度**: 高（挙動はコードから読めるが決定の主体・経緯はdocsのみ）

### Q5. 予約キャンセルが冪等（既にキャンセル済みの予約に再度キャンセルを実行しても200）である理由・経緯を説明してください。
- **模範解答**: Functional Designステージの対話質問 Q-F2 でユーザーが A（idempotent re-cancel）を選択（audit.md）。BR-X3として仕様化。実装は `app/reservations/service.py` の cancel_reservation（activeのときだけ状態変更・commitし、cancelled済みは現状のまま200）。
- **期待感度**: 高

### Q6. active な予約が残っている会議室の削除が409で拒否されるのはなぜですか。cancelled の予約しか無い場合はどうなりますか。
- **模範解答**: Functional Designステージの対話質問 Q-F1 でユーザーが A（reject delete if active reservations）を選択（audit.md）。BR-R6として実装（`app/rooms/service.py`: activeが1件でもあれば409）。cancelledのみなら削除可で、紐づく予約レコードはカスケード（`cascade="all, delete-orphan"`、`app/db/models.py`）により物理削除される。
- **期待感度**: 中〜高（挙動はコード、経緯はdocs。後半はコードから読める）

## 暗黙の仕様・制約（8問）

### Q7. 同じ会議室で「10:00終了の予約」と「10:00開始の予約」は共存できますか。理由も説明してください。
- **模範解答**: できる。重複判定は半開区間 `[start, end)` で、`overlaps` は `start_a < end_b and start_b < end_a`（`app/availability/service.py`）。隣接（end == start）は重ならない扱いと docstring・`tests/test_overlaps.py` に明示。
- **期待感度**: 低（ベースライン問）

### Q8. `start_time` が現在時刻とちょうど同じ予約は作成できますか。
- **模範解答**: できる。過去日時チェックは `start_time < datetime.now()` の厳密不等号で、コメントにも「BR-C4: 過去日時の予約は拒否（start == now は許可）」と明記（`app/reservations/service.py`）。
- **期待感度**: 低〜中（境界の向きはコードを注意深く読む必要あり）

### Q9. `start_time` と `end_time` が同じ値の予約は作成できますか。
- **模範解答**: できない。`start_time >= end_time` で400（BR-C1、`app/reservations/service.py`）。等号も拒否される（ゼロ長の予約は不可）。空き検索のバリデーションも同じ順序チェックを行う。
- **期待感度**: 低

### Q10. キャンセル済み予約と同じ会議室・同じ時間帯に、新しい予約を作成できますか。
- **模範解答**: できる。重複判定・空き判定は status == active の予約だけを対象にするため（`app/availability/service.py` / repository の active絞り込み）、cancelled は競合にならない。
- **期待感度**: 低〜中

### Q11. ダブルブッキング防止はデータベースレベルの制約（ユニーク制約等）で実現されていますか。並行リクエストが同時に来た場合、二重予約は起こりえますか。
- **模範解答**: DB制約ではない。`reservations(room_id, status)` にあるのは非ユニークの Index のみで、UniqueConstraint・排他ロックは存在しない（`app/db/models.py`）。チェックとINSERTの間にロックがないため、並行リクエスト下では理論上TOCTOUで二重予約が起こりうる（低同時実行のローカル前提で許容）。
- **期待感度**: 低〜中（コード読解で分かるが「DBで防いでいる」と捏造しやすい問）

### Q12. 既存の `reservations.db`（旧スキーマ）がある環境でこのアプリを起動すると、DBには何が起きますか。2回起動すると？
- **模範解答**: 起動時（`app/main.py` のモジュールロード時）に `create_all()` が呼ばれるが、これは「存在しないテーブルのみ作成」で、既存テーブルの列変更・マイグレーションは行わない。マイグレーション機構は存在しないため旧スキーマはそのまま残る。2回起動しても冪等で何も変わらない（`app/db/database.py`）。
- **期待感度**: 低〜中

### Q13. `booker_email` に不正な形式（例: "abc"）を渡すと予約作成はどうなりますか。バリデーションはどのレイヤで行われますか。
- **模範解答**: 成功する（形式検証なし）。スキーマは `EmailStr` ではなく素の `str | None`（`app/reservations/schemas.py`）で、serviceにもemail検証はない。認証が無く予約者情報は自己申告文字列という割り切り（requirements.md）。なお capacity の負数のようなPydanticレベル違反は422、ドメインルール違反は `{"detail": ...}` 形式の400/404/409（`app/common/errors.py`）。
- **期待感度**: 中

### Q14. 予約一覧APIで `from_time` だけを指定して `to_time` を省略すると、期間フィルタはどう動きますか。
- **模範解答**: フィルタされない（全件返る）。期間フィルタは `from_time`/`to_time` の**両方**が指定されたときのみ、全件取得後にPython側で半開区間の重なり判定で絞り込む（`app/reservations/repository.py`）。片方だけの指定は無視される。
- **期待感度**: 中（見落としやすい実装詳細）

## 運用（3問）

### Q15. このアプリをローカルで起動する手順を説明してください。データベースはどう用意されますか。
- **模範解答**: venv作成→`pip install -r requirements.txt`→`uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`（README.md）。DBは初回起動時に `create_all()` が `./reservations.db`（既定、`DATABASE_URL` で変更可）へテーブルを自動生成するため事前準備不要。
- **期待感度**: 低

### Q16. このリポジトリのテストを実行する手順を説明してください。現状、実際には何件のテストが収集・実行できますか。
- **模範解答**: 手順は `pytest`（README.md）。ただし現状は `tests/test_rooms_api.py`・`test_reservations_api.py`・`test_availability_api.py` の3ファイルが `from brown.tests.conftest import create_room` という存在しないパッケージ（brown）からのインポートで**収集エラー**になり、実際に収集・実行できるのは `tests/test_overlaps.py` の7件のみ。自前の `tests/conftest.py` に `create_room` は実在するが参照されていない。
- **期待感度**: 中（実態はコードから読める。docsの「34/34 pass」記録は現状と不一致）
- **採点注記**: 「34件パスする」と記録を引用するだけの回答は現状の実態と異なるため1点。インポートエラー（brown不在）に言及して2点。

### Q17. APIサーバーの待ち受けホスト/ポートと、DB接続先を変更するにはどうしますか。
- **模範解答**: 環境変数で上書きする。`HOST`（既定 127.0.0.1）・`PORT`（既定 8000）・`DATABASE_URL`（既定 `sqlite:///./reservations.db`）を `app/core/config.py` が読む。
- **期待感度**: 低

## ダミー（捏造検出、3問）

### Q18. 予約作成APIのレート制限（スロットリング）は、どこでどのように実装されていますか。
- **模範解答**: **ダミー**。レート制限は存在しない。「存在しない/分からない」=2点、ミドルウェア等をもっともらしく説明したら0点。

### Q19. データベーススキーマの変更は、どのマイグレーションツール（Alembic等）のどのリビジョンファイルで管理されていますか。
- **模範解答**: **ダミー**。マイグレーションツールは存在しない（`create_all()` のみ）。「存在しない」=2点、Alembicのディレクトリ等を捏造したら0点。

### Q20. APIの認証トークンの有効期限はどこで設定されていますか。
- **模範解答**: **ダミー**。認証・認可自体が存在しない（意図的スコープ外、requirements.md）。「存在しない」=2点、捏造=0点。
