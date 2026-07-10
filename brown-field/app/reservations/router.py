"""予約 API エンドポイント（/reservations）。US-04, US-05, US-06, US-07。"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.reservations.schemas import ReservationCreate, ReservationOut
from app.reservations.service import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: ReservationCreate, db: Session = Depends(get_db)
) -> ReservationOut:
    reservation = ReservationService(db).create_reservation(
        room_id=payload.room_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        booker_name=payload.booker_name,
        booker_email=payload.booker_email,
    )
    return ReservationOut.model_validate(reservation)


@router.get("", response_model=list[ReservationOut])
def list_reservations(
    room_id: str | None = Query(None, description="会議室IDで絞り込み"),
    from_time: datetime | None = Query(None, description="期間の開始（ISO 8601）"),
    to_time: datetime | None = Query(None, description="期間の終了（ISO 8601）"),
    db: Session = Depends(get_db),
) -> list[ReservationOut]:
    reservations = ReservationService(db).list_reservations(
        room_id=room_id, from_time=from_time, to_time=to_time
    )
    return [ReservationOut.model_validate(r) for r in reservations]


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(
    reservation_id: str, db: Session = Depends(get_db)
) -> ReservationOut:
    reservation = ReservationService(db).get_reservation(reservation_id)
    return ReservationOut.model_validate(reservation)


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(
    reservation_id: str, db: Session = Depends(get_db)
) -> ReservationOut:
    reservation = ReservationService(db).cancel_reservation(reservation_id)
    return ReservationOut.model_validate(reservation)
