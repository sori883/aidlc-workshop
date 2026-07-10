"""予約の入出力スキーマ（Pydantic v2）。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReservationCreate(BaseModel):
    room_id: str = Field(..., description="予約対象の会議室ID")
    start_time: datetime = Field(..., description="開始時刻（ISO 8601）")
    end_time: datetime = Field(..., description="終了時刻（ISO 8601）")
    booker_name: str = Field(..., description="予約者名（必須）")
    booker_email: str | None = Field(None, description="予約者メール（任意）")


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    room_id: str
    start_time: datetime
    end_time: datetime
    booker_name: str
    booker_email: str | None
    status: str
    created_at: datetime
    # 定期予約シリーズの各回はシリーズID、単発予約は None。
    series_id: str | None = None
