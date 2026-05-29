import os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()

DEVICE_API_KEY = os.getenv("DEVICE_API_KEY")
DASHBOARD_API_KEY = os.getenv("DASHBOARD_API_KEY")


def verify_device_api_key(x_api_key: str | None = Header(default=None)):
    if not DEVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Device API key is not configured"
        )

    if x_api_key != DEVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing device API key"
        )

    return True


def verify_dashboard_api_key(x_api_key: str | None = Header(default=None)):
    if not DASHBOARD_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard API key is not configured"
        )

    if x_api_key != DASHBOARD_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing dashboard API key"
        )

    return True