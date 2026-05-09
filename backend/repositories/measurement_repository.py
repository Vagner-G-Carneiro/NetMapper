from sqlalchemy.orm import Session
from typing import Optional
from models import Measurement


def create(
    db: Session,
    user_id: int,
    room_id: int,
    download_mbps: float,
    upload_mbps: float,
    ping_ms: float,
    jitter_ms: float,
) -> Measurement:
    m = Measurement(
        user_id=user_id,
        room_id=room_id,
        download_mbps=download_mbps,
        upload_mbps=upload_mbps,
        ping_ms=ping_ms,
        jitter_ms=jitter_ms,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def list_by_user(db: Session, user_id: int, room_id: Optional[int] = None) -> list[Measurement]:
    q = db.query(Measurement).filter(Measurement.user_id == user_id)
    if room_id:
        q = q.filter(Measurement.room_id == room_id)
    return q.order_by(Measurement.measured_at.desc()).all()
