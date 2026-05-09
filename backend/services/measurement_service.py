from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from models import Measurement
from schemas.measurement import MeasurementCreate
import repositories.room_repository as room_repo
import repositories.measurement_repository as measurement_repo


def create_measurement(db: Session, data: MeasurementCreate, user_id: int) -> Measurement:
    if not room_repo.get_by_id_and_user(db, data.room_id, user_id):
        raise HTTPException(status_code=404, detail="Cômodo não encontrado")
    return measurement_repo.create(db, user_id=user_id, **data.model_dump())


def list_measurements(db: Session, user_id: int, room_id: Optional[int] = None) -> list[Measurement]:
    return measurement_repo.list_by_user(db, user_id, room_id)
