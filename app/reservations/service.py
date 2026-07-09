"""予約のユースケース。business-rules.md の BR-C* / BR-X* / BR-L* に対応。"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.availability.service import AvailabilityService
from app.common.exceptions import ConflictError, NotFoundError, ValidationError
from app.db.models import Reservation, ReservationStatus
from app.reservations.repository import ReservationRepository
from app.rooms.repository import RoomRepository


class ReservationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ReservationRepository(db)
        self.room_repo = RoomRepository(db)
        self.availability = AvailabilityService(db)

    def create_reservation(
        self,
        room_id: str,
        start_time: datetime,
        end_time: datetime,
        booker_name: str,
        booker_email: str | None = None,
    ) -> Reservation:
        # BR-C1: 時刻の順序。
        if start_time >= end_time:
            raise ValidationError("start_time は end_time より前である必要があります。")
        # BR-C2: 予約者名は必須。
        if booker_name is None or not booker_name.strip():
            raise ValidationError("booker_name は必須です。")
        # BR-C3: 会議室の存在確認。
        if self.room_repo.get(room_id) is None:
            raise NotFoundError("指定された会議室が存在しません。")
        # BR-C4: 過去日時の予約は拒否（start == now は許可）。
        if start_time < datetime.now():
            raise ValidationError("過去の開始時刻では予約できません。")
        # BR-C5: 重複チェック→挿入を単一トランザクション内で実施。
        if self.availability.has_conflict(room_id, start_time, end_time):
            raise ConflictError("指定の時間帯は既に予約されています。")

        reservation = Reservation(
            id=str(uuid.uuid4()),
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
            booker_name=booker_name,
            booker_email=booker_email,
            status=ReservationStatus.active.value,
            created_at=datetime.now(),
        )
        self.repo.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def get_reservation(self, reservation_id: str) -> Reservation:
        reservation = self.repo.get(reservation_id)
        if reservation is None:
            raise NotFoundError("指定された予約が存在しません。")
        return reservation

    def list_reservations(
        self,
        room_id: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> list[Reservation]:
        return self.repo.list(room_id=room_id, from_time=from_time, to_time=to_time)

    def cancel_reservation(self, reservation_id: str) -> Reservation:
        reservation = self.get_reservation(reservation_id)
        # BR-X3: 既に cancelled なら冪等に成功（状態を変えない）。
        if reservation.status == ReservationStatus.active.value:
            reservation.status = ReservationStatus.cancelled.value
            self.db.commit()
            self.db.refresh(reservation)
        return reservation
