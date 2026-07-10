"""会議室の入出力スキーマ（Pydantic v2）。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    name: str = Field(..., description="会議室名（必須）")
    capacity: int = Field(0, ge=0, description="収容人数（0以上）")
    equipment: list[str] = Field(default_factory=list, description="設備の一覧")
    location: str = Field("", description="場所")


class RoomUpdate(BaseModel):
    name: str = Field(..., description="会議室名（必須）")
    capacity: int = Field(0, ge=0, description="収容人数（0以上）")
    equipment: list[str] = Field(default_factory=list, description="設備の一覧")
    location: str = Field("", description="場所")


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    capacity: int
    equipment: list[str]
    location: str
    created_at: datetime
