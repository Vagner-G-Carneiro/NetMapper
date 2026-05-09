from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    download_mbps = Column(Float, nullable=False)
    upload_mbps = Column(Float, nullable=False)
    ping_ms = Column(Float, nullable=False)
    jitter_ms = Column(Float, nullable=False)
    measured_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="measurements")
    room = relationship("Room", back_populates="measurements")
