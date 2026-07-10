"""定期予約 API エンドポイント（/reservations/recurring）。US-R01, R04, R06, R07。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.reservations.schemas import ReservationOut
from app.series.schemas import (
    RecurringReservationCreate,
    RecurringReservationOut,
    SeriesOut,
)
from app.series.service import RecurringReservationService

router = APIRouter(prefix="/reservations/recurring", tags=["recurring-reservations"])


def _series_out(service: RecurringReservationService, series) -> SeriesOut:
    occurrences = service.list_occurrences(series.id)
    out = SeriesOut.model_validate(series)
    out.occurrences = [ReservationOut.model_validate(r) for r in occurrences]
    return out


@router.post("", response_model=RecurringReservationOut, status_code=status.HTTP_201_CREATED)
def create_recurring_reservation(
    payload: RecurringReservationCreate, db: Session = Depends(get_db)
) -> RecurringReservationOut:
    service = RecurringReservationService(db)
    series = service.create_series(
        room_id=payload.room_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        booker_name=payload.booker_name,
        booker_email=payload.booker_email,
        count=payload.count,
        until=payload.until,
    )
    occurrences = service.list_occurrences(series.id)
    return RecurringReservationOut(
        series_id=series.id,
        occurrences=[ReservationOut.model_validate(r) for r in occurrences],
    )


@router.post("/{series_id}/cancel", response_model=SeriesOut)
def cancel_recurring_series(
    series_id: str, db: Session = Depends(get_db)
) -> SeriesOut:
    service = RecurringReservationService(db)
    series = service.cancel_series(series_id)
    return _series_out(service, series)


@router.get("/{series_id}", response_model=SeriesOut)
def get_recurring_series(
    series_id: str, db: Session = Depends(get_db)
) -> SeriesOut:
    service = RecurringReservationService(db)
    series = service.get_series(series_id)
    return _series_out(service, series)
