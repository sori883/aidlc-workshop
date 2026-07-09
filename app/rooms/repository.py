"""Room の永続化アクセス。"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Room


class RoomRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, room: Room) -> Room:
        self.db.add(room)
        self.db.flush()
        return room

    def get(self, room_id: str) -> Room | None:
        return self.db.get(Room, room_id)

    def list(self) -> list[Room]:
        return self.db.query(Room).all()

    def delete(self, room: Room) -> None:
        self.db.delete(room)
        self.db.flush()
