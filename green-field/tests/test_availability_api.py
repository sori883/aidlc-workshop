"""空き会議室検索 API テスト（US-08）。"""
from datetime import datetime, timedelta

from brown.tests.conftest import create_room


def future(hours: int, minutes: int = 0) -> str:
    base = datetime.now() + timedelta(days=1)
    base = base.replace(hour=0, minute=0, second=0, microsecond=0)
    return (base + timedelta(hours=hours, minutes=minutes)).isoformat()


def make_reservation(client, room_id, start, end, name="山田"):
    return client.post(
        "/reservations",
        json={"room_id": room_id, "start_time": start, "end_time": end, "booker_name": name},
    )


def test_find_available_rooms_excludes_booked(client):
    room_a = create_room(client, name="A")
    room_b = create_room(client, name="B")
    # room_a を 10:00-11:00 で予約
    make_reservation(client, room_a, future(10), future(11))

    resp = client.get("/availability", params={"start_time": future(10), "end_time": future(11)})
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.json()["available_rooms"]]
    assert room_a not in ids
    assert room_b in ids


def test_adjacent_room_is_available(client):
    room_a = create_room(client, name="A")
    make_reservation(client, room_a, future(10), future(11))
    # 11:00-12:00 は隣接なので空き扱い
    resp = client.get("/availability", params={"start_time": future(11), "end_time": future(12)})
    ids = [r["id"] for r in resp.json()["available_rooms"]]
    assert room_a in ids


def test_cancelled_reservation_frees_room(client):
    room_a = create_room(client, name="A")
    r = make_reservation(client, room_a, future(10), future(11)).json()
    client.post(f"/reservations/{r['id']}/cancel")
    resp = client.get("/availability", params={"start_time": future(10), "end_time": future(11)})
    ids = [r["id"] for r in resp.json()["available_rooms"]]
    assert room_a in ids


def test_bad_time_order_400(client):
    resp = client.get("/availability", params={"start_time": future(12), "end_time": future(11)})
    assert resp.status_code == 400


def test_no_rooms_returns_empty(client):
    room_a = create_room(client, name="A")
    make_reservation(client, room_a, future(10), future(11))
    resp = client.get("/availability", params={"start_time": future(10), "end_time": future(11)})
    assert resp.status_code == 200
    assert resp.json()["available_rooms"] == []
