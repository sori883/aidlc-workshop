# ドメインエンティティ (Domain Entities) — reservation-service

技術非依存のドメインモデル。ID はすべて UUID 文字列。時刻は ISO 8601（ローカルタイム、ナイーブ）で扱う。

## Entity: Room（会議室）
| 属性 | 型 | 説明 | 制約 |
|---|---|---|---|
| id | str (UUID) | 会議室ID | 主キー、システム採番 |
| name | str | 会議室名 | 必須、空不可 |
| capacity | int | 収容人数 | 0 以上の整数 |
| equipment | list[str] | 設備（例: プロジェクター） | 0件以上、任意 |
| location | str | 場所（例: 3F 東） | 任意（空文字許容） |
| created_at | datetime | 作成日時 | システム採番 |

## Entity: Reservation（予約）
| 属性 | 型 | 説明 | 制約 |
|---|---|---|---|
| id | str (UUID) | 予約ID | 主キー、システム採番 |
| room_id | str (UUID) | 予約対象の会議室 | 必須、既存 Room を参照 |
| start_time | datetime | 開始時刻 | 必須、分単位 |
| end_time | datetime | 終了時刻 | 必須、start_time より後 |
| booker_name | str | 予約者名 | 必須、空不可 |
| booker_email | str \| None | 予約者メール | 任意 |
| status | enum(active, cancelled) | 予約状態 | 既定 active |
| created_at | datetime | 作成日時 | システム採番 |

## 関係 (Relationships)
- Room 1 --- 0..* Reservation（1つの会議室は複数の予約を持ちうる）。
- Reservation は必ず1つの Room を参照する（room_id 必須）。

## 状態遷移 (Reservation.status)

```
[作成] --> active --(cancel)--> cancelled
                 <--(再cancelは冪等: cancelledのまま成功)
```

- active: 有効な予約。重複判定・空き検索の対象。
- cancelled: キャンセル済み。重複判定・空き検索の対象外。復活はしない。

## 値の扱い
- **時刻**: ナイーブな datetime（ローカルタイム前提）。API 入出力は ISO 8601 文字列。
- **半開区間**: 予約時間は `[start_time, end_time)` として扱う（終了時刻は含まない）。
