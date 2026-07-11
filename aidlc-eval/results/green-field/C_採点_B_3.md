Q1: 2 | Visionの未確定論点→要件Q1でユーザーが全体拒否を選択した経緯とBR-RS-OV2・コード根拠を明示。
Q2: 2 | 要件Q4でのユーザー選択（上限52=約1年）とBR-RS-C7・MAX_OCCURRENCES根拠を提示。
Q3: 2 | 各回が通常Reservation行で既存cancelAPI流用、Q7決定・BR-RS-I1を引用。
Q4: 2 | Functional Core思想・NFR-3・overlaps踏襲を根拠ファイル付きで説明。
Q5: 2 | create_all方針・冪等自動ALTERヘルパ採用理由と設計文書・コード根拠を提示。
Q6: 2 | PBTフレームワークかつPartialオプトイン決定と適用対象・根拠を明示。
Q7: 2 | 半開区間[start,end)で隣接OKをoverlaps・BR-RS-OV1根拠で正答。
Q8: 2 | inclusiveで含まれることを厳密な>判定とBR-RS-C6で正答。
Q9: 2 | 両指定・両省略とも400、排他判定の二重ガードとBR-RS-C4を提示。
Q10: 2 | start==now許可（<のみ拒否）をBR-RS-C8・コードで正答、追加注釈も誤りでない。
Q11: 2 | (a)(b)不変・(c)冪等200をlist_future_active_by_series・BR-RS-X1/2/3で正答。
Q12: 2 | リクエスト不変・レスポンスにseries_id追加、C-1制約と根拠を明示。
Q13: 2 | DB制約でなくアプリ層チェックでTOCTOU競合ありをコード根拠で正答。
Q14: 2 | ルートconftestのbrownエイリアスとC-4理由を根拠付きで説明。
Q15: 2 | 列ALTER＋新テーブル作成・2回目冪等を database.py 等根拠で正答。
Q16: 2 | 手順と66件パスを実行確認込みで正答（条件Aでの実行補完に相当）。
Q17: 2 | 53件で打ち切り→service層件数チェックで400をコード根拠で正答。
Q18: 2 | 変換は行われていない（ナイーブdatetime・スコープ外）と正しく否定。
Q19: 2 | 週次固定で隔週・月次不可・パラメータ無しと正しく否定。
Q20: 2 | 認証機構自体が存在せずと正しく否定。
TOTAL: 40
