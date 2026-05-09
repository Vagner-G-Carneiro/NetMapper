from sqlalchemy.orm import Session
from models import Room


def list_by_user(db: Session, user_id: int) -> list[Room]:
    return db.query(Room).filter(Room.user_id == user_id).all()


def get_by_id_and_user(db: Session, room_id: int, user_id: int) -> Room | None:
    return db.query(Room).filter(Room.id == room_id, Room.user_id == user_id).first()


def create(db: Session, name: str, user_id: int) -> Room:
    room = Room(name=name, user_id=user_id)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def delete(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()
