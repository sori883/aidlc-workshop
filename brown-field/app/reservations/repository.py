"""Reservation の永続化アクセス。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Reservation, ReservationStatus


class ReservationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, reservation: Reservation) -> Reservation:
        self.db.add(reservation)
        self.db.flush()
        return reservation

    def get(self, reservation_id: str) -> Reservation | None:
        return self.db.get(Reservation, reservation_id)

    def list(
        self,
        room_id: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> list[Reservation]:
        query = self.db.query(Reservation)
        if room_id is not None:
            query = query.filter(Reservation.room_id == room_id)
        results = query.all()
        # 期間フィルタは半開区間の重なり判定で行う（BR-L3）。
        if from_time is not None and to_time is not None:
            results = [
                r
                for r in results
                if r.start_time < to_time and from_time < r.end_time
            ]
        return results

    def list_active_by_room(self, room_id: str) -> list[Reservation]:
        return (
            self.db.query(Reservation)
            .filter(
                Reservation.room_id == room_id,
                Reservation.status == ReservationStatus.active.value,
            )
            .all()
        )
