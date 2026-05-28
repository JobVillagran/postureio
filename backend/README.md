# Posture Monitoring Backend

Backend API for a posture monitoring IoT project using Arduino sensors.

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy

## Main Features

1. Register posture sensor readings
2. Get latest posture reading
3. Get posture history
4. Generate posture summary report
5. Generate automatic posture advice

## Project Structure

```text
posture-backend/
├── app/
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── reports.py
│   ├── advice.py
│   └── main.py
├── simulator/
│   └── send_fake_readings.py
├── requirements.txt
└── README.md