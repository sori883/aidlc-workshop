"""ORM モデル定義（Room, Reservation, ReservationSeries）。

- ID は UUID 文字列。
- 時刻はナイーブ datetime（ローカル）。
- equipment は list[str] を JSON 文字列として保存する。
- 重複チェック・空き検索を効率化するため reservations(room_id, status) にインデックスを付与。
- 定期予約はシリーズ（ReservationSeries）として管理し、各回は reservations.series_id で紐付く。
"""
from __future__ import annotations

import enum
import json
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ReservationStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"


class RecurrenceEndType(str, enum.Enum):
    count = "count"
    until = "until"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 設備は JSON 文字列で保持（list[str]）。
    equipment_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    location: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )

    @property
    def equipment(self) -> list[str]:
        return json.loads(self.equipment_json)

    @equipment.setter
    def equipment(self, value: list[str]) -> None:
        self.equipment_json = json.dumps(value or [])


class ReservationSeries(Base):
    """定期予約シリーズ（週次）。各回は Reservation として展開され series_id で紐付く。"""

    __tablename__ = "reservation_series"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    room_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rooms.id"), nullable=False
    )
    booker_name: Mapped[str] = mapped_column(String, nullable=False)
    booker_email: Mapped[str | None] = mapped_column(String, nullable=True)
    # 起点（1回目）の日時。時刻部分が各回の開始/終了時刻を規定する。
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # 起点の曜日（Python weekday(): 月=0）。照会時の可読性のため保持。
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    # 終了条件。count 指定なら recurrence_count、until 指定なら recurrence_until を持つ。
    recurrence_end_type: Mapped[str] = mapped_column(String(16), nullable=False)
    recurrence_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recurrence_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    # 実際に生成された回数。
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    room: Mapped["Room"] = relationship()
    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="series"
    )


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    room_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rooms.id"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    booker_name: Mapped[str] = mapped_column(String, nullable=False)
    booker_email: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=ReservationStatus.active.value
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # 定期予約シリーズの各回に付与される。単発予約は NULL。
    series_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("reservation_series.id"), nullable=True
    )

    room: Mapped["Room"] = relationship(back_populates="reservations")
    series: Mapped["ReservationSeries | None"] = relationship(
        back_populates="reservations"
    )


# 重複チェック（対象会議室の active 予約走査）・空き検索を効率化。
Index("ix_reservations_room_id_status", Reservation.room_id, Reservation.status)
