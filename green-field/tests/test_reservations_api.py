"""予約 API テスト（US-04, US-05, US-06, US-07）。重複防止が中心。"""
from datetime import datetime, timedelta

from brown.tests.conftest import create_room


def future(hours: int, minutes: int = 0) -> str:
    """現在より十分未来の時刻を ISO 文字列で返す（過去日時拒否を回避）。"""
    base = datetime.now() + timedelta(days=1)
    base = base.replace(hour=0, minute=0, second=0, microsecond=0)
    return (base + timedelta(hours=hours, minutes=minutes)).isoformat()


def make_reservation(client, room_id, start, end, name="山田"):
    return client.post(
        "/reservations",
        json={
            "room_id": room_id,
            "start_time": start,
            "end_time": end,
            "booker_name": name,
        },
    )


def test_create_reservation(client):
    room_id = create_room(client)
    resp = make_reservation(client, room_id, future(10), future(11))
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "active"
    assert body["room_id"] == room_id


def test_create_reservation_missing_room_404(client):
    resp = make_reservation(client, "no-room", future(10), future(11))
    assert resp.status_code == 404


def test_create_reservation_bad_time_order_400(client):
    room_id = create_room(client)
    resp = make_reservation(client, room_id, future(11), future(10))
    assert resp.status_code == 400


def test_create_reservation_empty_booker_400(client):
    room_id = create_room(client)
    resp = make_reservation(client, room_id, future(10), future(11), name="  ")
    assert resp.status_code == 400


def test_past_time_reservation_400(client):
    room_id = create_room(client)
    past = (datetime.now() - timedelta(days=1)).isoformat()
    past_end = (datetime.now() - timedelta(days=1) + timedelta(hours=1)).isoformat()
    resp = make_reservation(client, room_id, past, past_end)
    assert resp.status_code == 400


def test_overlapping_reservation_conflict_409(client):
    room_id = create_room(client)
    assert make_reservation(client, room_id, future(10), future(11)).status_code == 201
    # 内包する時間帯 -> 409
    resp = make_reservation(client, room_id, future(10, 30), future(10, 45))
    assert resp.status_code == 409


def test_adjacent_reservation_ok(client):
    room_id = create_room(client)
    assert make_reservation(client, room_id, future(10), future(11)).status_code == 201
    # 隣接（11:00開始）は許可
    resp = make_reservation(client, room_id, future(11), future(12))
    assert resp.status_code == 201


def test_same_time_different_room_ok(client):
    room_a = create_room(client, name="A")
    room_b = create_room(client, name="B")
    assert make_reservation(client, room_a, future(10), future(11)).status_code == 201
    # 別室なら同一時間帯でもOK
    resp = make_reservation(client, room_b, future(10), future(11))
    assert resp.status_code == 201


def test_cancelled_slot_can_be_rebooked(client):
    room_id = create_room(client)
    r1 = make_reservation(client, room_id, future(10), future(11)).json()
    # キャンセル
    assert client.post(f"/reservations/{r1['id']}/cancel").status_code == 200
    # 同じ時間帯を再予約できる
    resp = make_reservation(client, room_id, future(10), future(11))
    assert resp.status_code == 201


def test_list_and_get_reservation(client):
    room_id = create_room(client)
    r = make_reservation(client, room_id, future(10), future(11)).json()
    assert client.get(f"/reservations/{r['id']}").status_code == 200
    listed = client.get("/reservations", params={"room_id": room_id})
    assert listed.status_code == 200
    assert any(x["id"] == r["id"] for x in listed.json())


def test_get_missing_reservation_404(client):
    assert client.get("/reservations/nope").status_code == 404


def test_cancel_is_idempotent(client):
    room_id = create_room(client)
    r = make_reservation(client, room_id, future(10), future(11)).json()
    first = client.post(f"/reservations/{r['id']}/cancel")
    assert first.status_code == 200
    assert first.json()["status"] == "cancelled"
    # 再キャンセルも 200 で cancelled のまま（冪等）
    second = client.post(f"/reservations/{r['id']}/cancel")
    assert second.status_code == 200
    assert second.json()["status"] == "cancelled"


def test_cancel_missing_reservation_404(client):
    assert client.post("/reservations/nope/cancel").status_code == 404
