from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, JSON
from datetime import datetime
from app.database import Base


class PostureReading(Base):
    __tablename__ = "posture_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    posture = Column(String, nullable=False)
    sensors = Column(JSON, nullable=False)
    is_bad_posture = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)