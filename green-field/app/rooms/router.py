"""会議室 API エンドポイント（/rooms）。US-01, US-02, US-03。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.rooms.schemas import RoomCreate, RoomOut, RoomUpdate
from app.rooms.service import RoomService

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)) -> RoomOut:
    room = RoomService(db).create_room(
        name=payload.name,
        capacity=payload.capacity,
        equipment=payload.equipment,
        location=payload.location,
    )
    return RoomOut.model_validate(room)


@router.get("", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db)) -> list[RoomOut]:
    rooms = RoomService(db).list_rooms()
    return [RoomOut.model_validate(r) for r in rooms]


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: str, db: Session = Depends(get_db)) -> RoomOut:
    room = RoomService(db).get_room(room_id)
    return RoomOut.model_validate(room)


@router.put("/{room_id}", response_model=RoomOut)
def update_room(
    room_id: str, payload: RoomUpdate, db: Session = Depends(get_db)
) -> RoomOut:
    room = RoomService(db).update_room(
        room_id=room_id,
        name=payload.name,
        capacity=payload.capacity,
        equipment=payload.equipment,
        location=payload.location,
    )
    return RoomOut.model_validate(room)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: str, db: Session = Depends(get_db)) -> None:
    RoomService(db).delete_room(room_id)
