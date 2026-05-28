from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Dict
from datetime import datetime


class PostureType(str, Enum):
    correct = "correct"
    leaning_left = "leaning_left"
    leaning_right = "leaning_right"
    leaning_forward = "leaning_forward"
    leaning_back = "leaning_back"
    slouched = "slouched"
    not_sitting = "not_sitting"


class SensorData(BaseModel):
    seat_left: int = Field(..., ge=0, le=1023)
    seat_right: int = Field(..., ge=0, le=1023)
    back_left: int = Field(..., ge=0, le=1023)
    back_right: int = Field(..., ge=0, le=1023)
    front_pressure: int = Field(..., ge=0, le=1023)


class PostureReadingCreate(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=50)
    user_id: str = Field(..., min_length=3, max_length=50)
    posture: PostureType
    sensors: SensorData
    is_bad_posture: bool
    confidence: float = Field(..., ge=0, le=1)

    @model_validator(mode="after")
    def validate_posture_state(self):
        if self.posture == PostureType.correct and self.is_bad_posture:
            raise ValueError("correct posture cannot be marked as bad posture")

        if self.posture != PostureType.correct and not self.is_bad_posture:
            raise ValueError("incorrect posture must be marked as bad posture")

        return self


class PostureReadingResponse(BaseModel):
    id: int
    device_id: str
    user_id: str
    posture: str
    sensors: Dict[str, int]
    is_bad_posture: bool
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True