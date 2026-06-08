"""Temperature route returning average reading across all senseBoxes."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from src.app.services.sensor_service import sensor_service
from src.app.routes.metrics import (
    CURRENT_TEMPERATURE,
    TEMP_STATUS,
    TEMPERATURE_HISTOGRAM,
    TEMP_READINGS_COUNT,
    TEMP_ENDPOINT_REQUESTS,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def too_old_data(sensor):
    """Check if the sensor data is older than 1 hour."""
    last_measurement_time = datetime.strptime(
        sensor["lastMeasurement"]["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    last_measurement_time = last_measurement_time.replace(tzinfo=timezone.utc)
    if last_measurement_time:
        date_now = datetime.now(timezone.utc)
        if date_now - last_measurement_time > timedelta(weeks=100):
            return True
    return False


def set_status(temperature):
    """Set status based on temperature value."""
    if temperature < 10:
        return "Too Cold"
    if 10 <= temperature <= 37:
        return "Good"
    return "Too Hot"


STATUS_MAP = {"Too Cold": 0.0, "Good": 1.0, "Too Hot": 2.0}


def accumulate_temperature(data, box_id):
    """Collect valid temperature readings from one box."""
    temperature = 0.0
    box_active = 0

    for sensor in data.get("sensors", []):
        if sensor.get("title") != "Temperatur":
            continue
        if too_old_data(sensor):
            continue

        reading = float(sensor["lastMeasurement"]["value"])
        temperature += reading
        box_active += 1

        CURRENT_TEMPERATURE.labels(box_id=box_id).set(reading)
        status_str = set_status(reading)
        TEMP_STATUS.labels(box_id=box_id).set(STATUS_MAP.get(status_str, 1.0))
        TEMPERATURE_HISTOGRAM.labels(box_id=box_id).observe(reading)
        TEMP_READINGS_COUNT.labels(box_id=box_id).inc()

    return temperature, box_active


@router.get("/temperature")
def get_avg_temperature():
    """Return average temperature value across all active senseBoxes."""
    logger.info("Temperature endpoint requested")
    TEMP_ENDPOINT_REQUESTS.inc()

    data_map = sensor_service.get_data()

    total_temperature = 0.0
    total_active_sensors = 0

    for box_id, data in data_map.items():
        box_temperature, active_sensors = accumulate_temperature(data, box_id)
        total_temperature += box_temperature
        total_active_sensors += active_sensors

    if total_active_sensors == 0:
        logger.warning("No active boxes with valid temperature data")
        raise HTTPException(
            status_code=503,
            detail="No active boxes with valid temperature data",
        )

    avg_temperature = total_temperature / total_active_sensors
    rounded_temp = round(avg_temperature, 2)
    status = set_status(avg_temperature)

    return {
        "average_temperature": rounded_temp,
        "status": status,
    }
