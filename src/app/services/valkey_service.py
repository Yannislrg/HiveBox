"""Valkey (Redis-compatible) cache service."""

import json
import logging
import os
from typing import Any, Optional

import redis

logger = logging.getLogger(__name__)


class ValkeyService:
    """Connection and operations with Valkey (Redis-compatible)."""

    def __init__(self):
        self.host = os.getenv("VALKEY_HOST", "localhost")
        self.port = int(os.getenv("VALKEY_PORT", "6379"))
        self.password = os.getenv("VALKEY_PASSWORD")
        self.db = int(os.getenv("VALKEY_DB", "0"))
        self.ttl = int(os.getenv("VALKEY_TTL", "300"))

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
                socket_timeout=5,
            )
            self.client.ping()
            logger.info("Connected to Valkey at %s:%s", self.host, self.port)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception(
                "Failed to connect to Valkey at %s:%s", self.host, self.port
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
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Error getting key %s from Valkey: %s", key, e)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store data in cache with TTL."""
        if not self.client:
            return
        try:
            ttl = ttl or self.ttl
            self.client.set(key, json.dumps(value), ex=ttl)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Error setting key %s in Valkey: %s", key, e)

    def is_available(self) -> bool:
        """Check if Valkey is available."""
        if not self.client:
            return False
        try:
            return self.client.ping()
        except Exception:  # pylint: disable=broad-exception-caught
            return False


valkey_service = ValkeyService()
