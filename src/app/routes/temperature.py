from datetime import datetime, timedelta, timezone
from fastapi import APIRouter
import os
import requests

router = APIRouter()

BASE_URL = os.getenv("BASE_URL")
BOX_ID = os.getenv("BOX_ID").split(",")

def too_old_data(sensor):
    """Check if the sensor data is older than 1 hour

    Args:
        sensor (_type_): sensor data
    Returns:
        bool: True if data is older than 1 hour, False otherwise
    """

    last_measurement_time = datetime.strptime(
        sensor["lastMeasurement"]["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    # createdAt ends with 'Z' (UTC) so make the datetime timezone-aware
    last_measurement_time = last_measurement_time.replace(tzinfo=timezone.utc)
    print("last measurement time:", last_measurement_time)
    if last_measurement_time:
        date_now = datetime.now(timezone.utc)
        if date_now - last_measurement_time > timedelta(weeks=100):
            print("data too old")
            return True
    print("data is recent")
    return False


def set_status(temperature):
    """Set status based on temperature value

    Args:
        temperature (float): temperature value

    Returns:
        str: status
    """
    if temperature < 10:
        status = "Too cold"
        return status
    elif 11 <= temperature <= 36:
        status = "good"
        return status
    else:
        status = "Too hot"
    print("status:", status)
    return status


@router.get("/temperature")
def get_avg_temperature():
    """return avg temperature value

    Returns:
        _type_: return avg temperature
    """
    temperature = 0.0
    box_active = 0
    for box_id in BOX_ID:
        response = requests.get(f"{BASE_URL}/boxes/{box_id}", timeout=30)
        data = response.json()
        for sensor in data.get("sensors", []):
            if sensor.get("title") != "Temperatur":
                continue
            if too_old_data(sensor):
                continue
            print("sensor data:", sensor)
            temperature += float(sensor["lastMeasurement"]["value"])
            box_active += 1
    print("box_active:", box_active)
    if box_active == 0:
        return {"error": "No active boxes with valid temperature data"}
    temperature /= box_active
    rounded_temp = round(temperature, 2)
    status = set_status(temperature)
    return {
        "average_temperature": rounded_temp,
        "status": status,
    }
