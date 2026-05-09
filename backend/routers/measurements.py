from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User, Room, Measurement
from schemas.measurement import MeasurementCreate, MeasurementOut
from services.auth_service import get_current_user

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.post("", response_model=MeasurementOut, status_code=201)
def create_measurement(
    data: MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == data.room_id, Room.user_id == current_user.id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Cômodo não encontrado")
    m = Measurement(**data.model_dump(), user_id=current_user.id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.get("", response_model=List[MeasurementOut])
def list_measurements(
    room_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Measurement).filter(Measurement.user_id == current_user.id)
    if room_id:
        q = q.filter(Measurement.room_id == room_id)
    return q.order_by(Measurement.measured_at.desc()).all()
