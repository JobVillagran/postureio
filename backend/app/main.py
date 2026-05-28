from app.security import verify_api_key
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import Base, engine, get_db
from app.schemas import PostureReadingCreate, PostureReadingResponse
from app import crud
from app.reports import generate_summary
from app.advice import generate_advice

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Posture Monitoring Backend",
    description="Cloud API for posture sensor readings from Arduino or ESP32",
    version="1.1.0"
)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "Posture Monitoring Backend",
        "version": "1.1.0"
    }


@app.get("/api/device/health")
def device_health_check():
    return {
        "status": "ready",
        "message": "Device can send readings to /api/readings"
    }


@app.get("/api/device/contract")
def get_device_contract():
    return {
        "method": "POST",
        "endpoint": "/api/readings",
        "content_type": "application/json",
        "valid_postures": [
            "correct",
            "leaning_left",
            "leaning_right",
            "leaning_forward",
            "leaning_back",
            "slouched",
            "not_sitting"
        ],
        "required_body": {
            "device_id": "chair-001",
            "user_id": "user-001",
            "posture": "leaning_left",
            "sensors": {
                "seat_left": 78,
                "seat_right": 42,
                "back_left": 65,
                "back_right": 55,
                "front_pressure": 70
            },
            "is_bad_posture": True,
            "confidence": 0.91
        }
    }


@app.post("/api/readings", response_model=PostureReadingResponse)
def create_reading(
    reading: PostureReadingCreate,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    return crud.create_reading(db, reading)


@app.get("/api/readings/latest", response_model=PostureReadingResponse | None)
def get_latest_reading(
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    return crud.get_latest_reading(db)


@app.get("/api/readings/history", response_model=List[PostureReadingResponse])
def get_reading_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    return crud.get_reading_history(db, limit)


@app.get("/api/reports/summary")
def get_summary(
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    readings = crud.get_all_readings(db, limit=100)
    return generate_summary(readings)


@app.get("/api/advice")
def get_advice(
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    readings = crud.get_all_readings(db, limit=100)
    return generate_advice(readings)

@app.get("/api/alerts/latest")
def get_latest_alert(
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    readings = crud.get_all_readings(db, limit=100)
    advice = generate_advice(readings)

    return {
        "risk_level": advice["risk_level"],
        "recommended_action": advice["recommended_action"],
        "message": advice["advice"]
    }