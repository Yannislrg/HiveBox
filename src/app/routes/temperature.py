from datetime import datetime, timedelta, timezone
import logging
import os

import requests
from fastapi import APIRouter, HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)

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
    if last_measurement_time:
        date_now = datetime.now(timezone.utc)
        if date_now - last_measurement_time > timedelta(weeks=100):
            logger.debug(
                "Skipping sensor data because it is too old",
                extra={"sensor": sensor},
            )
            return True
    return False


def set_status(temperature):
    """Set status based on temperature value

    Args:
        temperature (float): temperature value

    Returns:
        str: status
    """
    if temperature < 11:
        status = "Too cold"
        return status
    elif 11 <= temperature <= 36:
        status = "good"
        return status
    else:
        status = "Too hot"
    return status


def fetch_box_data(box_id):
    """Fetch sensor data for a single box."""
    logger.info("Fetching temperature data for box", extra={"box_id": box_id})
    try:
        response = requests.get(f"{BASE_URL}/boxes/{box_id}", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        logger.exception(
            "Failed to fetch temperature data for box",
            extra={"box_id": box_id},
        )
    except ValueError:
        logger.exception(
            "Failed to decode temperature response JSON",
            extra={"box_id": box_id},
        )
    return None


def accumulate_temperature(data, box_id):
    """Collect valid temperature readings from one box."""
    temperature = 0.0
    box_active = 0

    for sensor in data.get("sensors", []):
        if sensor.get("title") != "Temperatur":
            logger.debug(
                "Ignoring non-temperature sensor",
                extra={"box_id": box_id, "sensor": sensor},
            )
            continue
        if too_old_data(sensor):
            logger.debug(
                "Ignoring stale temperature sensor",
                extra={"box_id": box_id, "sensor": sensor},
            )
            continue

        reading = float(sensor["lastMeasurement"]["value"])
        logger.info(
            "Using temperature reading",
            extra={"box_id": box_id, "value": sensor["lastMeasurement"]["value"]},
        )
        temperature += reading
        box_active += 1

    return temperature, box_active


@router.get("/temperature")
def get_avg_temperature():
    """return avg temperature value

    Returns:
        _type_: return avg temperature
    """
    logger.info("Temperature endpoint requested")
    temperature = 0.0
    box_active = 0
    for box_id in BOX_ID:
        data = fetch_box_data(box_id)
        if data is None:
            continue
        box_temperature, active_sensors = accumulate_temperature(data, box_id)
        temperature += box_temperature
        box_active += active_sensors

    if box_active == 0:
        logger.warning("No active boxes with valid temperature data")
        raise HTTPException(
            status_code=503,
            detail="No active boxes with valid temperature data",
        )

    temperature /= box_active
    rounded_temp = round(temperature, 2)
    status = set_status(temperature)
    logger.info(
        "Temperature endpoint completed",
        extra={
            "average_temperature": rounded_temp,
            "status": status,
            "boxes_with_data": box_active,
        },
    )
    return {
        "average_temperature": rounded_temp,
        "status": status,
    }
