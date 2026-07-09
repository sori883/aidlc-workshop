"""ORM モデル定義（Room, Reservation）。

- ID は UUID 文字列。
- 時刻はナイーブ datetime（ローカル）。
- equipment は list[str] を JSON 文字列として保存する。
- 重複チェック・空き検索を効率化するため reservations(room_id, status) にインデックスを付与。
"""
from __future__ import annotations

import enum
import json
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ReservationStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"


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

    room: Mapped["Room"] = relationship(back_populates="reservations")


# 重複チェック（対象会議室の active 予約走査）・空き検索を効率化。
Index("ix_reservations_room_id_status", Reservation.room_id, Reservation.status)
