from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas.room import RoomCreate, RoomOut
from services.auth_service import get_current_user
import services.room_service as room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=List[RoomOut])
def list_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return room_service.list_rooms(db, current_user.id)


@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return room_service.create_room(db, data.name, current_user.id)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room_service.delete_room(db, room_id, current_user.id)
