調査が完了しました。以下の通り回答します。

**Q1. 共存できます。**
重複判定は半開区間 `[start, end)` で行われており、判定関数は `overlaps()`（`app/availability/service.py:14-19`）で `start_a < end_b and start_b < end_a` と実装されています。片方の予約の終了時刻（10:00）ともう一方の開始時刻（10:00）が一致する「隣接」のケースでは `start_b < end_a` が `10:00 < 10:00` で False になるため、重なりとは判定されません。同ファイルの docstring にも「隣接（end_a == start_b など）は重ならない扱い（半開区間）」と明記されています。予約作成時の重複チェックはこの関数を使う `AvailabilityService.has_conflict()` 経由で行われます（`app/reservations/service.py:44`）。

**Q2. 52回です。**
定数 `MAX_OCCURRENCES = 52` が `app/series/service.py:22` で定義されており、シリーズ作成時に `app/series/service.py:67-70`（BR-RS-C7）で「繰り返し回数が上限（52回）を超えています。」として検証されます。また、発生回生成関数 `generate_occurrences` のデフォルト引数 `max_count: int = 52` にも同じ値があります（`app/series/recurrence.py:18`。呼び出し側が超過を件数で検出できるよう最大 `max_count + 1` 件まで生成する設計）。

**Q3. 分からない（レート制限は実装されていないと判断します）。**
リポジトリ内を確認した限り、レート制限・スロットリングの実装は存在しません。予約作成エンドポイント（`app/reservations/router.py:16-18` の `POST /reservations`）には DB セッション以外の依存はなく、アプリのエントリポイント `app/main.py` にもレート制限用のミドルウェアや slowapi 等のライブラリ登録はありません。`app/` 配下および `aidlc-docs/` 配下を「rate limit / throttle / レート / スロットリング / 429」で検索してもヒットしませんでした。したがって「どこでどのように実装されているか」に該当する箇所は見つからず、現状は未実装というのが根拠に基づく答えです。
