import os
import redis
import logging
import json
from typing import Optional, Any

logger = logging.getLogger(__name__)


class ValkeyService:
    """Service to handle connection and operations with Valkey (Redis-compatible)."""

    def __init__(self):
        self.host = os.getenv("VALKEY_HOST", "localhost")
        self.port = int(os.getenv("VALKEY_PORT", 6379))
        self.password = os.getenv("VALKEY_PASSWORD", None)
        self.db = int(os.getenv("VALKEY_DB", 0))
        self.ttl = int(os.getenv("VALKEY_TTL", 300))

        self.client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Initialize the Redis client."""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True,
                socket_timeout=5
            )
            self.client.ping()
            logger.info(f"Connected to Valkey at {self.host}:{self.port}")
        except Exception as e:
            logger.error(
                f"Failed to connect to Valkey at {self.host}:{self.port}: {e}"
            )
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from cache."""
        if not self.client:
            return None
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Error getting key {key} from Valkey: {e}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store data in cache with TTL."""
        if not self.client:
            return
        try:
            ttl = ttl or self.ttl
            self.client.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.warning(f"Error setting key {key} in Valkey: {e}")

    def is_available(self) -> bool:
        """Check if Valkey is available."""
        if not self.client:
            return False
        try:
            return self.client.ping()
        except Exception:
            return False


valkey_service = ValkeyService()
