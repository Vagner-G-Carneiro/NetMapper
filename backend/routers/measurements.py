from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User
from schemas.measurement import MeasurementCreate, MeasurementOut
from services.auth_service import get_current_user
import services.measurement_service as measurement_service

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.post("", response_model=MeasurementOut, status_code=201)
def create_measurement(
    data: MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return measurement_service.create_measurement(db, data, current_user.id)


@router.get("", response_model=List[MeasurementOut])
def list_measurements(
    room_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return measurement_service.list_measurements(db, current_user.id, room_id)
