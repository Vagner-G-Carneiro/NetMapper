from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Room
import repositories.room_repository as room_repo


def list_rooms(db: Session, user_id: int) -> list[Room]:
    return room_repo.list_by_user(db, user_id)


def create_room(db: Session, name: str, user_id: int) -> Room:
    return room_repo.create(db, name=name, user_id=user_id)


def delete_room(db: Session, room_id: int, user_id: int) -> None:
    room = room_repo.get_by_id_and_user(db, room_id, user_id)
    if not room:
        raise HTTPException(status_code=404, detail="Cômodo não encontrado")
    room_repo.delete(db, room)
