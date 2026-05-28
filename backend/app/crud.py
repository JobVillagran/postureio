from sqlalchemy.orm import Session
from app.models import PostureReading
from app.schemas import PostureReadingCreate


def create_reading(db: Session, reading: PostureReadingCreate):
    db_reading = PostureReading(
        device_id=reading.device_id,
        user_id=reading.user_id,
        posture=reading.posture,
        sensors=reading.sensors,
        is_bad_posture=reading.is_bad_posture,
        confidence=reading.confidence
    )

    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    return db_reading


def get_latest_reading(db: Session):
    return (
        db.query(PostureReading)
        .order_by(PostureReading.created_at.desc())
        .first()
    )


def get_reading_history(db: Session, limit: int = 50):
    return (
        db.query(PostureReading)
        .order_by(PostureReading.created_at.desc())
        .limit(limit)
        .all()
    )


def get_all_readings(db: Session, limit: int = 100):
    return (
        db.query(PostureReading)
        .order_by(PostureReading.created_at.desc())
        .limit(limit)
        .all()
    )