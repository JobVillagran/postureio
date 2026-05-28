import random
import time
from datetime import datetime
import requests

API_URL = "http://localhost:8000/api/readings"

POSTURES = [
    "correct",
    "leaning_left",
    "leaning_right",
    "leaning_forward",
    "leaning_back",
    "slouched",
    "not_sitting"
]


def build_fake_reading():
    posture = random.choice(POSTURES)

    return {
        "device_id": "chair-001",
        "user_id": "user-001",
        "posture": posture,
        "sensors": {
            "seat_left": random.randint(20, 100),
            "seat_right": random.randint(20, 100),
            "back_left": random.randint(20, 100),
            "back_right": random.randint(20, 100),
            "front_pressure": random.randint(20, 100)
        },
        "is_bad_posture": posture != "correct",
        "confidence": round(random.uniform(0.75, 0.99), 2)
    }


while True:
    payload = build_fake_reading()

    response = requests.post(API_URL, json=payload)

    print(datetime.now(), response.status_code, payload)

    time.sleep(5)