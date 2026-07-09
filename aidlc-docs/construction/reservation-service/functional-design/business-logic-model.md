# 業務ロジックモデル (Business Logic Model) — reservation-service

主要ユースケースのロジックフロー。技術非依存（ステータスコードは実装契約として併記）。

## UC-1: 会議室を登録する（US-01）
```
入力: name, capacity, equipment[], location
1. name 非空を検証           -> 失敗 400 (BR-R1)
2. capacity >= 0 を検証       -> 失敗 400 (BR-R2)
3. Room を採番(UUID)して永続化
出力: 201 Created + Room
```

## UC-2: 会議室を更新/削除する（US-03）
```
更新:
1. room_id 存在確認          -> 無ければ 404
2. name/capacity 検証         -> 失敗 400
3. 更新して 200 + Room
削除:
1. room_id 存在確認          -> 無ければ 404
2. active 予約の有無を確認    -> 1件でもあれば 409 (BR-R6)
3. 削除して 204
```

## UC-3: 会議室を予約する（US-04, US-05）★中核
```
入力: room_id, start_time, end_time, booker_name, booker_email?
[トランザクション開始]
1. start_time < end_time を検証        -> 失敗 400 (BR-C1)
2. booker_name 非空を検証              -> 失敗 400 (BR-C2)
3. room_id 存在確認                    -> 無ければ 404 (BR-C3)
4. start_time >= now を検証            -> 過去なら 400 (BR-C4)
5. 重複チェック has_conflict(room_id, start, end):
     対象会議室の status=active 予約を取得し、
     各予約に overlaps(s,e, start,end) を適用
     いずれか真 -> 409 (BR-C5, BR-OV)
6. Reservation を採番(UUID), status=active で挿入
[トランザクション終了/コミット]
出力: 201 Created + Reservation
```

## UC-4: 予約を一覧/取得する（US-06）
```
一覧:
1. 任意フィルタ room_id / from / to を適用
   (from/to 指定時は [from,to) に重なる予約, BR-L3)
2. 200 + list[Reservation]
取得:
1. reservation_id 存在確認 -> 無ければ 404
2. 200 + Reservation
```

## UC-5: 予約をキャンセルする（US-07）
```
入力: reservation_id
1. reservation_id 存在確認 -> 無ければ 404 (BR-X1)
2. status == active なら cancelled に更新 (BR-X2)
   status == cancelled ならそのまま（冪等） (BR-X3)
3. 200 + Reservation(status=cancelled)
```

## UC-6: 空いている会議室を検索する（US-08）
```
入力: start, end
1. start < end を検証 -> 失敗 400 (BR-A1)
2. 全 Room を取得
3. 各 Room について、status=active 予約で [start,end) に重なるものが無ければ「空き」
   (overlaps 判定, cancelled 除外, BR-A2/A3)
4. 空きRoomのみをリストに', 200 + list[Room]（該当なしは空リスト, BR-A4）
```

## 重なり判定関数 overlaps（純粋関数）
```
overlaps(s1, e1, s2, e2) := (s1 < e2) and (s2 < e1)
```
- 半開区間。隣接（e1==s2 または e2==s1）は False。
- この関数はプロパティテスト/ユニットテストの主対象。

## ストーリー受け入れ基準のカバレッジ検証
| ストーリー | カバーする業務ルール/UC |
|---|---|
| US-01 | UC-1, BR-R1/R2/R3/R4 |
| US-02 | UC-4 相当（Room版）, BR-R? / 一覧・取得 |
| US-03 | UC-2, BR-R5/R6 |
| US-04 | UC-3, BR-C1/C2/C3/C4 |
| US-05 | UC-3 step5, BR-C5/BR-OV（境界: 隣接OK/一致・内包・部分NG/別室OK/cancelled除外） |
| US-06 | UC-4, BR-L1/L2/L3/L4 |
| US-07 | UC-5, BR-X1/X2/X3 |
| US-08 | UC-6, BR-A1/A2/A3/A4 |

- [x] 全8ストーリーの受け入れ基準が業務ルール/UCでカバーされている。
