"""会議室 API テスト（US-01, US-02, US-03）。"""
from tests.conftest import create_room


def test_create_room(client):
    resp = client.post(
        "/rooms",
        json={"name": "会議室A", "capacity": 6, "equipment": ["projector", "whiteboard"], "location": "3F東"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "会議室A"
    assert body["capacity"] == 6
    assert body["equipment"] == ["projector", "whiteboard"]
    assert body["location"] == "3F東"
    assert "id" in body


def test_create_room_empty_name_400(client):
    resp = client.post("/rooms", json={"name": "  ", "capacity": 4})
    assert resp.status_code == 400


def test_create_room_negative_capacity_422_or_400(client):
    # capacity は Pydantic の ge=0 で弾かれる（422）。
    resp = client.post("/rooms", json={"name": "A", "capacity": -1})
    assert resp.status_code == 422


def test_list_and_get_room(client):
    room_id = create_room(client, name="R1")
    resp = client.get("/rooms")
    assert resp.status_code == 200
    assert any(r["id"] == room_id for r in resp.json())

    resp = client.get(f"/rooms/{room_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == room_id


def test_get_missing_room_404(client):
    resp = client.get("/rooms/does-not-exist")
    assert resp.status_code == 404


def test_update_room(client):
    room_id = create_room(client, name="Old")
    resp = client.put(
        f"/rooms/{room_id}",
        json={"name": "New", "capacity": 10, "equipment": [], "location": "5F"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"
    assert resp.json()["capacity"] == 10


def test_update_missing_room_404(client):
    resp = client.put(
        "/rooms/nope", json={"name": "X", "capacity": 1, "equipment": [], "location": ""}
    )
    assert resp.status_code == 404


def test_delete_room(client):
    room_id = create_room(client)
    resp = client.delete(f"/rooms/{room_id}")
    assert resp.status_code == 204
    assert client.get(f"/rooms/{room_id}").status_code == 404


def test_delete_missing_room_404(client):
    resp = client.delete("/rooms/nope")
    assert resp.status_code == 404
