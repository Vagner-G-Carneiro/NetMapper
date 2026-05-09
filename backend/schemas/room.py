from pydantic import BaseModel
from datetime import datetime


class RoomCreate(BaseModel):
    name: str


class RoomOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
