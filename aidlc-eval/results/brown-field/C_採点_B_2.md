Q1: 2 | 全体拒否をユーザーが要件確認Q1で選択した経緯に言及し、BR-RS-OV2やservice.pyを引用している。
Q2: 2 | 52回=約1年の週次で要件確認Q4での確定に言及し、根拠ファイルを引用している。
Q3: 2 | 各回が通常Reservation行で既存キャンセルAPI流用（BR-RS-I1, Q7選択）を説明し引用あり。
Q4: 2 | 純粋関数分離によるテスト/PBT容易化とP-3パターンを説明しdocstring・nfr-design-patternsを引用。
Q5: 2 | create_all踏襲・軽量ALTERヘルパ採用の設計判断をinfra-design等の引用付きで説明。
Q6: 2 | PBTフレームワーク導入とPartial選択（Q13）を要件・audit・テストファイル引用で説明。
Q7: 2 | 半開区間[start,end)で隣接OKと正しく説明し、service.py・READMEを引用。
Q8: 2 | untilはinclusiveで境界回が含まれると説明しrecurrence.pyを引用。
Q9: 2 | 両方指定・両方省略とも400、service層とrecurrence.pyの二重防御を引用付きで説明。
Q10: 2 | start==nowは許可（過去のみ拒否）と正しく説明しservice.py・BR-RS-C8を引用。
Q11: 2 | (a)(b)不変、(c)冪等200を正しく説明しservice.py・business-rulesを引用。
Q12: 2 | リクエスト不変・series_id追加のみの後方互換変更を正しく説明し引用あり。
Q13: 2 | DB制約でなくアプリ層チェックでTOCTOU競合の可能性を正しく説明し引用あり。
Q14: 2 | ルートconftest.pyのbrownエイリアス登録とC-4での既存テスト不変更を説明し引用あり。
Q15: 2 | create_allでの列ALTER追加とreservation_series作成、2回目の冪等性を正しく説明し引用あり。
Q16: 2 | pytestで66件パスを実行確認し内訳も示している。
Q17: 2 | max_count+1(=53)生成後にservice層で>52検出し400を返すと正しく説明し引用あり。
Q18: 2 | タイムゾーン変換は行われずスコープ外と正しく答えている。
Q19: 2 | 週次固定で隔週・月次は指定不可・スコープ外と正しく答えている。
Q20: 2 | 認証未実装でトークン有効期限設定は存在しないと正しく答えている。
TOTAL: 40
