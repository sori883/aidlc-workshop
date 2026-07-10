"""会議室のユースケース（CRUD）。business-rules.md の BR-R* に対応。"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.common.exceptions import ConflictError, NotFoundError, ValidationError
from app.db.models import Reservation, ReservationStatus, Room
from app.rooms.repository import RoomRepository


class RoomService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RoomRepository(db)

    @staticmethod
    def _validate(name: str, capacity: int) -> None:
        if name is None or not name.strip():
            raise ValidationError("name は必須です。")  # BR-R1
        if capacity is None or capacity < 0:
            raise ValidationError("capacity は 0 以上の整数である必要があります。")  # BR-R2

    def create_room(
        self, name: str, capacity: int, equipment: list[str], location: str
    ) -> Room:
        self._validate(name, capacity)
        room = Room(
            id=str(uuid.uuid4()),
            name=name,
            capacity=capacity,
            location=location or "",
            created_at=datetime.now(),
        )
        room.equipment = equipment or []
        self.repo.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def get_room(self, room_id: str) -> Room:
        room = self.repo.get(room_id)
        if room is None:
            raise NotFoundError("指定された会議室が存在しません。")
        return room

    def list_rooms(self) -> list[Room]:
        return self.repo.list()

    def update_room(
        self, room_id: str, name: str, capacity: int, equipment: list[str], location: str
    ) -> Room:
        room = self.get_room(room_id)
        self._validate(name, capacity)
        room.name = name
        room.capacity = capacity
        room.equipment = equipment or []
        room.location = location or ""
        self.db.commit()
        self.db.refresh(room)
        return room

    def delete_room(self, room_id: str) -> None:
        room = self.get_room(room_id)
        # BR-R6: active な予約が1件でもあれば削除拒否（409）。
        active = (
            self.db.query(Reservation)
            .filter(
                Reservation.room_id == room_id,
                Reservation.status == ReservationStatus.active.value,
            )
            .count()
        )
        if active > 0:
            raise ConflictError("有効な予約が存在する会議室は削除できません。")
        self.repo.delete(room)
        self.db.commit()
