from pydantic import BaseModel
from datetime import datetime


class MeasurementCreate(BaseModel):
    room_id: int
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    jitter_ms: float


class MeasurementOut(BaseModel):
    id: int
    room_id: int
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    jitter_ms: float
    measured_at: datetime

    model_config = {"from_attributes": True}
