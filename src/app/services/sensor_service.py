from datetime import datetime, timezone, timedelta
import logging
import os
import requests
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL")
BOX_IDS = os.getenv("BOX_ID").split(",") if os.getenv("BOX_ID") else []

class SensorService:
    """Service to manage sensor data fetching and health status."""
    def __init__(self):
        self.cache: Dict[str, dict] = {}
        self.last_fetch_time: Optional[datetime] = None
        self.box_statuses: Dict[str, bool] = {box_id: True for box_id in BOX_IDS}

    def fetch_all_data(self) -> Tuple[int, int]:
        """Fetch data for all boxes and update cache/statuses."""
        reachable = 0
        for box_id in BOX_IDS:
            try:
                response = requests.get(f"{BASE_URL}/boxes/{box_id}", timeout=10)
                response.raise_for_status()
                self.cache[box_id] = response.json()
                self.box_statuses[box_id] = True
                reachable += 1
            except Exception:
                logger.warning(f"Failed to fetch data for box {box_id}")
                self.box_statuses[box_id] = False

        if reachable > 0:
            self.last_fetch_time = datetime.now(timezone.utc)

        return reachable, len(BOX_IDS)

    def get_data(self) -> Dict[str, dict]:
        """Get latest available data from cache, refreshing if necessary."""
        now = datetime.now(timezone.utc)
        if not self.last_fetch_time or (now - self.last_fetch_time > timedelta(minutes=1)):
            self.fetch_all_data()
        return self.cache

    def is_healthy(self) -> bool:
        """Check if the service is healthy based on complex rules."""
        total_boxes = len(BOX_IDS)
        if total_boxes == 0:
            return True

        unreachable_count = sum(1 for status in self.box_statuses.values() if not status)

        threshold = (total_boxes // 2) + 1
        is_majority_unreachable = unreachable_count >= threshold

        is_cache_stale = True
        if self.last_fetch_time:
            cache_age = datetime.now(timezone.utc) - self.last_fetch_time
            if cache_age <= timedelta(minutes=5):
                is_cache_stale = False

        if is_majority_unreachable and is_cache_stale:
            return False

        return True

sensor_service = SensorService()
