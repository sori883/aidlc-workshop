Q1: 2 | 要件確認Q1でユーザーがA案（全体拒否・原子性優先）を選択した経緯に言及し根拠ファイルを引用している。
Q2: 2 | 要件確認Q4での上限決定（52=約1年）に言及しservice.py/recurrence.pyを引用している。
Q3: 2 | 各回が通常Reservation行で既存cancel APIが流用される点と要件Q7・BR-RS-I1を引用している。
Q4: 2 | 純粋関数分離によるテスト容易性・PBT対応とoverlapsと同思想の踏襲をdocstring/NFR引用で説明している。
Q5: 2 | create_all踏襲とインフラ設計での軽量ALTERヘルパ選択に言及しinfrastructure-design.mdを引用している。
Q6: 2 | PBTフレームワークでありQ13でPartial選択された経緯とPBT項目を根拠付きで説明している。
Q7: 2 | 半開区間[start,end)で隣接OKと正答しavailability/service.pyを引用している。
Q8: 2 | inclusiveで含まれると正答しrecurrence.pyのbreak条件を引用している。
Q9: 2 | 両方指定・両方省略とも400と正答し排他判定箇所を引用している。
Q10: 2 | start==nowは許可（厳密past のみ拒否）と正答しservice.pyを引用している。
Q11: 2 | (a)(b)対象外で不変、(c)冪等200と正答しrepository/serviceを引用している。
Q12: 2 | リクエスト不変・series_id追加のみと正答しschemasを引用している。
Q13: 2 | DB制約でなくアプリ層チェックでTOCTOU競合ありと正答し根拠を引用している。
Q14: 2 | ルートconftest.pyのbrownエイリアス登録とC-4制約を根拠付きで説明している。
Q15: 2 | ALTER列追加＋新テーブル作成、2回目は冪等と正答しdatabase.pyを引用している。
Q16: 2 | venv→pip→pytestで66件パスと正答している。
Q17: 2 | サービス層で max_count+1生成→len>52判定の2段構えと正答し根拠を引用している。
Q18: 2 | タイムゾーン変換は行われずスコープ外と正しく否定している。
Q19: 2 | 週次固定で隔週・月次は不可・パラメータ無しと正しく否定している。
Q20: 2 | 認証未実装で設定箇所は存在しないと正しく否定している。
TOTAL: 40
