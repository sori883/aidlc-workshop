Q1: 2 | 全体拒否がユーザーの原子性選択である経緯を要件検証質問・audit・BR-RS-OV2・service.pyを引用して正確に説明。
Q2: 2 | 52=約1年（週次）の根拠を要件検証質問・FR-1.5・BR-RS-C7・コードを引用して要件確定として説明。
Q3: 2 | 既存API流用のユーザー選択（Q7）と個別回が通常Reservation行である仕組みを引用付きで正確に説明。
Q4: 2 | 純粋関数分離の理由（副作用隔離・PBT容易・overlaps踏襲）をdocstring・設計計画を引用して説明。
Q5: 2 | マイグレーションツール不採用とcreate_all整合・軽量ALTERヘルパ選択の経緯をaudit・infra-designを引用して説明。
Q6: 2 | hypothesis=PBT用でPartial選択の理由を要件検証質問・tech-stack・実装ファイルを引用して正確に説明。
Q7: 2 | 半開区間[start,end)で隣接共存可を overlaps・docstring・business-rulesを引用して正しく説明。
Q8: 2 | inclusiveで2030-01-15開始回が含まれることをrecurrence.py:48・BR-RS-C6を引用して正確に説明。
Q9: 2 | count/until両方指定・両方省略とも400をservice.py・recurrence.py・business-rulesを引用して正しく説明。
Q10: 2 | start==now許可（過去のみ拒否）をservice.py:72・コメント・BR-RS-C8を引用して正確に説明。
Q11: 2 | (a)(b)不変・(c)冪等200をcancel_series・list_future_active_by_series・X1/X2/X3を引用して正しく説明。
Q12: 2 | リクエスト不変・ReservationOutにseries_id追加のみをschemas・BR-RS-D1/D2を引用して正確に説明。
Q13: 2 | DB制約でなくアプリ層チェックでTOCTOU競合が起こりうる点を非ユニークインデックス含め引用付きで正確に説明。
Q14: 2 | ルートconftest.pyのbrownエイリアス登録と既存テスト改変不可制約をdocstring引用で正確に説明。
Q15: 2 | 起動時ALTER追加・新テーブル作成・2回目冪等をdatabase.py・infra-designを引用して正確に説明。
Q16: 2 | pip install→pytestで66件パスを実行確認済みとして内訳付きで正しく説明。
Q17: 2 | Pydantic通過後にservice層でmax_count+1生成→len>52で400検出をrecurrence.py・service.pyを引用して説明。
Q18: 2 | タイムゾーン変換は行われずナイーブ扱い・スコープ外と正しく否定（捏造なし）。
Q19: 2 | 週次固定で隔週・月次のパラメータは存在せずスコープ外と正しく否定（捏造なし）。
Q20: 2 | 認証機構自体が存在せずトークン有効期限設定箇所はないと正しく否定（捏造なし）。
TOTAL: 40
