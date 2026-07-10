"""空き検索の入出力スキーマ。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.rooms.schemas import RoomOut


class AvailableRoomsOut(BaseModel):
    start_time: datetime
    end_time: datetime
    available_rooms: list[RoomOut]
