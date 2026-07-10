"""空き状況・重複判定ロジック（中核）。

business-rules.md の BR-OV / BR-A に対応。半開区間 [start, end) で判定する。
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Reservation, ReservationStatus, Room


def overlaps(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    """2つの半開区間 [start_a, end_a) と [start_b, end_b) が重なるなら True。

    隣接（end_a == start_b など）は重ならない扱い（半開区間）。
    """
    return start_a < end_b and start_b < end_a


class AvailabilityService:
    """重複チェックと空き会議室検索を提供する。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def has_conflict(
        self,
        room_id: str,
        start: datetime,
        end: datetime,
        exclude_reservation_id: str | None = None,
    ) -> bool:
        """指定会議室・時間帯に active な予約の重複があれば True。"""
        query = self.db.query(Reservation).filter(
            Reservation.room_id == room_id,
            Reservation.status == ReservationStatus.active.value,
        )
        if exclude_reservation_id is not None:
            query = query.filter(Reservation.id != exclude_reservation_id)

        for res in query.all():
            if overlaps(res.start_time, res.end_time, start, end):
                return True
        return False

    def find_available_rooms(self, start: datetime, end: datetime) -> list[Room]:
        """指定 [start, end) に active 予約が重ならない会議室の一覧を返す。"""
        rooms = self.db.query(Room).all()
        available: list[Room] = []
        for room in rooms:
            if not self.has_conflict(room.id, start, end):
                available.append(room)
        return available
