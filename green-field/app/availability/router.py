"""空き会議室検索 API（/availability）。US-08。"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.availability.schemas import AvailableRoomsOut
from app.availability.service import AvailabilityService
from app.common.exceptions import ValidationError
from app.db.database import get_db
from app.rooms.schemas import RoomOut

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("", response_model=AvailableRoomsOut)
def find_available_rooms(
    start_time: datetime = Query(..., description="開始時刻（ISO 8601）"),
    end_time: datetime = Query(..., description="終了時刻（ISO 8601）"),
    db: Session = Depends(get_db),
) -> AvailableRoomsOut:
    # BR-A1: 時刻の順序。
    if start_time >= end_time:
        raise ValidationError("start_time は end_time より前である必要があります。")
    rooms = AvailabilityService(db).find_available_rooms(start_time, end_time)
    return AvailableRoomsOut(
        start_time=start_time,
        end_time=end_time,
        available_rooms=[RoomOut.model_validate(r) for r in rooms],
    )
