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
    description="Backend API for posture sensor readings",
    version="1.0.0"
)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "Posture Monitoring Backend"
    }


@app.post("/api/readings", response_model=PostureReadingResponse)
def create_reading(
    reading: PostureReadingCreate,
    db: Session = Depends(get_db)
):
    return crud.create_reading(db, reading)


@app.get("/api/readings/latest", response_model=PostureReadingResponse | None)
def get_latest_reading(db: Session = Depends(get_db)):
    return crud.get_latest_reading(db)


@app.get("/api/readings/history", response_model=List[PostureReadingResponse])
def get_reading_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return crud.get_reading_history(db, limit)


@app.get("/api/reports/summary")
def get_summary(db: Session = Depends(get_db)):
    readings = crud.get_all_readings(db, limit=100)
    return generate_summary(readings)


@app.get("/api/advice")
def get_advice(db: Session = Depends(get_db)):
    readings = crud.get_all_readings(db, limit=100)
    return generate_advice(readings)