# Component Methods — 定期予約機能

> 注: メソッドシグネチャと高レベルの目的のみ記載。詳細な業務ルール（境界条件・検証順序）は Functional Design（CONSTRUCTION）で定義する。

## C-3: app.series.recurrence（純粋関数）

```python
def generate_occurrences(
    start_time: datetime,
    end_time: datetime,
    count: int | None,
    until: date | datetime | None,
    max_count: int = 52,
) -> list[tuple[datetime, datetime]]:
    ...
```
- **Purpose**: 起点 (start_time, end_time) を1回目とし、7日刻みで各回の (start, end) を生成。
- **終了条件**: `count` 指定なら合計 count 回。`until` 指定なら開始日が until 以下の回まで。どちらか一方のみ有効（両方/両方未指定は呼び出し側で 400）。
- **上限**: 生成数が `max_count` を超える場合は呼び出し側で 400 とするため、判定可能な情報（生成リストまたは件数）を返す。
- **入出力**: 純粋関数、DB 非依存。

（補助関数の候補。Functional Design で確定）
```python
def resolve_occurrence_count(start_time, count, until, max_count) -> int: ...
```

## C-2: app.series.service（RecurringReservationService）

```python
class RecurringReservationService:
    def __init__(self, db: Session) -> None: ...

    def create_series(
        self,
        room_id: str,
        start_time: datetime,
        end_time: datetime,
        booker_name: str,
        booker_email: str | None,
        count: int | None,
        until: date | datetime | None,
    ) -> ReservationSeries: ...   # 生成した series と全 occurrences を保持

    def cancel_series(self, series_id: str) -> ReservationSeries: ...

    def get_series(self, series_id: str) -> ReservationSeries: ...  # 任意 US-R07
```
- **create_series**: 検証 → recurrence.generate_occurrences → 会議室存在確認 → 各回 has_conflict → 1回でも重複なら ConflictError（全体拒否）→ series + 全 Reservation を単一トランザクションで登録。
- **cancel_series**: series 存在確認 → 未来の active 回のみ cancelled（冪等）→ commit。
- **get_series**: series と全回を取得（未存在は NotFoundError）。

## C-5: app.series.repository（SeriesRepository）

```python
class SeriesRepository:
    def __init__(self, db: Session) -> None: ...
    def add(self, series: ReservationSeries) -> ReservationSeries: ...
    def get(self, series_id: str) -> ReservationSeries | None: ...
```

## C-8: app.reservations.repository（追加メソッド）

```python
def list_by_series(self, series_id: str) -> list[Reservation]: ...
def list_future_active_by_series(self, series_id: str, now: datetime) -> list[Reservation]: ...
```
- 既存メソッド（add/get/list/list_active_by_room）は不変。

## C-1: app.series.router（エンドポイント）

```python
@router.post("", response_model=RecurringReservationOut, status_code=201)   # POST /reservations/recurring
def create_recurring(payload: RecurringReservationCreate, db=Depends(get_db)): ...

@router.post("/{series_id}/cancel", response_model=SeriesOut)               # POST /reservations/recurring/{series_id}/cancel
def cancel_recurring(series_id: str, db=Depends(get_db)): ...

@router.get("/{series_id}", response_model=SeriesOut)                       # GET /reservations/recurring/{series_id}（任意）
def get_recurring(series_id: str, db=Depends(get_db)): ...
```
- router prefix = `/reservations/recurring`。既存 `/reservations` router とパスが衝突しないことを確認済み（`recurring` は2セグメント以上で単発の `/{reservation_id}` と非衝突）。

## C-7: app.reservations.schemas（変更）

```python
class ReservationOut(BaseModel):
    ...
    series_id: str | None   # 追加。単発予約は None
```
- **ReservationCreate は不変**（C-1）。
