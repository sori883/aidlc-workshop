"""定期予約（シリーズ）のユースケース。business-rules.md の BR-RS-* に対応。"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.availability.service import AvailabilityService
from app.common.exceptions import ConflictError, NotFoundError, ValidationError
from app.db.models import (
    RecurrenceEndType,
    Reservation,
    ReservationSeries,
    ReservationStatus,
)
from app.reservations.repository import ReservationRepository
from app.rooms.repository import RoomRepository
from app.series.recurrence import generate_occurrences
from app.series.repository import SeriesRepository

MAX_OCCURRENCES = 52


class RecurringReservationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.series_repo = SeriesRepository(db)
        self.res_repo = ReservationRepository(db)
        self.room_repo = RoomRepository(db)
        self.availability = AvailabilityService(db)

    def create_series(
        self,
        room_id: str,
        start_time: datetime,
        end_time: datetime,
        booker_name: str,
        booker_email: str | None,
        count: int | None,
        until: date | None,
    ) -> ReservationSeries:
        # BR-RS-C1: 時刻の順序。
        if start_time >= end_time:
            raise ValidationError("start_time は end_time より前である必要があります。")
        # BR-RS-C2: 予約者名は必須。
        if booker_name is None or not booker_name.strip():
            raise ValidationError("booker_name は必須です。")
        # BR-RS-C4: 終了条件は count または until のどちらか一方。
        if (count is None) == (until is None):
            raise ValidationError(
                "count または until のどちらか一方を指定してください。"
            )

        # BR-RS-G*: 週次の各回を生成。
        try:
            occurrences = generate_occurrences(
                start_time, end_time, count, until, max_count=MAX_OCCURRENCES
            )
        except ValueError as exc:
            raise ValidationError(str(exc))

        # BR-RS-C6: 有効な回が無い（until が起点より前など）。
        if not occurrences:
            raise ValidationError("指定条件では作成できる回がありません。")
        # BR-RS-C7: 回数上限。
        if len(occurrences) > MAX_OCCURRENCES:
            raise ValidationError(
                f"繰り返し回数が上限（{MAX_OCCURRENCES}回）を超えています。"
            )
        # BR-RS-C8: 最初の回の開始が過去なら拒否（start == now は許可）。
        if occurrences[0][0] < datetime.now():
            raise ValidationError("過去の開始時刻では予約できません。")
        # BR-RS-C3: 会議室の存在確認。
        if self.room_repo.get(room_id) is None:
            raise NotFoundError("指定された会議室が存在しません。")

        # BR-RS-OV1/OV2: 1回でも重複すればシリーズ全体を拒否（原子性）。
        for occ_start, occ_end in occurrences:
            if self.availability.has_conflict(room_id, occ_start, occ_end):
                raise ConflictError("指定の時間帯は既に予約されています。")

        # BR-RS-OV4: series と全回を単一トランザクションで登録。
        now = datetime.now()
        end_type = (
            RecurrenceEndType.count.value
            if count is not None
            else RecurrenceEndType.until.value
        )
        series = ReservationSeries(
            id=str(uuid.uuid4()),
            room_id=room_id,
            booker_name=booker_name,
            booker_email=booker_email,
            start_time=start_time,
            end_time=end_time,
            weekday=start_time.weekday(),
            recurrence_end_type=end_type,
            recurrence_count=count,
            recurrence_until=until,
            occurrence_count=len(occurrences),
            created_at=now,
        )
        self.series_repo.add(series)

        for occ_start, occ_end in occurrences:
            reservation = Reservation(
                id=str(uuid.uuid4()),
                room_id=room_id,
                start_time=occ_start,
                end_time=occ_end,
                booker_name=booker_name,
                booker_email=booker_email,
                status=ReservationStatus.active.value,
                created_at=now,
                series_id=series.id,
            )
            self.res_repo.add(reservation)

        self.db.commit()
        self.db.refresh(series)
        return series

    def get_series(self, series_id: str) -> ReservationSeries:
        series = self.series_repo.get(series_id)
        if series is None:
            raise NotFoundError("指定されたシリーズが存在しません。")
        return series

    def cancel_series(self, series_id: str) -> ReservationSeries:
        # BR-RS-X4: 存在確認。
        series = self.get_series(series_id)
        # BR-RS-X1/X2/X3: 未来の active 回のみ cancelled（冪等）。
        now = datetime.now()
        future_active = self.res_repo.list_future_active_by_series(series_id, now)
        if future_active:
            for reservation in future_active:
                reservation.status = ReservationStatus.cancelled.value
            self.db.commit()
            self.db.refresh(series)
        return series

    def list_occurrences(self, series_id: str) -> list[Reservation]:
        """シリーズの全回を開始時刻順で返す（照会・レスポンス整形用）。"""
        return self.res_repo.list_by_series(series_id)
