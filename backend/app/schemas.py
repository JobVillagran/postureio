from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime


class PostureReadingCreate(BaseModel):
    device_id: str = Field(..., example="chair-001")
    user_id: str = Field(..., example="user-001")
    posture: str = Field(..., example="leaning_left")
    sensors: Dict[str, int]
    is_bad_posture: bool
    confidence: float = Field(..., ge=0, le=1)


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