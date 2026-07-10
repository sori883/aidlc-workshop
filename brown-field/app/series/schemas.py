"""定期予約（シリーズ）の入出力スキーマ（Pydantic v2）。"""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.reservations.schemas import ReservationOut


class RecurringReservationCreate(BaseModel):
    room_id: str = Field(..., description="予約対象の会議室ID")
    start_time: datetime = Field(..., description="起点（1回目）の開始時刻（ISO 8601）")
    end_time: datetime = Field(..., description="起点（1回目）の終了時刻（ISO 8601）")
    booker_name: str = Field(..., description="予約者名（必須）")
    booker_email: str | None = Field(None, description="予約者メール（任意）")
    # 終了条件は count または until のどちらか一方を指定する（両方/両方未指定は 400）。
    count: int | None = Field(
        None, ge=1, description="繰り返し回数（count または until の一方）"
    )
    until: date | None = Field(
        None, description="繰り返し終了日（この日以前の開始回まで、inclusive）"
    )


class SeriesOut(BaseModel):
    """シリーズのメタ情報 + 全回。GET / キャンセルのレスポンス。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    room_id: str
    booker_name: str
    booker_email: str | None
    weekday: int
    recurrence_end_type: str
    recurrence_count: int | None
    recurrence_until: date | None
    occurrence_count: int
    created_at: datetime
    occurrences: list[ReservationOut] = Field(default_factory=list)


class RecurringReservationOut(BaseModel):
    """シリーズ作成のレスポンス（series_id + 生成された全回）。"""

    series_id: str
    occurrences: list[ReservationOut]
