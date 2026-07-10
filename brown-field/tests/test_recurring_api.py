"""定期予約 API テスト（US-R01〜US-R08）。既存規約に合わせ brown.tests.conftest を利用。"""
from datetime import date, datetime, timedelta

from brown.tests.conftest import create_room


def next_monday(weeks: int = 0) -> datetime:
    """翌日以降の直近月曜 10:00 を基準に、weeks 週後の月曜 10:00 を返す（過去日時回避）。"""
    base = datetime.now() + timedelta(days=1)
    base = base.replace(hour=10, minute=0, second=0, microsecond=0)
    # 月曜(0)まで進める
    while base.weekday() != 0:
        base += timedelta(days=1)
    return base + timedelta(weeks=weeks)


def iso(dt: datetime) -> str:
    return dt.isoformat()


def create_series(client, room_id, start, end=None, count=None, until=None, name="山田"):
    end = end or (start + timedelta(hours=1))
    body = {
        "room_id": room_id,
        "start_time": iso(start),
        "end_time": iso(end),
        "booker_name": name,
    }
    if count is not None:
        body["count"] = count
    if until is not None:
        body["until"] = until.isoformat()
    return client.post("/reservations/recurring", json=body)


def test_create_series_by_count(client):
    room_id = create_room(client)
    start = next_monday()
    resp = create_series(client, room_id, start, count=4)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "series_id" in body
    assert len(body["occurrences"]) == 4
    # 各回に series_id が付与され active
    for occ in body["occurrences"]:
        assert occ["series_id"] == body["series_id"]
        assert occ["status"] == "active"


def test_create_series_by_until_inclusive(client):
    room_id = create_room(client)
    start = next_monday()
    until = (start + timedelta(weeks=3)).date()  # 起点含め4回
    resp = create_series(client, room_id, start, until=until)
    assert resp.status_code == 201, resp.text
    assert len(resp.json()["occurrences"]) == 4


def test_series_weekly_7_day_step(client):
    room_id = create_room(client)
    start = next_monday()
    occ = create_series(client, room_id, start, count=3).json()["occurrences"]
    starts = sorted(datetime.fromisoformat(o["start_time"]) for o in occ)
    assert (starts[1] - starts[0]) == timedelta(days=7)
    assert (starts[2] - starts[1]) == timedelta(days=7)


def test_conflict_rejects_whole_series_atomically(client):
    room_id = create_room(client)
    start = next_monday()
    # 2週目に単発予約を入れておく
    conflict_start = start + timedelta(weeks=1)
    single = client.post(
        "/reservations",
        json={
            "room_id": room_id,
            "start_time": iso(conflict_start),
            "end_time": iso(conflict_start + timedelta(hours=1)),
            "booker_name": "先客",
        },
    )
    assert single.status_code == 201
    # 4回シリーズ（2週目が重複）-> 全体拒否 409
    resp = create_series(client, room_id, start, count=4)
    assert resp.status_code == 409
    # 原子性: シリーズの回は1件も作られていない（単発の1件のみ）
    listed = client.get("/reservations", params={"room_id": room_id}).json()
    assert len(listed) == 1
    assert listed[0]["series_id"] is None


def test_both_count_and_until_400(client):
    room_id = create_room(client)
    start = next_monday()
    resp = create_series(
        client, room_id, start, count=4, until=(start + timedelta(weeks=3)).date()
    )
    assert resp.status_code == 400


def test_neither_count_nor_until_400(client):
    room_id = create_room(client)
    start = next_monday()
    resp = create_series(client, room_id, start)
    assert resp.status_code == 400


def test_over_max_count_400(client):
    room_id = create_room(client)
    start = next_monday()
    resp = create_series(client, room_id, start, count=53)
    assert resp.status_code == 400


def test_past_start_400(client):
    room_id = create_room(client)
    past = datetime.now().replace(microsecond=0) - timedelta(days=7)
    resp = create_series(client, room_id, past, count=3)
    assert resp.status_code == 400


def test_missing_room_404(client):
    start = next_monday()
    resp = create_series(client, "no-room", start, count=3)
    assert resp.status_code == 404


def test_bad_time_order_400(client):
    room_id = create_room(client)
    start = next_monday()
    resp = create_series(client, room_id, start, end=start - timedelta(hours=1), count=3)
    assert resp.status_code == 400


def test_cancel_series_cancels_future_active_only(client):
    room_id = create_room(client)
    start = next_monday()
    body = create_series(client, room_id, start, count=4).json()
    series_id = body["series_id"]
    resp = client.post(f"/reservations/recurring/{series_id}/cancel")
    assert resp.status_code == 200, resp.text
    # 全回未来なので全て cancelled
    for occ in resp.json()["occurrences"]:
        assert occ["status"] == "cancelled"


def test_cancel_series_idempotent(client):
    room_id = create_room(client)
    start = next_monday()
    series_id = create_series(client, room_id, start, count=3).json()["series_id"]
    first = client.post(f"/reservations/recurring/{series_id}/cancel")
    assert first.status_code == 200
    second = client.post(f"/reservations/recurring/{series_id}/cancel")
    assert second.status_code == 200


def test_cancel_missing_series_404(client):
    assert client.post("/reservations/recurring/nope/cancel").status_code == 404


def test_individual_occurrence_cancel_via_existing_api(client):
    room_id = create_room(client)
    start = next_monday()
    occ = create_series(client, room_id, start, count=3).json()["occurrences"]
    target = occ[1]["id"]
    # 既存の個別キャンセル API を流用（US-R05）
    resp = client.post(f"/reservations/{target}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
    # 他の回は active のまま
    others = [o["id"] for o in occ if o["id"] != target]
    for oid in others:
        assert client.get(f"/reservations/{oid}").json()["status"] == "active"


def test_get_series(client):
    room_id = create_room(client)
    start = next_monday()
    series_id = create_series(client, room_id, start, count=3).json()["series_id"]
    resp = client.get(f"/reservations/recurring/{series_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == series_id
    assert body["occurrence_count"] == 3
    assert len(body["occurrences"]) == 3


def test_get_missing_series_404(client):
    assert client.get("/reservations/recurring/nope").status_code == 404


def test_series_id_shown_in_listing(client):
    room_id = create_room(client)
    start = next_monday()
    series_id = create_series(client, room_id, start, count=2).json()["series_id"]
    listed = client.get("/reservations", params={"room_id": room_id}).json()
    assert all(r["series_id"] == series_id for r in listed)


def test_single_reservation_has_null_series_id(client):
    room_id = create_room(client)
    future = (datetime.now() + timedelta(days=1)).replace(microsecond=0)
    single = client.post(
        "/reservations",
        json={
            "room_id": room_id,
            "start_time": iso(future),
            "end_time": iso(future + timedelta(hours=1)),
            "booker_name": "単発",
        },
    )
    assert single.status_code == 201
    assert single.json()["series_id"] is None
