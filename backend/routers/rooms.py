from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Room
from schemas.room import RoomCreate, RoomOut
from services.auth_service import get_current_user

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=List[RoomOut])
def list_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Room).filter(Room.user_id == current_user.id).all()


@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = Room(name=data.name, user_id=current_user.id)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(Room).filter(Room.id == room_id, Room.user_id == current_user.id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Cômodo não encontrado")
    db.delete(room)
    db.commit()
